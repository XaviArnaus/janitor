from argparse import ArgumentParser, Namespace
import pkg_resources
from janitor.runners.runner_protocol import RunnerProtocol
from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from pyxavi.logger import Logger
import os
from definitions import ROOT_DIR
from pyxavi.debugger import full_stack

from janitor.runners.create_app import CreateApp
from janitor.runners.run_local import RunLocal
from janitor.runners.run_remote import RunRemote
from janitor.runners.listen import Listen
from janitor.runners.scheduler import Scheduler
from janitor.runners.publish_queue import PublishQueue
from janitor.runners.publish_test import PublishTest
from janitor.runners.update_ddns import UpdateDdns
from janitor.runners.publish_git_changes import PublishGitChanges

PROGRAM_NAME = "janitor"
PROGRAM_DESC = "CLI command to trigger the runners"
PROGRAM_VERS = pkg_resources.get_distribution(PROGRAM_NAME).version
SUBCOMMAND_TOKEN = "#SUBCOMMAND#"
COMMAND_MAP = {
    "create_app": CreateApp,
    "sys_info": SUBCOMMAND_TOKEN,
    "listen": Listen,
    "scheduler": Scheduler,
    "publish_test": PublishTest,
    "publish_queue": PublishQueue,
    "update_ddns": UpdateDdns,
    "publish_git_changes": PublishGitChanges
}

SUBCOMMAND_MAP = {
    "sys_info": {
        "local": RunLocal,
        "remote": RunRemote,
    }
}


def _get_runner__by_command(args: Namespace) -> RunnerProtocol:
    command_candidate = args.command

    if command_candidate in COMMAND_MAP:
        # So we have this command registered.
        #   It can be a direct Runner or forwarding to a subcommand
        if COMMAND_MAP[command_candidate] == SUBCOMMAND_TOKEN:
            # Search it then inside the subcommands list
            if command_candidate in SUBCOMMAND_MAP:
                # Now get the subcommand
                subcommand_candidate = args.subcommand
                if subcommand_candidate in SUBCOMMAND_MAP[command_candidate]:
                    # It is a direct Runner.
                    # DO NOT return the instance, let it be in the main.
                    return SUBCOMMAND_MAP[command_candidate][subcommand_candidate]
                else:
                    # Oops! It's not here, return an error
                    raise RuntimeError(
                        f"The requested subcommand '{subcommand_candidate}' relates to no" +
                        f" module for the command '{command_candidate}'"
                    )
            else:
                # Oops! Seems like the command does not have an entry into subcommands
                raise RuntimeError(
                    f"The requested command '{command_candidate}' is set up to have subcommands"
                    + " but these are not set up. Mostly a Runner setup error."
                )
        else:
            # It is a direct Runner.
            # DO NOT return the instance, let it be in the main.
            return COMMAND_MAP[command_candidate]
    else:
        # Oops! It's not here, return an error
        raise RuntimeError(f"The requested command '{command_candidate}' does not exist")


def setup_parser() -> ArgumentParser:

    parser = ArgumentParser(prog=PROGRAM_NAME, description=PROGRAM_DESC)

    # First argument is the command
    parser.add_argument("command", action="store")

    # Second argument is optional and should be the sub-command (test actions, for example)
    parser.add_argument("subcommand", nargs='?', default=None)

    # Ability to show the version
    parser.add_argument("--version", action="version", version=PROGRAM_VERS)
    return parser


def run():
    try:
        config = Config(filename=os.path.join(ROOT_DIR, "config.yaml"))
        logger = Logger(config=config, base_path=ROOT_DIR).get_logger()

        # Set up the parser
        parser = setup_parser()

        # Get the arguments
        args = parser.parse_args()

        # Find the command to execute. It is ready to be instantiated
        runner = _get_runner__by_command(args=args)(config=config, logger=logger)

        # Execute the runner
        runner.run()
    except RuntimeError as e:
        print(TerminalColor.RED_BRIGHT + str(e) + TerminalColor.END)
    except Exception:
        print(full_stack())
