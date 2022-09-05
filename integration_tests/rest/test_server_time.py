class TestServerTime:

    def test_response_corresponds_swagger_schema(self, client):
        resp_keys = ['serverTime']
        server_time = client.get_server_time()
        assert len(server_time) == 1
        assert type(server_time) is dict
        assert all(key in resp_keys for key in server_time)
        assert all(server_time[key] is not None for key in server_time)
