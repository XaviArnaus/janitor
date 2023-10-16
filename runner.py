from argparse import ArgumentParser, Namespace
import pkg_resources
from janitor.runners.runner_protocol import RunnerProtocol
from pyxavi.terminal_color import TerminalColor
from pyxavi.config import Config
from pyxavi.logger import Logger
import os
from definitions import ROOT_DIR
from pyxavi.debugger import full_stack
from string import Template

from janitor.runners.create_app import CreateApp
from janitor.runners.run_local import RunLocal
from janitor.runners.run_remote import RunRemote
from janitor.runners.listen import Listen
from janitor.runners.scheduler import Scheduler
from janitor.runners.publish_queue import PublishQueue
from janitor.runners.publish_test import PublishTest
from janitor.runners.update_ddns import UpdateDdns
from janitor.runners.git_changes import GitChanges

PROGRAM_NAME = "janitor"
CLI_NAME = "jan"
PROGRAM_DESC = "CLI command to execute runners and tasks"
PROGRAM_EPILOG = f"Use [{CLI_NAME} commands] to get a list of available commands."
PROGRAM_VERSION = pkg_resources.get_distribution(PROGRAM_NAME).version
SUBCOMMAND_TOKEN = "#SUBCOMMAND#"
HELP_TOKEN = "#HELP#"
COMMAND_MAP = {
    "commands": (HELP_TOKEN, "Shows the list of available commands and subcommands"),
    "mastodon": (SUBCOMMAND_TOKEN, "Performs tasks related to the Mastodon-like API"),
    "sys_info": (SUBCOMMAND_TOKEN, "Performs tasks related to the System Info gathering"),
    "listen": (
        Listen,
        "Starts the server side listener, that receives System Info and arbitrary messages"
    ),
    "scheduler": (Scheduler, "Perform scheduled tasks, set up in the config file"),
    "update_ddns": (
        UpdateDdns,
        "Discovers the current external IP and updates the Directnic Dynamic DNS registers"
    ),
    "git_changes": (
        GitChanges, "Discovers changes in the monitored Git repositories and publishes them"
    )
}

SUBCOMMAND_MAP = {
    "sys_info": {
        "local": (
            RunLocal,
            "Gathers the local System Info, compares with thresholds and publishes if crossed."
        ),
        "remote": (
            RunRemote,
            "Gathers the local System Info and sends them to a listening server to be processed"
        ),
    },
    "mastodon": {
        "create_app": (CreateApp, "Creates the Mastodon-like API application session file"),
        "test": (
            PublishTest,
            "Publishes a test message to the Mastodon-like API to ensure that all is set up ok."
        ),
        "publish_queue": (
            PublishQueue,
            "Publishes the current queue to the Mastodon-like API, attending the config file."
        ),
    }
}


def print_command_list(with_colors: bool = True):
    main_template = "\n$title\n\nusage: $example_use\n\nCommand list:\n\n$command_list\n"
    title_template = "$name v$version"
    example_template = "$name command [subcommand]"
    command_template = "$command$description"
    subcommand_template = "  $subcommand$description"
    command_max_width = 20
    subcommand_max_width = 18

    if with_colors:
        title_template = f"{TerminalColor.ORANGE_BRIGHT}{title_template}{TerminalColor.END}"
        example_template = f"$name {TerminalColor.YELLOW_BRIGHT}command{TerminalColor.END} " +\
            f"[{TerminalColor.CYAN_BRIGHT}subcommand{TerminalColor.END}]"
        command_template = f"{TerminalColor.YELLOW_BRIGHT}{command_template}{TerminalColor.END}"
        subcommand_template = f"{TerminalColor.CYAN_BRIGHT}{subcommand_template}" +\
            f"{TerminalColor.END}"

    commands_list = []
    for command, pair in COMMAND_MAP.items():
        action, description = pair
        commands_list.append(
            Template(command_template).substitute(
                command=command.ljust(command_max_width), description=description
            )
        )
        if command in SUBCOMMAND_MAP:
            for subcommand, subpair in SUBCOMMAND_MAP[command].items():
                subaction, subdescription = subpair
                commands_list.append(
                    Template(subcommand_template).substitute(
                        subcommand=subcommand.ljust(subcommand_max_width),
                        description=subdescription
                    )
                )

    content = Template(main_template).substitute(
        title=Template(title_template
                       ).substitute(name=PROGRAM_NAME.capitalize(), version=PROGRAM_VERSION),
        example_use=Template(example_template).substitute(name=CLI_NAME),
        command_list="\n".join(commands_list)
    )
    print(content)


def _get_runner_by_command(args: Namespace) -> RunnerProtocol:
    command_candidate = args.command

    if command_candidate in COMMAND_MAP:
        # So we have this command registered.
        #   It can be a direct Runner or forwarding to a subcommand
        if COMMAND_MAP[command_candidate][0] == SUBCOMMAND_TOKEN:
            # Search it then inside the subcommands list
            if command_candidate in SUBCOMMAND_MAP:
                # Now get the subcommand
                subcommand_candidate = args.subcommand
                if subcommand_candidate in SUBCOMMAND_MAP[command_candidate]:
                    # It is a direct Runner.
                    # DO NOT return the instance, let it be in the main.
                    return SUBCOMMAND_MAP[command_candidate][subcommand_candidate][0]
                elif subcommand_candidate is None:
                    # A subcommand is expected
                    raise RuntimeError(
                        f"The requested command '{command_candidate}' expects a" +
                        " subcommand, that is not present. Please type also a subcommand."
                    )
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
            # Rather than ignoring the subcommand, complain for the unexpected argument
            subcommand_candidate = args.subcommand
            if subcommand_candidate is not None:
                raise RuntimeError(
                    f"The requested command '{command_candidate}' is does not expect" +
                    "  subcommands but one is received. Stopping."
                )
            else:
                # It is a direct Runner.
                # DO NOT return the instance, let it be in the main.
                return COMMAND_MAP[command_candidate][0]
    else:
        # Oops! It's not here, return an error
        raise RuntimeError(f"The requested command '{command_candidate}' does not exist")


@staticmethod
def setup_parser() -> ArgumentParser:

    parser = ArgumentParser(prog=CLI_NAME, description=PROGRAM_DESC, epilog=PROGRAM_EPILOG)

    # First argument is the command
    parser.add_argument("command", action="store")

    # Second argument is optional and should be the sub-command (test actions, for example)
    parser.add_argument("subcommand", nargs='?', default=None)

    # Ability to show the version
    parser.add_argument("--version", action="version", version=PROGRAM_VERSION)
    return parser


def run():
    try:
        config = Config(filename=os.path.join(ROOT_DIR, "config.yaml"))
        logger = Logger(config=config, base_path=ROOT_DIR).get_logger()

        # Set up the parser
        parser = setup_parser()

        # Get the arguments
        args = parser.parse_args()

        # This prints the list of available commands and leaves.
        if args.command == "commands":
            print_command_list()
            exit(0)

        # Find the command to execute. It is ready to be instantiated
        runner = _get_runner_by_command(args=args)(config=config, logger=logger)

        # Execute the runner
        runner.run()
    except RuntimeError as e:
        print(TerminalColor.RED_BRIGHT + str(e) + TerminalColor.END)
    except Exception:
        print(full_stack())
