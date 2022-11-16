"""
Unit tests for controller.py
"""
import json
from icecream import ic
from handlers.handler import Handler


def test_index(client):
    """
    Test HTTP GET to /
    """
    response = client.get("/")
    assert b"Unauthorized." in response.data


def test_malwarebytes(mocker, client):
    """
    Test HTTP POST to url for Malwarebytes
    """
    uri_path = "/7cbPiUCZi"

    response = client.get(uri_path)
    assert b"Unauthorized." in response.data

    response = client.post(
        uri_path,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"incomplete": "object"}),
    )
    ic(response)
    assert 400 == response.status_code
    assert b"Invalid data" in response.data

    payload = {
        "account_name": "adyptation",
        "group_name": "Default",
        "machine_ip": "192.168.4.3",
        "machine_name": "Frodo-Desktop-Pro",
        "nics": "en0",
        "os_platform": "macos",
        "os_release_name": "Ventura",
        "path": "C:\\\\USERS\\\\ADMIN\\\\DESKTOP\\\\80febe47-44fe-4b5e-9549-4677b5d8dc8d.EXE",
        "policy_name": "Default Policy",
        "severity": "SEVERE",
        "status": "found",
        "threat_name": "PUP.Optional.FooBar",
    }
    mocker.patch.object(Handler, "send_to_slack", return_value='{"status": "ok"}')

    response = client.post(
        uri_path, headers={"Content-Type": "application/json"}, data=json.dumps(payload)
    )
    print(payload)
    print(response.data)
    assert 200 == response.status_code
    assert b"ok" in response.data
