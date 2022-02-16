import os

from eth_typing import ChecksumAddress

from base import BaseTrader
from config import ABIS_V2_FILES


class FactoryV2(BaseTrader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contract_address, self.abi = self.load_contract(
            os.path.join(ABIS_V2_FILES, 'factory.json'))
        self.contract = self.w3.eth.contract(self.contract_address, abi=self.abi)

    def all_pairs(self, tk_id: int):
        return self.contract.functions.allPairs(tk_id).call()

    @property
    def all_pairs_length(self):
        return self.contract.functions.allPairsLength().call()

    def create_pair(self, tk1: ChecksumAddress, tk2: ChecksumAddress):
        return self.contract.functions.createPair(tk1, tk2).call()

    @property
    def fee_to(self):
        return self.contract.functions.feeTo().call()

    def set_fee_to(self, address: ChecksumAddress):
        return self.contract.functions.setFeeTo(address).call()

    def get_pair(self, tk1: ChecksumAddress, tk2: ChecksumAddress):
        return self.contract.functions.getPair(tk1, tk2).call()
