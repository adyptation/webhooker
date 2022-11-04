import requests_mock
from handlers.handler import Handler


def test_handler_create_random_string():
    rs = Handler.create_random_string()
    assert len(rs) == 40


def not_today_test_handler_run(mocker):
    mocker.patch.object(Handler, "send_to_slack", return_value='{"status": "ok"}')
    h = Handler()
    response = h.run()
    assert response == "ok"
