import os
from typing import Union

from eth_typing import ChecksumAddress
from web3.types import Wei

from config import ABIS_V3_FILES
from base import BaseTrader


class QuoterV3(BaseTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract_address, self.abi = self.load_contract(
            os.path.join(ABIS_V3_FILES, 'quoter.json'))
        self.contract = self.w3.eth.contract(self.contract_address, abi=self.abi)

    _sqrtPriceLimitX96 = 0

    @property
    def sqrtPriceLimitX96(self):
        return self._sqrtPriceLimitX96

    @sqrtPriceLimitX96.setter
    def sqrtPriceLimitX96(self, value) -> None:
        self._sqrtPriceLimitX96 = value

    @property
    def weth_address(self):
        return self.contract.functions.WETH9().call()

    @property
    def factory(self):
        return self.contract.functions.factory().call()

    def quote_exact_input(self, tk1: ChecksumAddress, tk2: ChecksumAddress, fee: int,
                          amount_in: Union[int, Wei]):
        return self.contract.functions.quoteExactInput(
            self.encode_bytes(tk1, tk2, fee), amount_in).call()

    def quote_exact_input_single(self, tk1: ChecksumAddress, tk2: ChecksumAddress, fee: int,
                                 amount_in: Union[int, Wei]):
        return self.contract.functions.quoteExactInputSingle(
            tk1, tk2, fee, amount_in, self.sqrtPriceLimitX96).call()

    def quote_exact_output(self, tk1: ChecksumAddress, tk2: ChecksumAddress, fee: int,
                           amount_out: Union[int, Wei]):
        return self.contract.functions.quoteExactOutput(
            self.encode_bytes(tk1, tk2, fee), amount_out).call()

    def quote_exact_output_single(self, tk1: ChecksumAddress, tk2: ChecksumAddress, fee: int,
                                  amount_out: Union[int, Wei]):
        return self.contract.functions.quoteExactOutputSingle(
            tk1, tk2, fee, amount_out, self.sqrtPriceLimitX96).call()

    def uniswapV3SwapCallback(self, amount1_delta: int, amount2_delta: int, tk1, tk2, fee):
        return self.contract.functions.uniswapV3SwapCallback(
            amount1_delta, amount2_delta, self.encode_bytes(tk1, tk2, fee)).call()