from decimal import Decimal, setcontext, ExtendedContext, getcontext


def long_price_viewing(price: Decimal) -> str:
    setcontext(ExtendedContext)
    getcontext().clear_flags()
    return '{:f}'.format(price)

