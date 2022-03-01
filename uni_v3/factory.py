import os
from typing import Union

from eth_typing import ChecksumAddress

from base.config import ABIS_V3_FILES
from base.base import BaseContractManager
from base.utils import load_contract


class FactoryV3(BaseContractManager):
    contract_address, abi = load_contract(os.path.join(ABIS_V3_FILES, 'factory.json'))

    def __init__(self, provider_http: str = None):
        super().__init__(provider_http=provider_http)
        self.contract = self.w3.eth.contract(self.contract_address, abi=self.abi)

    def get_pool(self, tk1, tk2, fee: int) -> ChecksumAddress:
        return self.contract.functions.getPool(tk1, tk2, fee).call()

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
