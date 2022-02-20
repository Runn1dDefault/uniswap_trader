from base.mixins import BaseTraderMixin
from uni_v3.router import RouterV3
from uni_v3.quoter import QuoterV3

from .utils import find_fee

"""
ex: 
    tk1, tk1_decimals, tk1_amount = WETH, 18, 0.1
    tk2, tk2_decimals, tk2_amount = USDT, 6, 0.01
    trader = Trader(wallet_addr, private_key)
    trader.init(tk1, tk2, tk2_amount, tk2_decimals)
    price_in, fee_in = trader.price_input()
    # for output
    # 0.01: tk1_amount, 6: tk1_decimals
    trader.init(tk1, tk2, tk1_amount, tk2_decimals)
    price_out, fee_out = trader.price_output()
"""


class TraderV3(RouterV3, BaseTraderMixin):
    def __init__(self, address: str, private_key: str):
        super().__init__()
        self.address = address
        self._private_key = private_key
        self.quoter = QuoterV3()

    @find_fee
    def price_output(self, fee: int = None) -> tuple:
        if self.quoter.is_weth_address(self.tk1) or self.quoter.is_weth_address(self.tk2):
            quote = self.quoter.quote_exact_input_single(self.tk1, self.tk2, fee, self.amount)
        else:
            quote = self.quoter.quote_exact_input(self.tk1, self.tk2, fee, self.amount)
        return quote, fee

    @find_fee
    def price_input(self, fee: int = None) -> tuple:
        if self.quoter.is_weth_address(self.tk1) or self.quoter.is_weth_address(self.tk2):
            return self.quoter.quote_exact_output_single(
                self.tk1, self.tk2, fee, self.amount), fee
        return self.quoter.quote_exact_output(self.tk1, self.tk2, fee, self.amount), fee

    def trade_input(self, slippage: float) -> str:
        if not self.is_eth_address(self.tk1):
            self.approve(self.tk1, self.contract_address)
        price, fee = self.price_input()
        min_amount_out = int((1 - slippage) * price)
        if self.is_weth_address(self.tk1) or self.is_weth_address(self.tk2):
            func = self.exact_input_single(self.tk1, self.tk2, self.amount, fee, min_amount_out, self.address)
        else:
            func = self.exact_input(self.tk1, self.tk2, self.amount, fee, min_amount_out, self.address)
        tx = self.build_tx_and_send(func)
        self.check_contract_success(tx)
        return tx.hex()

    def trade_output(self, slippage: float) -> str:
        if not self.is_eth_address(self.tk1):
            self.approve(self.tk1, self.contract_address)
        price, fee = self.price_output()
        max_amount_in = int((1 + slippage) * price)
        if self.is_weth_address(self.tk1) or self.is_weth_address(self.tk2):
            func = self.exact_output_single(self.tk1, self.tk2, self.amount, fee, max_amount_in, self.address)
        else:
            func = self.exact_output(self.tk1, self.tk2, self.amount, fee, max_amount_in, self.address)
        tx = self.build_tx_and_send(func)
        self.check_contract_success(tx)
        return tx.hex()
