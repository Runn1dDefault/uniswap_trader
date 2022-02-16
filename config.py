import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

PROVIDER = 'https://ropsten.infura.io/v3/d6dc1928fa734842bb81ce889a2f7e8b'

BASE_ABIS = os.path.join(BASE_DIR, 'abis')
ABIS_V3_FILES = os.path.join(BASE_ABIS, 'abis_v3')
ABIS_V2_FILES = os.path.join(BASE_ABIS, 'abis_v2')


ADDRESS = '0x9bc74DD43970b43ea94760A24043bBe2089A670B'
PRIVATE_KEY = '28a5525ad829a69dcda8cb068f659117d5305e0437e2a794339d914bf4141363'

