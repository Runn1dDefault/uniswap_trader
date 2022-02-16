from uni_v3.factory import FactoryV3
from uni_v3.router import RouterV3
from uni_v3.quoter import QuoterV3
from utils import find_fee


class TraderV3:
    factory_class = FactoryV3
    router_class = RouterV3
    quoter_class = QuoterV3

    def __init__(self, address: str, private_key: str):
        self.factory = self.factory_class(address=address, private_key=private_key)
        self.router = self.router_class(address=address, private_key=private_key)
        self.quoter = self.quoter_class(address=address, private_key=private_key)

    @find_fee
    def price_input(self, tk1: str, tk2: str, tk1_decimals: int, tk1_amount: float, fee: int = None) -> tuple:
        self.quoter.init(tk1, tk2, tk1_decimals, tk1_amount)
        if self.quoter.is_weth_address(self.quoter.tk1) or self.quoter.is_weth_address(self.quoter.tk2):
            return self.quoter.quote_exact_input_single(
                self.quoter.tk1, self.quoter.tk2, fee, self.quoter.tk_amount), fee
        return self.quoter.quote_exact_input(self.quoter.tk1, self.quoter.tk2, fee,
                                             self.quoter.tk_amount), fee

    @find_fee
    def price_output(self, tk1: str, tk2: str, tk2_decimals: int, tk2_amount: float, fee: int = None) -> tuple:
        self.quoter.init(tk1, tk2, tk2_decimals, tk2_amount)
        if self.quoter.is_weth_address(self.quoter.tk1) or self.quoter.is_weth_address(self.quoter.tk2):
            return self.quoter.quote_exact_output_single(
                self.quoter.tk1, self.quoter.tk2, fee, self.quoter.tk_amount), fee
        return self.quoter.quote_exact_output(self.quoter.tk1, self.quoter.tk2, fee,
                                              self.quoter.tk_amount), fee

    @find_fee
    def trade_input(self, tk1: str, tk2: str, qty: int, price: int, slippage: float, fee: int = None) -> str:
        self.router.init(tk1, tk2)
        if not self.router.is_eth_address(self.router.tk1):
            self.router.approve(self.router.tk1, self.router.contract_address)
        min_amount_out = int((1 - slippage) * price)
        if self.router.is_weth_address(self.router.tk1) or self.router.is_weth_address(self.router.tk2):
            func = self.router.exact_input_single(self.router.tk1, self.router.tk2,
                                                  qty, fee, min_amount_out)
        else:
            func = self.router.exact_input(self.router.tk1, self.router.tk2,
                                           qty, fee, min_amount_out)
        tx = self.router.build_tx_and_send(func)
        self.router.check_contract_success(tx)
        return tx.hex()

    @find_fee
    def trade_output(self, tk1: str, tk2: str, qty: int, price: int, slippage: float, fee: int = None) -> str:
        self.router.init(tk1, tk2)
        if not self.router.is_eth_address(self.router.tk1):
            self.router.approve(self.router.tk1, self.router.contract_address)
        max_amount_in = int((1 + slippage) * price)
        if self.router.is_weth_address(self.router.tk1) or self.router.is_weth_address(self.router.tk2):
            func = self.router.exact_output_single(self.router.tk1, self.router.tk2,
                                                   qty, fee, max_amount_in)
        else:
            func = self.router.exact_output(self.router.tk1, self.router.tk2,
                                            qty, fee, max_amount_in)
        tx = self.router.build_tx_and_send(func)
        self.router.check_contract_success(tx)
        return tx.hex()
