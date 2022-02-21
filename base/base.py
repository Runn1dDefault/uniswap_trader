import os
from decimal import Decimal
from time import time
from typing import Union

from eth_typing import ChecksumAddress
from web3 import Web3
from eth_abi.packed import encode_abi_packed
from web3.types import Wei, _Hash32

from .config import BASE_ABIS, IPC_PATH
from .constants import ROUTE_TYPES
from .exeptions import InsufficientBalance
from .utils import load_contract


class BaseContractManager:
    CONVERT_MAP = {'1': 'wei', '3': 'kwei', '6': 'mwei', '9': 'gwei', '12': 'szabo', '15': 'finney',
                   '18': 'ether', '21': 'kether', '24': 'mether', '27': 'gether', '30': 'tether'}
    w3 = Web3(Web3.IPCProvider(IPC_PATH))
    max_approval_int = int(f"0x{64 * 'f'}", 16)
    max_approval_check_int = int(f"0x{15 * '0'}{49 * 'f'}", 16)
    _, erc20_abi = load_contract(os.path.join(BASE_ABIS, 'erc20.json'))

    def quantity(self, count: Union[float, int, Decimal], decimal: int) -> int:
        return self.w3.toWei(count, self.CONVERT_MAP[str(decimal)])

    def convert_wei_by_decimal(self, count: Union[Wei, int], decimal: int):
        return self.w3.fromWei(count, self.CONVERT_MAP[str(decimal)])

    weth_address = None
    _eth_address = '0x0000000000000000000000000000000000000000'

    @property
    def eth_address(self):
        return self.w3.toChecksumAddress(self._eth_address)

    @eth_address.setter
    def eth_address(self, address: ChecksumAddress) -> None:
        self.eth_address = address

    def is_eth_address(self, tk: ChecksumAddress) -> bool:
        if tk == self.eth_address:
            return True
        return False

    def is_weth_address(self, tk: ChecksumAddress) -> bool:
        if tk == self.weth_address:
            return True
        return False

    def check_contract_success(self, tx_hash: Union[_Hash32, str]):
        tx_data = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_data.status == 1:
            return True
        return False

    @property
    def deadline(self) -> int:
        return int(time()) + 10 * 60

    def encode_bytes(self, tk1: ChecksumAddress, tk2: ChecksumAddress, fee: int):
        return encode_abi_packed(ROUTE_TYPES, (tk1, fee, self.weth_address, fee, tk2))

    def get_balance(self, address: ChecksumAddress, tk: ChecksumAddress = None) -> Wei:
        if tk is None or self.is_eth_address(tk):
            return self.w3.eth.get_balance(address)
        erc20_contract = self.w3.eth.contract(tk, abi=self.erc20_abi)
        return erc20_contract.functions.balanceOf(address).call()

    def err_insufficient_balance(self, address: ChecksumAddress, qty: Union[Wei, int], tk: ChecksumAddress = None):
        balance = self.get_balance(address, tk)
        if qty > balance:
            raise InsufficientBalance(balance, qty)
