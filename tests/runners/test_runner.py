from argparse import ArgumentParser
from runner import print_command_list, _get_runner_by_command, setup_parser, run,\
                    PROGRAM_NAME, PROGRAM_DESC, PROGRAM_EPILOG, PROGRAM_VERSION,\
                    SUBCOMMAND_TOKEN, CLI_NAME
from unittest.mock import patch, Mock, call
import pytest
from unittest import TestCase
from definitions import ROOT_DIR
from pyxavi.config import Config
from pyxavi.logger import Logger
import os
from janitor.runners.runner_protocol import RunnerProtocol

test_command_map = {
    "command_1": ("runner_1", "description_1"),
    "command_2": (SUBCOMMAND_TOKEN, "description_2")
}
test_subcommand_map = {
    "command_2": {
        "subcommand_a": ("runner_a", "description_a"),
        "subcommand_b": ("runner_b", "description_b")
    }
}


def test_setup_parser():

    mocked_argument_parser = Mock()
    mocked_argument_parser.__class__ = ArgumentParser
    mocked_argument_parser.return_value = None
    mocked_add_argument = Mock()
    with patch.object(ArgumentParser, "__init__", new=mocked_argument_parser):
        with patch.object(ArgumentParser, "add_argument", new=mocked_add_argument):
            _ = setup_parser()

    mocked_argument_parser.assert_called_once_with(
        prog=CLI_NAME, description=PROGRAM_DESC, epilog=PROGRAM_EPILOG
    )
    mocked_add_argument.assert_has_calls(
        [
            call("command", action="store"),
            call("subcommand", nargs='?', default=None),
            call("--version", action="version", version=PROGRAM_VERSION)
        ]
    )


@pytest.mark.parametrize(
    argnames=('command', 'subcommand', 'expected_runner'),
    argvalues=[
        ("command_1", None, "runner_1"),
        ("command_2", "subcommand_a", "runner_a"),
        ("command_2", "subcommand_b", "runner_b"),
        (None, None, False),
        ("command_2", None, False),
        ("command_1", "command_2", False),
        ("command_2", "subcommmand_c", False),
    ],
)
def test_get_runner_by_command(command, subcommand, expected_runner, capsys):
    # For test purposes, runners here ("runner_(0-9)+") are strings,
    #   while in the program are meant to be the class of the runner,
    #   so that once it is returned by the function, the result
    #   can be directly instantiated.
    #
    #   class Example:
    #       def __init__(self, param: str):
    #           ...
    #
    #   command_map = {
    #       "command_1": (Example, "I am the description")
    #   }
    #
    #   runner = _get_runner_by_command(args=parsed_args)
    #   instantiated_runner = runner(param="parameter in the runner's constructor")
    #

    # Initialize
    parser = setup_parser()

    received_arguments = []
    if command is not None:
        received_arguments.append(command)
    if subcommand is not None:
        received_arguments.append(subcommand)

    if command is None:
        with pytest.raises(SystemExit):
            parser.parse_args(received_arguments)
            out, err = capsys.readouterr()
            assert out == f"{PROGRAM_NAME}: error: " +\
                "the following arguments are required: command\n"
        return
    else:
        args = parser.parse_args(received_arguments)

    with patch("runner.COMMAND_MAP", new=test_command_map):
        with patch("runner.SUBCOMMAND_MAP", new=test_subcommand_map):
            if expected_runner is False:
                with TestCase.assertRaises("runner", RuntimeError):
                    runner_to_call = _get_runner_by_command(args=args)
            else:
                runner_to_call = _get_runner_by_command(args=args)
                assert runner_to_call == expected_runner


def test_print_command_list(capsys):
    with patch("runner.COMMAND_MAP", new=test_command_map):
        with patch("runner.SUBCOMMAND_MAP", new=test_subcommand_map):
            print_command_list(with_colors=False)

    captured = capsys.readouterr()

    assert captured.out == f"\n{PROGRAM_NAME.capitalize()} v{PROGRAM_VERSION}\n\n" +\
        "usage: jan command [subcommand]\n\n" +\
        "Command list:\n\n" +\
        "command_1           description_1\n" +\
        "command_2           description_2\n" +\
        "  subcommand_a      description_a\n" +\
        "  subcommand_b      description_b\n\n"


def test_run_command():

    class Namespace:
        command: str
        subcommad: str

        def __init__(self, command: str, subcommand: str = None) -> None:
            self.command = command
            self.subcommad = subcommand

    parsed_args = Namespace("command_1")
    mocked_config_init = Mock()
    mocked_config_init.return_value = None
    mocked_logger_init = Mock()
    mocked_logger_init.return_value = None
    mocked_get_logger = Mock()
    mocked_parser = Mock()
    mocked_setup_parser = Mock()
    mocked_setup_parser.return_value = mocked_parser
    mocked_get_runner = Mock()
    mocked_parse_args = Mock()
    mocked_parse_args.return_value = parsed_args
    mocked_runner_run = Mock(name="runner.run")
    mocked_returned_runner = Mock(name="returned_runner")
    mocked_returned_runner.return_value = mocked_runner_run
    mocked_get_runner = Mock(name="get_runner")
    mocked_get_runner.return_value = mocked_returned_runner
    with patch.object(Config, "__init__", new=mocked_config_init):
        with patch.object(Logger, "__init__", new=mocked_logger_init):
            with patch.object(Logger, "get_logger", new=mocked_get_logger):
                with patch("runner.setup_parser", new=mocked_setup_parser):
                    with patch.object(mocked_parser, "parse_args", new=mocked_parse_args):
                        with patch("runner._get_runner_by_command", new=mocked_get_runner):
                            with patch.object(RunnerProtocol,
                                              "__init__",
                                              new=mocked_returned_runner):
                                with patch.object(mocked_runner_run,
                                                  "run",
                                                  new=mocked_runner_run):
                                    run()

    mocked_config_init.assert_called_once_with(filename=os.path.join(ROOT_DIR, "config.yaml"))
    mocked_logger_init.assert_called()
    mocked_setup_parser.assert_called_once()
    mocked_parse_args.assert_called_once()

    mocked_get_runner.assert_called_once_with(args=parsed_args)
    mocked_returned_runner.assert_called_once()
    mocked_runner_run.assert_called_once()
