from base.decorators import catch_raise
from base.exeptions import NotFoundPool
from base.mixins import BaseTraderMixin
from uni_v3.router import RouterV3
from uni_v3.quoter import QuoterV3
from uni_v3.factory import FactoryV3
from .constants import FEE_AMOUNT


class TraderV3(RouterV3, BaseTraderMixin):
    def __init__(self, address: str = None, private_key: str = None, provider_http: str = None):
        super().__init__(provider_http=provider_http)
        self.address = address
        self._private_key = private_key
        self.quoter = QuoterV3(provider_http=provider_http)
        self.factory_c = FactoryV3(provider_http=provider_http)
        self.is_input: bool = False

    def check_pool(self) -> int:
        for fee in FEE_AMOUNT.values():
            if not self.is_eth_address(self.get_pool(fee=fee)):
                return fee
        raise NotFoundPool('Not found pool in V3')

    def get_pool(self, fee: int):
        return self.factory_c.get_pool(self.tk1, self.tk2, fee)

    def price_input(self) -> float:
        if self.quoter.is_weth_address(self.tk1) or self.quoter.is_weth_address(self.tk2):
            quote = self.quoter.quote_exact_input_single(self.tk1, self.tk2, self.fee, self.amount)
        else:
            quote = self.quoter.quote_exact_input(self.tk1, self.tk2, self.fee, self.amount)
        return quote

    def price_output(self) -> float:
        if self.quoter.is_weth_address(self.tk1) or self.quoter.is_weth_address(self.tk2):
            return self.quoter.quote_exact_output_single(
                self.tk1, self.tk2, self.fee, self.amount)
        return self.quoter.quote_exact_output(self.tk1, self.tk2, self.fee, self.amount)

    @catch_raise
    def trade_input(self, slippage: float) -> str:
        assert self.address is not None and self._private_key is not None
        fee = self.check_pool()
        if not self.is_eth_address(self.tk1):
            self.approve(self.tk1, self.contract_address)
        price = self.price_input()
        min_amount_out = int((1 - slippage) * price)
        if self.is_weth_address(self.tk1) or self.is_weth_address(self.tk2):
            func = self.exact_input_single(self.tk1, self.tk2, self.amount, fee, min_amount_out, self.address)
        else:
            func = self.exact_input(self.tk1, self.tk2, self.amount, fee, min_amount_out, self.address)
        tx = self.build_tx_and_send(func)
        return tx.hex()

    @catch_raise
    def trade_output(self, slippage: float) -> str:
        assert self.address is not None and self._private_key is not None
        if not self.is_eth_address(self.tk1):
            self.approve(self.tk1, self.contract_address)
        price = self.price_output()
        max_amount_in = int((1 + slippage) * price)
        if self.is_weth_address(self.tk1) or self.is_weth_address(self.tk2):
            func = self.exact_output_single(self.tk1, self.tk2, self.amount, self.fee, max_amount_in, self.address)
        else:
            func = self.exact_output(self.tk1, self.tk2, self.amount, self.fee, max_amount_in, self.address)
        tx = self.build_tx_and_send(func)
        return tx.hex()
