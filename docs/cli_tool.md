# #️⃣ The CLI tool

**Janitor** ships also a CLI tool to execute the runners and other tasks. It is called `jan` and it is meant to run from a terminal.

## Disclaimer

**jan** is a bash script that performs some of the tasks and the rest are forwarded to a Python script executed under Poetry so that it benefits from the virtual environment. That's why **jan**:
- Needs to be executed from the root of the *Janitor* project directory
- Takes a while to run, as it loads all the Python virtual environment

## How to use it?

As a command line script, you can call it with the `-h` argument and you'll receive a print like the following:

```
usage: jan [-h] [--version] [-l LOGLEVEL] [-d] command [subcommand]

CLI command to execute runners and tasks

positional arguments:
  command
  subcommand

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -l LOGLEVEL, --loglevel LOGLEVEL
  -d, --debug
```

You can also use the command `commands` and it will print the full list of available commands:

```
$ bin/jan commands

Janitor v0.5.0

usage: jan command [subcommand]

Command list:

commands            Shows the list of available commands and subcommands
mastodon            Performs tasks related to the Mastodon-like API
  create_app        Creates the Mastodon-like API application session file
  test              Publishes a test message to the Mastodon-like API to ensure that all is set up ok.
  publish_queue     Publishes the current queue to the Mastodon-like API, attending the config file.
sys_info            Performs tasks related to the System Info gathering
  local             Gathers the local System Info, compares with thresholds and publishes if crossed.
  remote            Gathers the local System Info and sends them to a listening server to be processed
listener            Perform tasks related to the Server side listener,that receives System Info and arbitrary messages
  start             Starts the listener.
  status            Requests the status of the listener. Will print the PID if running
  stop              Stops the listener.
scheduler           Perform scheduled tasks, set up in the config file
update_ddns         Discovers the current external IP and updates the Directnic Dynamic DNS registers
git_changes         Discovers changes in the monitored Git repositories and publishes them
validate_config     Validates the config.yaml Configuration file
migrate_config      Migrates the configuration file(s) between versions
  v0.5.0            Migrates from v0.4.0 to v0.5.0
ip                  Returns the current external IP
```

As you can see, there are **commands** that define something to do, **subcommands** in case the command has more subdivisions, and **arguments** that modify the normal run. Please refer to the list above to discover what can **jan** do for you.