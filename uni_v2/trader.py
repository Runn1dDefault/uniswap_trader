from uni_v2.factory import FactoryV2
from uni_v2.router import RouterV2


class TraderV2:
    factory_class = FactoryV2
    router_class = RouterV2

    def __init__(self, address: str, private_key: str):
        self.factory = self.factory_class(address=address, private_key=private_key)
        self.router = self.router_class(address=address, private_key=private_key)

    def prices_input(self, tk1: str, tk2: str, tk1_decimals: int, amount_in: float) -> list:
        self.router.init(tk1, tk2, tk1_decimals, amount_in)
        return self.router.get_amounts_in(self.router.tk1, self.router.tk2, self.router.tk_amount)

    def prices_output(self, tk1: str, tk2: str, tk2_decimals: int, amount_out: float) -> list:
        self.router.init(tk1, tk2, tk2_decimals, amount_out)
        return self.router.get_amounts_out(self.router.tk1, self.router.tk2, self.router.tk_amount)

    def trade_input(self, tk1, tk2, qty: int, slippage: float, price: int) -> str:
        self.router.init(tk1, tk2)
        if not self.router.is_eth_address(self.router.tk1):
            self.router.approve(self.router.tk1, self.router.contract_address)
        min_amount_out = int((1 - slippage) * price)
        if self.router.is_eth_address(self.router.tk1):
            func = self.router.swap_exact_eth_for_tk(self.router.tk1, self.router.tk2, min_amount_out)
        elif self.router.is_eth_address(self.router.tk2):
            func = self.router.swap_exact_tk_for_eth(self.router.tk1, self.router.tk2, qty, min_amount_out)
        else:
            func = self.router.swap_exact_tk_for_tk(self.router.tk1, self.router.tk2, qty, min_amount_out)
        tx = self.router.build_tx_and_send(func)
        self.router.check_contract_success(tx)
        return tx.hex()

    def trade_output(self, tk1, tk2, qty: int, price: int, slippage: float) -> str:
        self.router.init(tk1, tk2)
        if not self.router.is_eth_address(self.router.tk1):
            self.router.approve(self.router.tk1, self.router.contract_address)
        max_amount_in = int((1 + slippage) * price)
        if self.router.is_eth_address(self.router.tk1):
            func = self.router.swap_eth_for_exact_tk(self.router.tk1, self.router.tk2, qty)
        elif self.router.is_eth_address(self.router.tk2):
            func = self.router.swap_tk_for_exact_eth(self.router.tk1, self.router.tk2, qty, max_amount_in)
        else:
            func = self.router.swap_tk_for_exact_tk(self.router.tk1, self.router.tk2, qty, max_amount_in)
        tx = self.router.build_tx_and_send(func)
        self.router.check_contract_success(tx)
        return tx.hex()

