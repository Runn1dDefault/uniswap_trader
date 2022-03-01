import os
from typing import Union

from eth_typing import ChecksumAddress, Address
from web3.types import Wei

from base.config import ABIS_V3_FILES
from base.base import BaseContractManager
from base.utils import load_contract


class RouterV3(BaseContractManager):
    contract_address, abi = load_contract(os.path.join(ABIS_V3_FILES, 'router.json'))

    def __init__(self, provider_http: str = None):
        super().__init__(provider_http=provider_http)
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
                    amount_in: Union[int, Wei], fee: int, min_amount_out: Union[Wei, int],
                    address: Union[Address, ChecksumAddress, str]):
        return self.contract.functions.exactInput(
            self.encode_bytes(tk1, tk2, fee), address, self.deadline, amount_in, min_amount_out
        )

    def exact_input_single(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                           amount_in: Union[int, Wei], fee: int, min_amount_out: Union[Wei, int],
                           address: Union[Address, ChecksumAddress, str]):
        return self.contract.functions.exactInputSingle(
            {
                "tokenIn": tk1,
                "tokenOut": tk2,
                "fee": fee,
                "recipient": address,
                "deadline": self.deadline,
                "amountIn": amount_in,
                "amountOutMinimum": min_amount_out,
                "sqrtPriceLimitX96": self.sqrtPriceLimitX96,
            }
        )

    def exact_output(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                     amount_out: Union[int, Wei], fee: int, max_amount_in: Union[Wei, int],
                     address: Union[Address, ChecksumAddress, str]):
        return self.contract.functions.exactOutput(
            self.encode_bytes(tk1, tk2, fee), address, self.deadline, amount_out, max_amount_in
        )

    def exact_output_single(self, tk1: ChecksumAddress, tk2: ChecksumAddress,
                            amount_out: Union[int, Wei], fee: int, max_amount_in: Union[Wei, int],
                            address: Union[Address, ChecksumAddress, str]):
        return self.contract.functions.exactOutputSingle().call(
            {
                "tokenIn": tk1,
                "tokenOut": tk2,
                "fee": fee,
                "recipient": address,
                "deadline": self.deadline,
                "amountOut": amount_out,
                "amountInMaximum": max_amount_in,
                "sqrtPriceLimitX96": self.sqrtPriceLimitX96,
            }
        )
