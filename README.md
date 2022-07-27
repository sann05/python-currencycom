## Welcome to the python-currencycom

This is an unofficial Python wrapper for the Currency.com exchange REST API v1 and Websockets API.
I am in no way affiliated with Currency.com, use at your own risk.

### Documentation
Please find official documentation by:
https://exchange.currency.com/api

Or Swagger by the link: https://apitradedoc.currency.com/swagger-ui.html#/.


### QuickStart

[Register an account on Currency.com](https://exchange.currency.com/trading/signup)

[Create an API Key with correct permissions](https://exchange.currency.com/trading/platform/settings)

```
pip install python-currencycom
```

Let's retrieve tradable symbols on the market
```python
from pprint import pprint

from currencycom.client import CurrencycomClient as Client

client = Client('API_KEY', 'SECRET_KEY')

# Exchange info contains various info including tradable symbols
exchange_info = client.get_exchange_info()
tradable_symbols = [x['symbol'] for x in exchange_info['symbols']]
pprint(tradable_symbols,
       indent=2)
```

### Hybrid = Websockets + REST API

Python3.6+ is required for the websockets support

```python
import time
import asyncio

from pprint import pprint

from currencycom.hybrid import CurrencycomHybridClient


def your_handler(message):
    pprint(message, indent=2)


async def keep_waiting():
    while True:
        await asyncio.sleep(20)


client = CurrencycomHybridClient(api_key='YOUR_API_KEY', api_secret='YOUR_API_SECRET',
                                 handler=your_handler, demo=True)

# Subscribe to market data
client.subscribe("BTC/USD_LEVERAGE", "ETH/USD_LEVERAGE")

# Run the client in a thread
client.run()
time.sleep(3)

# Also you can use REST API
pprint(client.rest.get_24h_price_change("BTC/USD_LEVERAGE"))

loop = asyncio.get_event_loop()
loop.run_until_complete(keep_waiting())
```

Default symbol price handler is provided for you, you can use it or write your own.

For more check out [the documentation](https://exchange.currency.com/api) and [Swagger](https://apitradedoc.currency.com/swagger-ui.html#/).

