import os
from typing import Union

from eth_typing import ChecksumAddress

from base.config import ABIS_V3_FILES
from base.base import BaseContractManager
from base.utils import load_contract


class FactoryV3(BaseContractManager):
    contract_address, abi = load_contract(os.path.join(ABIS_V3_FILES, 'factory.json'))

    def __init__(self):
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
