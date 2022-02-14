import functools
import json
from decimal import Decimal
from pprint import pprint
from time import time, sleep
from typing import Union, Tuple, Callable

from eth_typing import ChecksumAddress
from web3 import Web3
from eth_abi.packed import encode_abi_packed
from web3.contract import ContractFunction, Contract
from web3.exceptions import ContractLogicError
from web3.types import Wei, TxParams, _Hash32


PROVIDER = 'https://ropsten.infura.io/v3/d6dc1928fa734842bb81ce889a2f7e8b'

NETWORKS_IDS = {
    1: "mainnet",
    3: "ropsten",
    4: "rinkeby",
    10: "optimism",
    42: "kovan",
    56: "binance",
    97: "binance_testnet",
    137: "polygon",
    100: "xdai",
    250: "fantom",
    42161: "arbitrum",
    421611: "arbitrum_testnet",
}


class InsufficientBalance(Exception):
    """Raised when the account has insufficient balance for a transaction."""

    def __init__(self, had: int, needed: int) -> None:
        Exception.__init__(self, f"Insufficient balance. Had {had}, needed {needed}")


class BaseTrader:
    def __init__(self, address: str, private_key: str):
        self.address = address
        self.__private_key = private_key
        self.max_approval_int = int(f"0x{64 * 'f'}", 16)
        self.max_approval_check_int = int(f"0x{15 * '0'}{49 * 'f'}", 16)
        _, self.erc20_abi = self.load_contract('./abis/erc20.json')

    _w3 = Web3(Web3.HTTPProvider(PROVIDER, request_kwargs={"timeout": 60}))

    @property
    def w3(self):
        return self._w3

    @w3.setter
    def w3(self, w3: Web3) -> None:
        self._w3 = w3

    @property
    def network_id(self):
        return int(self.w3.net.version)

    def load_contract(self, path: str) -> tuple:
        with open(path) as file:
            data = json.load(file)[0]
        abi = data['abi']
        if data.get('networks'):
            contract = data['networks'][NETWORKS_IDS[self.network_id]]
        else:
            contract = data.get('contract')
        if contract is None:
            return None, abi
        return contract, abi

    CONVERT_MAP = {'1': 'wei', '3': 'kwei', '6': 'mwei', '9': 'gwei', '12': 'szabo', '15': 'finney',
                   '18': 'ether', '21': 'kether', '24': 'mether', '27': 'gether', '30': 'tether'}

    def quantity(self, count: Union[float, int, Decimal], decimal: int) -> int:
        return self.w3.toWei(count, self.CONVERT_MAP[str(decimal)])

    def convert_wei_by_decimal(self, count: Union[Wei, int], decimal: int):
        return self.w3.fromWei(count, self.CONVERT_MAP[str(decimal)])

    weth_address = None
    _eth_address = '0x0000000000000000000000000000000000000000'

    @property
    def eth_address(self):
        return self.w3.toChecksumAddress(self._eth_address)

    @eth_address.setter
    def eth_address(self, address: ChecksumAddress) -> None:
        self.eth_address = address

    def is_eth_address(self, tk: ChecksumAddress) -> bool:
        if tk == self.eth_address:
            return True
        return False

    def is_weth_address(self, tk: ChecksumAddress) -> bool:
        if tk == self.weth_address:
            return True
        return False

    def get_balance(self, tk: ChecksumAddress = None) -> Wei:
        if tk is None or self.is_eth_address(tk):
            return self.w3.eth.get_balance(self.address)
        erc20_contract = self.w3.eth.contract(tk, abi=self.erc20_abi)
        return erc20_contract.functions.balanceOf(self.address).call()

    def build_tx_and_send(self, function: ContractFunction):
        params: TxParams = {"from": self.address, "value": Wei(0),
                            "nonce": self.w3.eth.get_transaction_count(self.address)}
        tx = function.buildTransaction(params)
        tx['gas'] = Wei(int(self.w3.eth.estimate_gas(tx) * 1.2))
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.__private_key)
        return self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    @property
    def deadline(self) -> int:
        return int(time()) + 10 * 60

    def err_insufficient_balance(self, qty: Union[Wei, int]):
        eth_balance = self.get_balance()
        if qty > eth_balance:
            raise InsufficientBalance(eth_balance, qty)

    def check_contract_success(self, tx_hash: Union[_Hash32, str]):
        pprint(f'Awaiting {tx_hash}...')
        tx_data = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_data.status == 1:
            return True
        return False

    def __is_approved(self, erc20_contract: Contract, router_address: str) -> bool:
        check_amount = (erc20_contract.functions.allowance(self.address, router_address).call()
                        >= self.max_approval_check_int)
        if check_amount:
            return True
        return False

    def approve(self, token: ChecksumAddress, router_address: str) -> None:
        erc20_contract = self.w3.eth.contract(token, abi=self.erc20_abi)
        if self.__is_approved(erc20_contract, router_address):
            tx = self.build_tx_and_send(
                erc20_contract.functions.approve(router_address, self.max_approval_int))
            self.check_contract_success(tx)
            sleep(1)


