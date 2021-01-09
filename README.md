## Welcome to the python-currencycom

This is an unofficial Python wrapper for the Currency.com exchange REST API v1.
I am in no way affiliated with Currency.com, use at your own risk.

### Documentation
Please find official documentation by:
https://exchange.currency.com/api

### QuickStart

[Register an account on Currency.com](https://exchange.currency.com/trading/signup)

[Create an API Key with correct permissions](https://exchange.currency.com/trading/platform/settings)

```
pip install python-currencycom
```

Let's retrieve tradable symbols on the market
```python
from pprint import pprint

from currencycom.client import Client

client = Client('API_KEY', 'SECRET_KEY')

# Exchange info contains various info including tradable symbols
exchange_info = client.get_exchange_info()
tradable_symbols = [x['symbol'] for x in exchange_info['symbols']]
pprint(tradable_symbols,
       indent=2)
```

For more check out [the documentation](https://exchange.currency.com/api) and [Swagger](https://apitradedoc.currency.com/swagger-ui.html#/).
