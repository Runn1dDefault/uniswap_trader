import os
from typing import Union, Tuple

from eth_typing import ChecksumAddress
from web3.types import Wei

from base.base import BaseContractManager
from base.config import ABIS_V2_FILES
from base.utils import auto_call, load_contract


class RouterV2(BaseContractManager):
    contract_address, abi = load_contract(os.path.join(ABIS_V2_FILES, 'router.json'))

    def __init__(self):
        super().__init__()
        self.contract = self.w3.eth.contract(self.contract_address, abi=self.abi)

    @property
    @auto_call
    def weth_address(self):
        return self.contract.functions.WETH()

    @property
    @auto_call
    def factory(self):
        return self.contract.functions.factory()

    @auto_call
    def add_liquidity(self, tk1: ChecksumAddress, tk2: ChecksumAddress, amount_tk1_desired,
                      amount_tk2_desired, min_amount_tk1, min_amount_tk2, address: ChecksumAddress):
        assert all(isinstance(i, int) for i in (
            amount_tk1_desired, amount_tk2_desired, min_amount_tk1, min_amount_tk2))
        return self.contract.functions.addLiquidity(
            tk1, tk2, amount_tk1_desired, amount_tk2_desired, min_amount_tk1, min_amount_tk2,
            address, self.deadline)

    @auto_call
    def add_liquidity_eth(self, tk: ChecksumAddress, tk_amount_desired,
                          min_amount_tk, min_amount_eth, address: ChecksumAddress):
        assert all(isinstance(i, int) for i in (
            min_amount_tk, min_amount_eth, tk_amount_desired))
        return self.contract.functions.addLiquidityETH(
            tk, tk_amount_desired, min_amount_tk, min_amount_eth, address, self.deadline)

    def get_route(self, tk1: ChecksumAddress, tk2: ChecksumAddress) -> Tuple[list, int]:
        if self.is_weth_address(tk1):
            return [self.weth_address, tk2], 1
        elif self.is_weth_address(tk2):
            return [tk1, self.weth_address], 2
        else:
            return [tk1, self.weth_address, tk2], 3

    @auto_call
    def get_amount_in(self, amount_out: Union[int, Wei], reserve_in: int, reserve_out: int):
        return self.contract.functions.getAmountIn(amount_out, reserve_in, reserve_out)

    @auto_call
    def get_amount_out(self, amount_in: Union[int, Wei], reserve_in: int, reserve_out: int):
        return self.contract.functions.getAmountOut(amount_in, reserve_in, reserve_out)

    @auto_call
    def get_amounts_in(self, tk1, tk2, amount_out: Union[int, Wei]):
        return self.contract.functions.getAmountsIn(amount_out, self.get_route(tk1, tk2)[0])

    @auto_call
    def get_amounts_out(self, tk1, tk2, amount_in: Union[int, Wei]):
        return self.contract.functions.getAmountsOut(amount_in, self.get_route(tk1, tk2)[0])

    @auto_call
    def quote(self, amount_tk1: Union[int, Wei], tk1_reserve: int, tk2_reserve: int):
        self.contract.functions.quote(amount_tk1, tk1_reserve, tk2_reserve)

    @auto_call
    def remove_liquidity(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                         liquidity: int, min_amount_tk1: int, min_amount_tk2, address: ChecksumAddress):
        return self.contract.functions.removeLiquidity(
            tk1, tk2, liquidity, min_amount_tk1, min_amount_tk2, address, self.deadline)

    @auto_call
    def remove_liquidity_eth(self, tk: ChecksumAddress, liquidity: int,
                             min_amount_tk: int, min_amount_eth: int, address: ChecksumAddress):
        return self.contract.functions.removeLiquidityETH(
            tk, liquidity, min_amount_tk, min_amount_eth, address, self.deadline)

    def swap_eth_for_exact_tk(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                              amount_out: int, address: ChecksumAddress):
        return self.contract.functions.swapETHForExactTokens(
            amount_out, self.get_route(tk1, tk2), address, self.deadline)

    def swap_exact_eth_for_tk(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                              min_amount_out: int, address: ChecksumAddress):
        return self.contract.functions.swapExactETHForTokens(
            min_amount_out, self.get_route(tk1, tk2), address, self.deadline)

    def swap_exact_eth_for_tk_sft(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                                  min_amount_out: int, address: ChecksumAddress):
        return self.contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
            min_amount_out, self.get_route(tk1, tk2), address, self.deadline)

    def swap_exact_tk_for_eth(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                              amount_in: int, min_amount_out: int, address: ChecksumAddress):
        return self.contract.functions.swapExactTokensForETH(
            amount_in, min_amount_out, self.get_route(tk1, tk2), address, self.deadline)

    def swap_exact_tk_for_eth_sft(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                                  amount_in: int, min_amount_out: int, address: ChecksumAddress):
        return self.contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
            amount_in, min_amount_out, self.get_route(tk1, tk2), address, self.deadline)

    def swap_exact_tk_for_tk(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                             amount_in: int, min_amount_out: int, address: ChecksumAddress):
        return self.contract.functions.swapExactTokensForTokens(
            amount_in, min_amount_out, self.get_route(tk1, tk2), address, self.deadline)

    def swap_exact_tk_for_tk_sft(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                                 amount_in: int, min_amount_out: int, address: ChecksumAddress):
        return self.contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
            amount_in, min_amount_out, self.get_route(tk1, tk2), address, self.deadline)

    def swap_tk_for_exact_eth(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                              amount_out: int, max_amount_in: int, address: ChecksumAddress):
        return self.contract.functions.swapTokensForExactETH(
            amount_out, max_amount_in, self.get_route(tk1, tk2), address, self.deadline)

    def swap_tk_for_exact_tk(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                             amount_out: int, max_amount_in: int, address: ChecksumAddress):
        return self.contract.functions.swapTokensForExactTokens(
            amount_out, max_amount_in, self.get_route(tk1, tk2), address, self.deadline)

