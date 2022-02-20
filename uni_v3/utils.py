import functools
from typing import Callable

from web3.exceptions import ContractLogicError

from .constants import FEE_AMOUNT


def find_fee(func: Callable):
    # methods with param fee: int = None
    @functools.wraps(func)
    def send_fee(self, *args, **kwargs):
        if kwargs.get('fee') or kwargs.get('is_v2'):
            return func(self, *args, **kwargs)
        for fee in FEE_AMOUNT.values():
            try:
                return func(self, *args, **kwargs, fee=fee)
            except ContractLogicError as e:
                if fee == 10000:
                    raise ContractLogicError(e)
                continue
    return send_fee
