# Run geth ligth node
```commandline
$ docker-compose -f docker-compose-ipc.yml up -d
```
>Next, you need to wait for the end of synchronization,
> if you're lucky it will take a few minutes
# EXAMPLE on ropsten network
```shell
>> from time import time
>> time()
1645391307.4048705

>> from base.config import ADDRESS, PRIVATE_KEY
>> from base.constants import WETH, UNIV3
>> from uni_v2.associations import TraderV2
>> from uni_v3.associations import TraderV3
>> trader_v2 = TraderV2(ADDRESS, PRIVATE_KEY)
>> trader_v2.init(WETH, UNIV3, 0.1, 18)
>> price_in = trader_v2.price_input()
>> trader_v2.init(WETH, UNIV3, 0.1, 18)
>> price_out = trader_v2.price_output()
>> print("V2:", price_in, price_out)
V2: 613980496286740249 16292060104868525

>> trader_v3 = TraderV3(ADDRESS, PRIVATE_KEY)
>> trader_v3.init(WETH, UNIV3, 0.1, 18)
>> price_out, fee_out = trader_v3.price_input()
>> trader_v3.init(WETH, UNIV3, 0.1, 18)
>> price_in, fee_in = trader_v3.price_output()
>> print("V3:", price_in, fee_in, price_out, fee_out)
V3: 16296062741009488 500 617469516738177855 500
```