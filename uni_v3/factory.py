import os
from typing import Union

from eth_typing import ChecksumAddress

from config import ABIS_V3_FILES
from base import BaseTrader


class FactoryV3(BaseTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract_address, self.abi = self.load_contract(
            os.path.join(ABIS_V3_FILES, 'factory.json'))
        self.contract = self.w3.eth.contract(self.contract_address, abi=self.abi)

    def get_pool(self, tk1, tk2, fee: int) -> Union[tuple, None]:
        pool = self.contract.functions.getPool(tk1, tk2, fee).call()
        if not self.is_eth_address(pool):
            return pool

    def create_pool(self, tk1, tk2, fee: int) -> ChecksumAddress:
        return self.contract.functions.createPool(tk1, tk2, fee).call()

    def fee_amount_tickSpacing(self, fee: int) -> int:
        return self.contract.functions.feeAmountTickSpacing(fee).call()

    @property
    def owner(self) -> ChecksumAddress:
        return self.contract.functions.owner().call()

    @property
    def parameters(self) -> Union[list, tuple]:
        return self.contract.functions.parameters().call()
