import functools
from decimal import Decimal, setcontext, ExtendedContext, getcontext
from typing import Callable

from web3.exceptions import ContractLogicError


def long_price_viewing(price: Decimal) -> str:
    setcontext(ExtendedContext)
    getcontext().clear_flags()
    return '{:f}'.format(price)


def find_fee(func: Callable):
    # methods with param fee: int = None
    @functools.wraps(func)
    def send_fee(self, *args, **kwargs):
        if kwargs.get('fee') or kwargs.get('is_v2'):
            return func(self, *args, **kwargs)
        for fee in (3000, 500, 10000):
            try:
                return func(self, *args, **kwargs, fee=fee)
            except ContractLogicError as e:
                if fee == 10000:
                    raise ContractLogicError(e)
                continue
    return send_fee


def auto_call(func: Callable):
    @functools.wraps(func)
    def call_call(self, *args, **kwargs):
        return func(self, *args, **kwargs).call()
    return call_call
