import json
import os
from decimal import Decimal
from pprint import pprint
from time import time, sleep
from typing import Union

from eth_typing import ChecksumAddress, Address
from web3 import Web3
from eth_abi.packed import encode_abi_packed
from web3.contract import ContractFunction, Contract
from web3.types import Wei, TxParams, _Hash32

from config import BASE_ABIS, PROVIDER
from constants import ROUTE_TYPES, NETWORKS_IDS


class InsufficientBalance(Exception):
    """Raised when the account has insufficient balance for a transaction."""

    def __init__(self, had: int, needed: int) -> None:
        Exception.__init__(self, f"Insufficient balance. Had {had}, needed {needed}")


class BaseContractManager:
    def __init__(self, address: str, private_key: str):
        self.address = address
        self.__private_key = private_key
        self.max_approval_int = int(f"0x{64 * 'f'}", 16)
        self.max_approval_check_int = int(f"0x{15 * '0'}{49 * 'f'}", 16)
        _, self.erc20_abi = self.load_contract(os.path.join(BASE_ABIS, 'erc20.json'))

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

    def encode_bytes(self, tk1: ChecksumAddress, tk2: ChecksumAddress, fee: int):
        return encode_abi_packed(ROUTE_TYPES, (tk1, fee, self.weth_address, fee, tk2))


class BaseTrader(BaseContractManager):
    tk1: Union[Address, ChecksumAddress, str]
    tk2: Union[Address, ChecksumAddress, str]
    tk_decimals: int
    tk_amount: Union[float, int, Decimal]

    def raise_if_equal_tks(self) -> None:
        if self.tk1 == self.tk2:
            raise ValueError('token1 can not be equal to token2!')

    def init(self, tk1: Union[Address, ChecksumAddress, str],
             tk2: Union[Address, ChecksumAddress, str],
             tk_decimals: int = None, amount: Union[float, int, Decimal] = None):
        self.tk1 = self.w3.toChecksumAddress(tk1)
        self.tk2 = self.w3.toChecksumAddress(tk2)
        self.raise_if_equal_tks()
        if amount and tk_decimals:
            self.tk_decimals = tk_decimals
            self.tk_amount = self.quantity(amount, self.tk_decimals)

