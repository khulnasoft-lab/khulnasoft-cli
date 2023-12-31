import json
import sys

import click

import khulnasoftcli.cli.utils
import khulnasoftcli.clients.apiexternal

config = {}


@click.group(name="repo", short_help="Repository operations")
@click.pass_obj
def repo(ctx_config):
    global config
    config = ctx_config

    try:
        khulnasoftcli.cli.utils.check_access(config)
    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "repo", {}, err))
        sys.exit(2)


@repo.command(name="add", short_help="Add a repository")
@click.option(
    "--noautosubscribe",
    is_flag=True,
    help="If set, instruct the engine to disable subscriptions for any discovered tags.",
)
@click.option(
    "--lookuptag",
    help="Specify a tag to use for repo tag scan if 'latest' tag does not exist in the repo.",
)
@click.option(
    "--dryrun",
    is_flag=True,
    help="List which tags would actually be watched if this repo was added (without actually adding the repo)",
)
@click.argument("input_repo", nargs=1)
def add(input_repo, noautosubscribe, lookuptag, dryrun):
    """
    INPUT_REPO: Input repository can be in the following formats: registry/repo
    """
    response_code = 0

    auto_subscribe = not noautosubscribe
    image_info = khulnasoftcli.cli.utils.parse_dockerimage_string(input_repo)
    input_repo = image_info["registry"] + "/" + image_info["repo"]

    try:
        ret = khulnasoftcli.clients.apiexternal.add_repo(
            config,
            input_repo,
            auto_subscribe=auto_subscribe,
            lookup_tag=lookuptag,
            dry_run=dryrun,
        )
        response_code = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "repo_add", {"dry_run": dryrun}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "repo_add", {}, err))
        if not response_code:
            response_code = 2

    khulnasoftcli.cli.utils.doexit(response_code)


@repo.command(name="list", short_help="List added repositories")
def listrepos():
    ecode = 0

    try:
        ret = khulnasoftcli.clients.apiexternal.get_repo(config)
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret["success"]:
            print(
                khulnasoftcli.cli.utils.format_output(
                    config, "repo_list", {}, ret["payload"]
                )
            )
        else:
            raise Exception(json.dumps(ret["error"], indent=4))

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "repo_list", {}, err))
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@repo.command(name="get", short_help="Get a repository")
@click.argument("input_repo", nargs=1)
def get(input_repo):
    """
    INPUT_REPO: Input repository can be in the following formats: registry/repo
    """
    ecode = 0

    image_info = khulnasoftcli.cli.utils.parse_dockerimage_string(input_repo)
    input_repo = image_info["registry"] + "/" + image_info["repo"]

    try:
        ret = khulnasoftcli.clients.apiexternal.get_repo(config, input_repo=input_repo)
        if ret:
            ecode = khulnasoftcli.cli.utils.get_ecode(ret)
            if ret["success"]:
                print(
                    khulnasoftcli.cli.utils.format_output(
                        config, "repo_get", {}, ret["payload"]
                    )
                )
            else:
                raise Exception(json.dumps(ret["error"], indent=4))
        else:
            raise Exception("operation failed with empty response")

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "repo_get", {}, err))
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@repo.command(
    name="del",
    short_help="Delete a repository from the watch list (does not delete already analyzed images)",
)
@click.argument("input_repo", nargs=1)
def delete(input_repo):
    """
    INPUT_REPO: Input repo can be in the following formats: registry/repo
    """
    ecode = 0

    image_info = khulnasoftcli.cli.utils.parse_dockerimage_string(input_repo)
    input_repo = image_info["registry"] + "/" + image_info["repo"]

    try:
        ret = khulnasoftcli.clients.apiexternal.delete_repo(config, input_repo)
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret:
            if ret["success"]:
                print(
                    khulnasoftcli.cli.utils.format_output(
                        config, "repo_delete", {}, ret["payload"]
                    )
                )
            else:
                raise Exception(json.dumps(ret["error"], indent=4))
        else:
            raise Exception("operation failed with empty response")

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "repo_delete", {}, err))
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@repo.command(
    name="unwatch",
    short_help="Instruct engine to stop automatically watching the repo for image updates",
)
@click.argument("input_repo", nargs=1)
def unwatch(input_repo):
    """
    INPUT_REPO: Input repo can be in the following formats: registry/repo
    """
    ecode = 0

    image_info = khulnasoftcli.cli.utils.parse_dockerimage_string(input_repo)
    input_repo = image_info["registry"] + "/" + image_info["repo"]

    try:
        ret = khulnasoftcli.clients.apiexternal.unwatch_repo(config, input_repo)
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret:
            if ret["success"]:
                print(
                    khulnasoftcli.cli.utils.format_output(
                        config, "repo_unwatch", {}, ret["payload"]
                    )
                )
            else:
                raise Exception(json.dumps(ret["error"], indent=4))
        else:
            raise Exception("operation failed with empty response")

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "repo_unwatch", {}, err))
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)


@repo.command(
    name="watch",
    short_help="Instruct engine to start automatically watching the repo for image updates",
)
@click.argument("input_repo", nargs=1)
def watch(input_repo):
    """
    INPUT_REPO: Input repo can be in the following formats: registry/repo
    """
    ecode = 0

    image_info = khulnasoftcli.cli.utils.parse_dockerimage_string(input_repo)
    input_repo = image_info["registry"] + "/" + image_info["repo"]

    try:
        ret = khulnasoftcli.clients.apiexternal.watch_repo(config, input_repo)
        ecode = khulnasoftcli.cli.utils.get_ecode(ret)
        if ret:
            if ret["success"]:
                print(
                    khulnasoftcli.cli.utils.format_output(
                        config, "repo_watch", {}, ret["payload"]
                    )
                )
            else:
                raise Exception(json.dumps(ret["error"], indent=4))
        else:
            raise Exception("operation failed with empty response")

    except Exception as err:
        print(khulnasoftcli.cli.utils.format_error_output(config, "repo_watch", {}, err))
        if not ecode:
            ecode = 2

    khulnasoftcli.cli.utils.doexit(ecode)