class TraderV2(BaseTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.factory_address, self.factory_abi = self.load_contract('abis/abis_v2/factory.json')
        self.router_address, self.router_abi = self.load_contract('abis/abis_v2/router.json')

        self.factory_contract = self.w3.eth.contract(self.factory_address, abi=self.factory_abi)
        self.router_contract = self.w3.eth.contract(self.router_address, abi=self.router_abi)

    @property
    def weth_address(self):
        return self.w3.toChecksumAddress(self.router_contract.functions.WETH().call())

    def get_route(self, tk1: ChecksumAddress, tk2: ChecksumAddress) -> Tuple[list, int]:
        if self.is_weth_address(tk1):
            return [self.weth_address, tk2], 1
        elif self.is_weth_address(tk2):
            return [tk1, self.weth_address], 2
        else:
            return [tk1, self.weth_address, tk2], 3

    def extract_output_prices(self, tk1: ChecksumAddress, tk2: ChecksumAddress, qty: Union[Wei, int]) -> list:
        return self.router_contract.functions.getAmountsOut(
            qty, self.get_route(tk1, tk2)[0]).call()

    def extract_input_prices(self, tk1: ChecksumAddress, tk2: ChecksumAddress, qty: Union[Wei, int]) -> list:
        return self.router_contract.functions.getAmountsIn(
            qty, self.get_route(tk1, tk2)[0]).call()

    def trade_output(self, tk1: ChecksumAddress, tk2: ChecksumAddress, qty: Union[Wei, int], min_amount_out: int):
        route, func_num = self.get_route(tk1, tk2)
        with_qty = True
        if func_num == 1:
            with_qty = False
            func = self.router_contract.functions.swapExactETHForTokens
        elif func_num == 2:
            func = self.router_contract.functions.swapExactTokensForETH
        else:
            func = self.router_contract.functions.swapExactTokensForTokens
        args = (qty, min_amount_out, route, self.address, self.deadline
                ) if with_qty else (min_amount_out, route, self.address, self.deadline)
        return self.build_tx_and_send(func(*args))

    def trade_input(self, tk1: ChecksumAddress, tk2: ChecksumAddress, qty: Union[Wei, int], max_amount_in: int):
        route, func_num = self.get_route(tk1, tk2)
        with_max_amount_in = True
        if func_num == 1:
            with_max_amount_in = False
            func = self.router_contract.functions.swapETHForExactTokens
        elif func_num == 2:
            func = self.router_contract.functions.swapTokensForExactETH
        else:
            func = self.router_contract.functions.swapTokensForExactTokens
        args = (qty, max_amount_in, route, self.address, self.deadline
                ) if with_max_amount_in else (qty, route, self.address, self.deadline)
        return self.build_tx_and_send(func(*args))


class TraderV3(BaseTrader):
    route_types = ['address', 'uint24', 'address', 'uint24', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.factory_address, self.factory_abi = self.load_contract('abis/abis_v3/factory.json')
        self.router_address, self.router_abi = self.load_contract('abis/abis_v3/router.json')
        self.quoter_address, self.quoter_abi = self.load_contract('abis/abis_v3/quoter.json')

        self.factory_contract = self.w3.eth.contract(self.factory_address, abi=self.factory_abi)
        self.router_contract = self.w3.eth.contract(self.router_address, abi=self.router_abi)
        self.quoter_contract = self.w3.eth.contract(self.quoter_address, abi=self.quoter_abi)

    @property
    def weth_address(self):
        return self.w3.toChecksumAddress(self.router_contract.functions.WETH9().call())

    def _encode_bytes(self, tk1: ChecksumAddress, tk2: ChecksumAddress, fee: int):
        return encode_abi_packed(self.route_types, (tk1, fee, self.weth_address, fee, tk2))

    def extract_input_price(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                            qty: Union[Wei, int], fee: int):
        return self.quoter_contract.functions.quoteExactInput(
            self._encode_bytes(tk1, tk2, fee), qty).call()

    def extract_output_price(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                             qty: Union[Wei, int], fee: int):
        return self.quoter_contract.functions.quoteExactOutput(
            self._encode_bytes(tk2, tk1, fee), qty).call()

    def is_weth_address(self, tk: ChecksumAddress) -> bool:
        if tk == self.weth_address:
            return True
        return False

    def extract_input_single_price(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                                   qty: Union[Wei, int], fee: int):
        return self.quoter_contract.functions.quoteExactInputSingle(tk1, tk2, fee, qty, 0).call()

    def extract_output_single_price(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                                    qty: Union[Wei, int], fee: int):
        return self.quoter_contract.functions.quoteExactOutputSingle(tk1, tk2, fee, qty, 0).call()

    def trade_input(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                    qty: Union[Wei, int], fee: int, min_amount_out: Union[Wei, int]):
        if self.is_weth_address(tk1) or self.is_weth_address(tk2):
            func = self.router_contract.functions.exactInputSingle(
                {"tokenIn": tk1, "tokenOut": tk2, "fee": fee, "recipient": self.address,
                 "deadline": self.deadline, "amountIn": qty, "amountOutMinimum": min_amount_out,
                 "sqrtPriceLimitX96": 0}
            )
        else:
            func = self.router_contract.functions.exactInput(
                {"path": self._encode_bytes(tk1, tk2, fee), "recipient": self.address,
                 "deadline": self.deadline, "amountIn": qty, "amountOutMinimum": min_amount_out}
            )
        return self.build_tx_and_send(func)

    def trade_exact_output(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                           qty: Union[Wei, int], fee: int, max_amount_in: Union[Wei, int]):
        if self.is_weth_address(tk1) or self.is_weth_address(tk2):
            func = self.router_contract.functions.exactOutputSingle(
                {"tokenIn": tk1, "tokenOut": tk2, "fee": fee, "recipient": self.address,
                 "deadline": self.deadline, "amountOut": qty, "amountInMaximum": max_amount_in,
                 "sqrtPriceLimitX96": 0}
            )
        else:
            func = self.router_contract.functions.exactOutput(
                {"path": self._encode_bytes(tk1, tk2, fee), "recipient": self.address,
                 "deadline": self.deadline, "amountOut": qty, "amountInMaximum": max_amount_in}
            )
        return self.build_tx_and_send(func)

    def input_price(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                    qty: Union[Wei, int], fee: int):
        if self.is_weth_address(tk1) or self.is_weth_address(tk2):
            return self.extract_input_single_price(tk1, tk2, qty, fee)
        else:
            return self.extract_input_price(tk1, tk2, qty, fee)

    def output_price(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                     qty: Union[Wei, int], fee: int):
        if self.is_weth_address(tk1) or self.is_weth_address(tk2):
            return self.extract_output_single_price(tk1, tk2, qty, fee)
        else:
            return self.extract_output_price(tk1, tk2, qty, fee)


def find_fee(func: Callable):
    # methods with param fee: int = None
    @functools.wraps(func)
    def send_fee(self, *args, **kwargs):
        if kwargs.get('fee') or kwargs.get('is_v2'):
            return func(self, *args, **kwargs)
        for fee in (3000, 500, 10000):
            try:
                return func(self, *args, **kwargs, fee=fee)
            except ContractLogicError as e:
                if fee == 10000:
                    raise ContractLogicError(e)
                continue
    return send_fee


class UnitedTrader:
    address = '0x9bc74DD43970b43ea94760A24043bBe2089A670B'
    _private_key = '28a5525ad829a69dcda8cb068f659117d5305e0437e2a794339d914bf4141363'

    def __init__(self, tk1: str, tk2: str,
                 tk1_qty: float, tk1_decimal: int,
                 tk2_qty: float, tk2_decimal: int, slippage: float = 0.5):
        self.trader_v2 = TraderV2(self.address, self._private_key)
        self.trader_v3 = TraderV3(self.address, self._private_key)
        self.tk1 = self.trader_v2.w3.toChecksumAddress(tk1)
        self.tk2 = self.trader_v2.w3.toChecksumAddress(tk2)
        self.tk1_qty = self.trader_v2.quantity(tk1_qty, tk1_decimal)
        self.tk2_qty = self.trader_v2.quantity(tk2_qty, tk2_decimal)
        self.slippage = slippage

    @find_fee
    def price_input(self, fee: int = None, is_v2: bool = False) -> tuple:
        tk1, tk2, qty = (self.tk1, self.tk2, self.tk2_qty)
        if is_v2:
            return self.trader_v2.extract_input_prices(tk1, tk2, qty), None
        return self.trader_v3.input_price(tk1, tk2, qty, fee), fee

    @find_fee
    def price_output(self, fee: int = None, is_v2: bool = False) -> tuple:
        tk1, tk2, qty = (self.tk1, self.tk2, self.tk1_qty)
        if is_v2:
            return self.trader_v2.extract_output_prices(tk1, tk2, qty), None
        return self.trader_v3.output_price(tk1, tk2, qty, fee), fee

    def approve(self, token: ChecksumAddress, is_v2: bool) -> None:
        if not self.trader_v3.is_weth_address(token):
            func = self.trader_v3 if not is_v2 else self.trader_v2
            router_address = self.trader_v3.router_address if not is_v2 else self.trader_v2.router_address
            func.approve(token, router_address)

    def trade_input(self, is_v2: bool = False) -> Union[str, None]:
        self.approve(self.tk1, is_v2)
        price_, fee = self.price_input(is_v2=is_v2)
        if not is_v2 and fee:
            min_amount = int((1 - self.slippage) * price_)
            tx_hash = self.trader_v3.trade_extract_input(self.tk1, self.tk2, self.tk2_qty, fee, min_amount)
        else:  # v2
            min_amount = int((1 - self.slippage) * price_[0])
            tx_hash = self.trader_v2.trade_input(self.tk1, self.tk2, self.tk2_qty, min_amount)
        if self.trader_v3.check_contract_success(tx_hash.hex()):
            return tx_hash.hex()

    def trade_output(self, is_v2: bool = True):
        self.approve(self.tk1, is_v2)
        price_, fee = self.price_output(is_v2=is_v2)
        if not is_v2 and fee:
            min_amount = int((1 - self.slippage) * price_)
            tx_hash = self.trader_v3.trade_extract_input(self.tk1, self.tk2, self.tk2_qty, fee, min_amount)
        else:  # v2
            min_amount = int((1 - self.slippage) * price_[0])
            tx_hash = self.trader_v2.trade_input(self.tk1, self.tk2, self.tk2_qty, min_amount)
        if self.trader_v3.check_contract_success(tx_hash.hex()):
            return tx_hash.hex()


TESTKING = '0x588a4fAf0B068446caA3F54AbcC19F41426b1d1F'
UNI = '0xC8F88977E21630Cf93c02D02d9E8812ff0DFC37a'
UNI_v3 = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'
WETH = '0xc778417E063141139Fce010982780140Aa0cD5Ab'
USDT = '0x03f7cef050aac29954a97334c00920aa8919dc37'

trader = UnitedTrader(tk1=WETH, tk2=UNI,
                      tk1_decimal=18, tk2_decimal=18,
                      tk1_qty=0.1, tk2_qty=0.026716954748894888)

# pi3, feei3 = trader.price_input()
# print('V3 input: ', pi3, 'price: ', trader.trader_v2.convert_wei_by_decimal(pi3, 18), 'fee: ', feei3)
# pi2, _ = trader.price_input(is_v2=True)
# print('V2 input: ', pi2, 'price: ', trader.trader_v2.convert_wei_by_decimal(pi2[0], 18))

# po3, feeo3 = trader.price_output()
# print('V3 output: ', po3, 'price: ', trader.trader_v2.convert_wei_by_decimal(po3, 18), 'fee:', feeo3)
# po2, _ = trader.price_output(is_v2=True)
# print('V2 output: ', po2, 'price: ', trader.trader_v2.convert_wei_by_decimal(po2[-1], 18))


# e = trader.trader_v3.extract_output_single_price(trader.tk1, trader.tk2, trader.tk2_qty, 3000)
# print(e)

p = trader.trader_v2.extract_output_prices(trader.tk1, trader.tk2, 50000000000000000)
print(p)
e = trader.trader_v3.extract_input_single_price(trader.tk1, trader.tk2, 50000000000000000, 3000)
print(e)
print(p[-1] + e)
