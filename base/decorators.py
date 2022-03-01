import functools
from typing import Callable

from base.exeptions import SlipPageError


def catch_raise(func: Callable):
    @functools.wraps(func)
    def raise_err(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            if 'STF' in str(e):
                raise SlipPageError('Error slippage for this trade')
    return raise_err
