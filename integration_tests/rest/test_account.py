class TestAccount:
    def test_base(self, client):
        account_info = client.get_account_info()
        assert len(account_info) > 0

    def test_show_balances_without_0(self, client):
        account_info = client.get_account_info(show_zero_balance=False)
        assert all((balance["free"] + balance["free"]) > 0
                   for balance in account_info["balances"])

    def test_show_balances_with_0(self, client):
        account_info = client.get_account_info(show_zero_balance=True)
        assert not all((balance["free"] + balance["free"]) > 0
                       for balance in account_info["balances"])
