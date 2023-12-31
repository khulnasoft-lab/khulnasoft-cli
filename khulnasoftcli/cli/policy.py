import sys
import json
import click

import khulnasoftcli.clients.apiexternal, khulnasoftcli.clients.hub
import khulnasoftcli.cli

config = {}


@click.group(name="policy", short_help="Policy operations")
@click.pass_context
@click.pass_obj
def policy(ctx_config, ctx):
    global config
    config = ctx_config

    if ctx.invoked_subcommand not in ["hub"]:
        try:
            khulnasoftcli.cli.utils.check_access(config)
        except Exception as err:
            print(khulnasoftcli.cli.utils.format_error_output(config, "policy", {}, err))
            sys.exit(2)


@policy.command(name="add", short_help="Add a policy bundle")
@click.argument(
    "input_policy",
    nargs=1,
    type=click.Path(exists=True),
    metavar="<KhulnaSoft Policy Bundle File>",
)
def add(input_policy):
    ecode = 0

    try:
        with open(input_policy, "r") as FH:
            policybundle = json.loads(FH.read())

        ret = khulnasoftcli.clients.apiexternal.add_policy(
            config, policybundle=policybundle, detail=True
        )
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "policy_add", {}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "policy_add", {}, err))
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@policy.command(name="get", short_help="Get a policy bundle")
@click.argument("policyid", nargs=1)
@click.option("--detail", is_flag=True, help="Get policy bundle as JSON")
def get(policyid, detail):
    """
    POLICYID: Policy ID to get
    """
    ecode = 0

    try:
        ret = khulnasoftcli.clients.apiexternal.get_policy(
            config, policyId=policyid, detail=detail
        )
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "policy_get", {"detail": detail}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "policy_get", {}, err))
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@policy.command(name="list", short_help="List all policies")
def policylist():
    ecode = 0

    try:
        ret = khulnasoftcli.clients.apiexternal.get_policies(config, detail=False)
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "policy_list", {"detail": False}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "policy_list", {}, err))
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@policy.command(name="activate", short_help="Activate a policyid")
@click.argument("policyid", nargs=1)
def activate(policyid):
    """
    POLICYID: Policy ID to be activated
    """
    ecode = 0

    try:
        ret = khulnasoftcli.clients.apiexternal.get_policy(
            config, policyId=policyid, detail=True
        )
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            policy_records = ret["payload"]
            policy_record = {}
            if policy_records:
                policy_record = policy_records[0]
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

        if not policy_record:
            raise Exception("no policy could be fetched to activate")

        policy_record["active"] = True

        ret = khulnasoftcli.clients.apiexternal.update_policy(
            config, policyid, policy_record=policy_record
        )
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "policy_activate", {"policyId": policyid}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(config, "policy_activate", {}, err)
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@policy.command(name="del", short_help="Delete a policy bundle")
@click.argument("policyid", nargs=1)
def delete(policyid):
    """
    POLICYID: Policy ID to delete
    """
    ecode = 0

    try:
        ret = khulnasoftcli.clients.apiexternal.delete_policy(config, policyId=policyid)
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "policy_delete", {}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(config, "policy_delete", {}, err)
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@policy.command(
    name="describe", short_help="Describes the policy gates and triggers available"
)
@click.option(
    "--all",
    help="Display deprecated and end-of-lifed entries, which are filtered out by default",
    is_flag=True,
    default=False,
)
@click.option("--gate", help="Pick a specific gate to describe instead of all")
@click.option(
    "--trigger",
    help="Pick a specific trigger to describe instead of all, requires the --gate option to be specified",
)
def describe(all=False, gate=None, trigger=None):
    ecode = 0
    try:
        ret = khulnasoftcli.clients.apiexternal.describe_policy_spec(config)

        if ret["success"]:
            render_payload = ret["payload"]

            if not gate and not trigger:
                print(
                    khulnasoftcli.cli.utils.format_output(
                        config, "describe_gates", {"all": all}, render_payload
                    )
                )
            elif gate and not trigger:
                print(
                    khulnasoftcli.cli.utils.format_output(
                        config,
                        "describe_gate_triggers",
                        {"gate": gate, "all": all},
                        render_payload,
                    )
                )
            elif gate and trigger:
                print(
                    khulnasoftcli.cli.utils.format_output(
                        config,
                        "describe_gate_trigger_params",
                        {"gate": gate, "trigger": trigger, "all": all},
                        render_payload,
                    )
                )
            else:
                raise click.Abort("Trigger can only be specified with --gate as well")
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(config, "describe_policy", {}, err)
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@policy.group(name="hub", short_help="KhulnaSoft Hub Operations")
@click.pass_context
def hub(ctx):
    if ctx.invoked_subcommand not in ["list", "get"]:
        try:
            khulnasoftcli.cli.utils.check_access(config)
        except Exception as err:
            print(khulnasoftcli.cli.utils.format_error_output(config, "policy", {}, err))
            sys.exit(2)


@hub.command(name="list")
def hublist():
    ecode = 0

    try:
        ret = khulnasoftcli.clients.hub.get_policies(config)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "policy_hub_list", {}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(config, "policy_hub_list", {}, err)
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@hub.command(name="get")
@click.argument("bundlename", nargs=1)
def hubget(bundlename):
    ecode = 0

    try:
        ret = khulnasoftcli.clients.hub.get_policy(config, bundlename)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "policy_hub_get", {}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(config, "policy_hub_get", {}, err)
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@hub.command(name="install")
@click.argument("bundlename", nargs=1)
@click.option("--target-id", help="Override bundle target ID with supplied ID string")
@click.option(
    "--force",
    help="Install specified bundleid in place of existing policy bundle with same ID, if present",
    is_flag=True,
)
def hubinstall(bundlename, target_id, force):
    ecode = 0

    try:
        ret = khulnasoftcli.clients.hub.install_policy(
            config, bundlename, target_id=target_id, force=force
        )
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "policy_add", {}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(
            khulnasoftcli.cli.utils.format_error_output(
                config, "policy_hub_install", {}, err
            )
        )
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)
