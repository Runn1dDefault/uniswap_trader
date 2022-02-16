import os
from typing import Union

from eth_typing import ChecksumAddress
from web3.types import Wei

from config import ABIS_V3_FILES
from base import BaseTrader


class RouterV3(BaseTrader):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract_address, self.abi = self.load_contract(
            os.path.join(ABIS_V3_FILES, 'router.json'))
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

    def exact_input(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                    amount_in: Union[int, Wei], fee: int, min_amount_out: Union[Wei, int]):
        return self.contract.functions.exactInput(
            self.encode_bytes(tk1, tk2, fee), self.address, self.deadline, amount_in, min_amount_out
        )

    def exact_input_single(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                           amount_in: Union[int, Wei], fee: int, min_amount_out: Union[Wei, int]):
        return self.contract.functions.exactInputSingle(
            tk1, tk2, fee, self.address, self.deadline, amount_in, min_amount_out, self.sqrtPriceLimitX96
        )

    def exact_output(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                     amount_out: Union[int, Wei], fee: int, max_amount_in: Union[Wei, int]):
        return self.contract.functions.exactOutput(
            self.encode_bytes(tk1, tk2, fee), self.address, self.deadline, amount_out, max_amount_in
        )

    def exact_output_single(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                            amount_out: Union[int, Wei], fee: int, max_amount_in: Union[Wei, int]):
        return self.contract.functions.exactOutputSingle().call(
            tk1, tk2, fee, self.address, self.deadline, amount_out, max_amount_in, self.sqrtPriceLimitX96
        )
