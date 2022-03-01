class InsufficientBalance(Exception):
    """Raised when the account has insufficient balance for a transaction."""

    def __init__(self, had: int, needed: int) -> None:
        Exception.__init__(self, f"Insufficient balance. Had {had}, needed {needed}")


class NotFoundPool(Exception):
    pass


class SlipPageError(Exception):
    pass


class PriceLimit(Exception):
    # SPL
    def __init__(self):
        super().__init__('Square root price limit')


class AmountError(Exception):
    # IIA
    def __init__(self):
        super().__init__('Insufficient input amount,'
                         ' an insufficient amount of input token was sent during the callback')

