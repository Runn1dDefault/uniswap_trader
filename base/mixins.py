from time import sleep
from typing import Union

from eth_typing import Address, ChecksumAddress
from hexbytes import HexBytes
from web3.contract import ContractFunction, Contract
from web3.types import Wei, TxParams


class BaseTraderMixin:
    address: Union[Address, ChecksumAddress, str]
    _private_key: Union[HexBytes, str]
    tk1: Union[Address, ChecksumAddress, str]
    tk2: Union[Address, ChecksumAddress, str]
    amount: Union[int, Wei]

    def init(self, tk1: Union[Address, ChecksumAddress, str],
             tk2: Union[Address, ChecksumAddress, str], amount: float, tk_decimals):
        assert tk1 != tk2
        self.tk1 = self.w3.toChecksumAddress(tk1)
        self.tk2 = self.w3.toChecksumAddress(tk2)
        self.amount = self.quantity(amount, tk_decimals)
        self.err_insufficient_balance(self.address, self.amount)

    def build_tx_and_send(self, function: ContractFunction):
        params: TxParams = {"from": self.address, "value": Wei(0),
                            "nonce": self.w3.eth.get_transaction_count(self.address)}
        tx = function.buildTransaction(params)
        tx['gas'] = Wei(int(self.w3.eth.estimate_gas(tx) * 1.2))
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self._private_key)
        return self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    def approve(self, token: ChecksumAddress, router_address: str) -> None:
        erc20_contract = self.w3.eth.contract(token, abi=self.erc20_abi)
        if self.__is_approved(erc20_contract, router_address):
            tx = self.build_tx_and_send(
                erc20_contract.functions.approve(router_address, self.max_approval_int))
            self.check_contract_success(tx)
            sleep(1)

    def __is_approved(self, erc20_contract: Contract, router_address: str) -> bool:
        check_amount = (erc20_contract.functions.allowance(self.address, router_address).call()
                        >= self.max_approval_check_int)
        if check_amount:
            return True
        return False
