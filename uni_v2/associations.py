from base.mixins import BaseTraderMixin
from uni_v2.router import RouterV2


class TraderV2(RouterV2, BaseTraderMixin):
    def __init__(self, address: str = None, private_key: str = None):
        super().__init__()
        self.address = address
        self._private_key = private_key

    def price_input(self):
        return self.get_amounts_in(self.tk1, self.tk2, self.amount)[0]

    def price_output(self):
        return self.get_amounts_out(self.tk1, self.tk2, self.amount)[-1]

    def trade_input(self, slippage: float) -> str:
        assert self.address is not None and self._private_key is not None

        if not self.is_eth_address(self.tk1):
            self.approve(self.tk1, self.contract_address)
        min_amount_out = int((1 - slippage) * self.price_input())
        if self.is_eth_address(self.tk1):
            func = self.swap_exact_eth_for_tk(self.tk1, self.tk2, min_amount_out, self.address)
        elif self.is_eth_address(self.tk2):
            func = self.swap_exact_tk_for_eth(self.tk1, self.tk2, self.amount, min_amount_out, self.address)
        else:
            func = self.swap_exact_tk_for_tk(self.tk1, self.tk2, self.amount, min_amount_out, self.address)
        tx = self.build_tx_and_send(func)
        self.check_contract_success(tx)
        return tx.hex()

    def trade_output(self, slippage: float) -> str:
        assert self.address is not None and self._private_key is not None

        if not self.is_eth_address(self.tk1):
            self.approve(self.tk1, self.contract_address)
        max_amount_in = int((1 + slippage) * self.price_output())
        if self.is_eth_address(self.tk1):
            func = self.swap_eth_for_exact_tk(self.tk1, self.tk2, self.amount, self.address)
        elif self.is_eth_address(self.tk2):
            func = self.swap_tk_for_exact_eth(self.tk1, self.tk2, self.amount, max_amount_in, self.address)
        else:
            func = self.swap_tk_for_exact_tk(self.tk1, self.tk2, self.amount, max_amount_in, self.address)
        tx = self.build_tx_and_send(func)
        self.check_contract_success(tx)
        return tx.hex()
