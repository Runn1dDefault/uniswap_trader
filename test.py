# from datetime import datetime
# from typing import Union
#
# import hexbytes
# import requests
#
# from decimal import Decimal
#
# from web3.exceptions import ContractLogicError
# from web3.types import Wei
# from eth_typing import ChecksumAddress
# from uniswap import Uniswap
#
# PROVIDER = 'https://ropsten.infura.io/v3/d6dc1928fa734842bb81ce889a2f7e8b'
# ADDRESS = '0x9bc74DD43970b43ea94760A24043bBe2089A670B'
# PRIVATE_KEY = '28a5525ad829a69dcda8cb068f659117d5305e0437e2a794339d914bf4141363'
#
#
# def get_price(tk1: ChecksumAddress, tk2: ChecksumAddress, chain_id, qty):
#     url = f'https://api.uniswap.org/v1/quote?protocols=v2,v3&tokenInAddress={tk1}&tokenInChainId={chain_id}' \
#           f'&tokenOutAddress={tk2}&tokenOutChainId={chain_id}&amount={qty}&type=exactIn'
#     response = requests.get(url, headers={'origin': 'https://app.uniswap.org'})
#     print(response.status_code)
#     if response.status_code == 200:
#         return Decimal(response.json()['quoteDecimals'])
#
#
# class Trader:
#     chainID = 3
#     convert_map = {'1': 'wei', '3': 'kwei', '6': 'mwei', '9': 'gwei', '12': 'szabo', '15': 'finney',
#                    '18': 'ether', '21': 'kether', '24': 'mether', '27': 'gether', '30': 'tether'}
#
#     def __init__(self, tk1: hexbytes, tk2: hexbytes, tk1_decimal: int, tk2_decimal: int,
#                  slippage: float, tk1_qty: Decimal, tk2_qty: Decimal, sell_percentage: Decimal):
#         self.slippage = slippage
#         self.uniswap = Uniswap(address=ADDRESS, private_key=PRIVATE_KEY, version=2, provider=PROVIDER,
#                                use_estimate_gas=True, default_slippage=slippage)
#         self.tk1 = self.uniswap.w3.toChecksumAddress(tk1)
#         self.tk2 = self.uniswap.w3.toChecksumAddress(tk2)
#         self.tk1_qty = tk1_qty
#         self.tk2_qty = tk2_qty
#         self.tk1_decimal = tk1_decimal
#         self.tk2_decimal = tk2_decimal
#         self.sell_percentage = sell_percentage
#         self.percentage_price = self.get_tk1_price_from_percentage(sell_percentage)
#         self.sell_price = self.tk1_qty + self.percentage_price
#
#     def get_tk1_price_from_percentage(self, percentage: Decimal) -> Decimal:
#         return Decimal('{:f}'.format(self.tk1_qty / 100 * percentage))
#         # self.quantity(self.tk1_qty + percentage_price, self.tk1_decimal)
#
#     def quantity(self, count: Decimal, decimal: int) -> int:
#         return self.uniswap.w3.toWei(count, self.convert_map[str(decimal)])
#
#     def make_trade(self, tk1: ChecksumAddress, tk2: ChecksumAddress, qty: Union[Wei, int]):
#         for fee in (3000, 500, 10000):
#             try:
#                 return self.uniswap.make_trade(tk1, tk2, qty=qty, fee=fee).hex()
#             except ContractLogicError as e:
#                 if fee == 10000:
#                     raise Exception(e)
#                 continue
#
#     def get_price(self, tk1: ChecksumAddress, tk2: ChecksumAddress, qty: Union[Wei, int]):
#         for fee in (3000, 500, 10000):
#             try:
#                 price = self.uniswap.get_price_output(
#                     token0=tk1,
#                     token1=tk2,
#                     qty=qty,
#                     fee=fee
#                 )
#                 return price
#             except Exception as e:
#                 if fee == 10000:
#                     raise Exception(e)
#                 continue
#
#
# USDT = '0x03f7cef050aac29954a97334c00920aa8919dc37'   # 6
# ETH = '0xc778417E063141139Fce010982780140Aa0cD5Ab'    # 18
#
#
# trader = Trader(tk1=ETH, tk2=USDT,
#                 tk1_decimal=18, tk2_decimal=6,
#                 tk1_qty=Decimal('0.1'), tk2_qty=Decimal('0.160712'),
#                 sell_percentage=Decimal('0.1'), slippage=0.3)
#
# q = trader.quantity(trader.tk1_qty, trader.tk1_decimal)
# print(q)
# p = trader.get_price(trader.tk1, trader.tk2, q)
# print(p)
# # c = trader.make_trade(
# #     tk1=trader.tk1, tk2=trader.tk2, qty=trader.quantity(trader.tk1_qty, 18)
# # )
# # p = trader.get_tk1_price_from_percentage(Decimal('1'))

