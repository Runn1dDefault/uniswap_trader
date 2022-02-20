import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

BASE_ABIS = os.path.join(BASE_DIR, 'materials/abis')
ABIS_V3_FILES = os.path.join(BASE_ABIS, 'abis_v3')
ABIS_V2_FILES = os.path.join(BASE_ABIS, 'abis_v2')

NETWORK = os.environ['NETWORK']
INFURA_PROVIDERS_FILE = os.path.join(BASE_DIR, 'materials/providers.txt')

# after docker container run
IPC_PATH = os.path.join(BASE_DIR, f'materials/nodes/{NETWORK}/geth.ipc')
# my local path
# IPC_PATH = "/home/me/.ethereum/ropsten/geth.ipc"

ADDRESS = os.environ['ADDRESS']
PRIVATE_KEY = os.environ['PRIVATE_KEY']
