import os

import pytest

from currencycom.client import Client

API_KEY_VAR = "API_KEY"
API_SECRET_VAR = "API_SECRET"


@pytest.fixture(scope="session", autouse=True)
def check_env_variables():
    required_vars = [API_KEY_VAR, API_SECRET_VAR]
    missing_vars = []
    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)

    if len(missing_vars) > 0:
        raise EnvironmentError("Missing required environmental variables: "
                               f"{', '.join(missing_vars)}")


@pytest.fixture(scope='function')
def client():
    client = Client(os.environ[API_KEY_VAR], os.environ[API_SECRET_VAR])
    return client
