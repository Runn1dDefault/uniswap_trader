import json
import random
import functools
from typing import Callable
from decimal import Decimal, setcontext, ExtendedContext, getcontext

from web3.contract import ContractFunction

from base.config import INFURA_PROVIDERS_FILE, NETWORK


def load_contract(path: str) -> tuple:
    with open(path) as file:
        data = json.load(file)[0]
    abi = data['abi']
    if data.get('networks'):
        contract = data['networks'][NETWORK]
    else:
        contract = data.get('contract')
    if contract is None:
        return None, abi
    return contract, abi


def load_random_infura_provider(network: str = None):
    with open(INFURA_PROVIDERS_FILE) as file:
        rows = file.readlines()
    provider = random.choice(rows)[:-1]
    if network:
        provider = provider.replace('mainnet', network)
    return provider


def long_price_viewing(price: Decimal) -> str:
    setcontext(ExtendedContext)
    getcontext().clear_flags()
    return '{:f}'.format(price)


def auto_call(func: Callable):
    @functools.wraps(func)
    def call_call(self, *args, **kwargs):
        f_result = func(self, *args, **kwargs)
        if not isinstance(f_result, ContractFunction):
            raise DeprecationWarning(f'{func.__name__} returned not an object of the ContractFunction class')
        return f_result.call()
    return call_call
