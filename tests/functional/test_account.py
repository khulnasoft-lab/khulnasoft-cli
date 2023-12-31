from conftest import call, ExitCode
import json
import pytest


@pytest.mark.parametrize(
    "sub_command", ["add", "del", "disable", "enable", "get", "list", "user", "whoami"]
)
def test_unauthorized(sub_command):
    out, err, code = call(["khulnasoft-cli", "account", sub_command])
    assert code == ExitCode(2)
    assert out == '"Unauthorized"\n'


class TesttList:
    def test_is_authorized(self, admin_call):
        out, err, code = admin_call(["account", "whoami"])
        assert code == ExitCode(0)
        assert "Username: admin" in out
        assert "AccountName: admin" in out
        assert "AccountEmail: admin@mykhulnasoft" in out
        assert "AccountType: admin" in out

    def test_is_authorized_json(self, admin_call):
        out, err, code = admin_call(["--json", "account", "whoami"])
        assert code == ExitCode(0)
        # only one account
        loaded = json.loads(out)
        account = loaded["account"]
        user = loaded["user"]
        assert account["email"] == "admin@mykhulnasoft"
        assert account["name"] == "admin"
        assert account["type"] == "admin"
        assert account["state"] == "enabled"
        assert user["source"] is None
        assert user["type"] == "native"
        assert user["username"] == "admin"


class TestWhoami:
    def test_is_authorized(self, admin_call):
        # get output in split lines, to avoid tabbing problems, real output is
        # not a list, just long lines
        out, err, code = admin_call(["account", "list"], split=True)
        assert code == 0
        assert out[0] == ["Name", "Email", "Type", "State", "Created"]
        # remove the TZ
        assert out[1][:-1] == ["admin", "admin@mykhulnasoft", "admin", "enabled"]

    def test_is_authorized_json(self, admin_call):
        out, err, code = admin_call(["--json", "account", "list"])
        assert code == ExitCode(0)
        # only one account
        loaded = json.loads(out)[0]
        assert loaded["email"] == "admin@mykhulnasoft"
        assert loaded["name"] == "admin"
        assert loaded["type"] == "admin"
        assert loaded["state"] == "enabled"
        assert "last_updated" in loaded


class TestDisable:
    def test_account_not_found(self, admin_call):
        out, err, code = admin_call(["account", "disable", "foo"])
        assert code == ExitCode(1)
        assert "Error: Account not found" in out
        assert "HTTP Code: 404" in out
        assert "Detail: {" in out
        assert "'error_codes': []" in out

    def test_disable_account(self, add_account, admin_call):
        account_name = add_account()
        out, err, code = admin_call(["account", "disable", account_name])
        assert code == ExitCode(0)
        assert out == "Success\n"

    def test_disable_account_fails_deleting(self, add_account, admin_call):
        account_name = add_account()
        admin_call(["account", "disable", account_name])
        admin_call(["account", "del", "--dontask", account_name])
        out, err, code = admin_call(["account", "disable", account_name])
        assert code == ExitCode(1)
        assert "Error: Invalid account state change requested." in out
        assert "Cannot go from state deleting to state disabled" in out

    def test_del_account_fails_deleting(self, add_account, admin_call):
        account_name = add_account()
        admin_call(["account", "disable", account_name])
        admin_call(["account", "del", "--dontask", account_name])
        out, err, code = admin_call(["account", "del", "--dontask", account_name])
        assert code == ExitCode(1)
        assert "Error: Invalid account state change requested." in out
        assert "Cannot go from state deleting to state deleting" in out
