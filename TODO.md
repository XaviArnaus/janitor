# ToDo

- Simplify the messaging:
    - Merge `Message` and `QueueItem`.
    - Make `QueueItem` just a protocol
- Move the Mastodon publish related classes to `pyxavi`
- Make the `git_monitor` to monitor git tags and not only CHANGELOG changes.
- Make a PyPI monitor
- When the Listener starts, loop the status until it gets up and running.
- Iterate the Scheduler, should not be defined so much manually. Also should be a CLI command to list Scheduleable tasks
- Make scheduler to pick up what to do and then execute, to avoid long tasks delay the next and when checked they are not in the window time anymore
- Make that the runner for Log rotate also publishes a toot when it's done, according to a new config param
- Remove the deprecated set of Makefile targets
- Migrar pyxavi logging from old config to new config

# Done

✅ Move `MastodonHelper` to `pyxavi`
✅ Iterate all log messages: Move innecessary infos to debug and introduce some color scheme
✅ The `formatter` has the the `MessageType` ignored when building the post
✅ Rotate the logs
✅ A command to request for the external IP, reusing the logic we already have
✅ Make the `git_monitor` to be able to publish to several other Mastodon accounts (example: own repositories vs. external repositories)
❌ New `Makefile` target `update` or `reload` that: 
    1. brings down the listener
    2. `git pull`
    3. `poetry install` and a possible `poetry lock`
    4. brings up the listener
    ➡️ Won't do, as obscures the tasks to do and now we have a tool to start/stop/status the Listener
✅ Organize better the code:
    - Directory for Runners
    - Directory for Configs
    - Split the configs per Common & each Runner and read all together at init
✅ Make that the runner `listen` publishes a message when starts listening
    ➡️ the new main runner is more verbose
✅ Fix `Makefile` target `background`.
    ➡️ Moved from targets in `Makefile` to a main runner with commands





