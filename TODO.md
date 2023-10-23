# ToDo

- The `formatter` has the the `MessageType` ignored when building the post
    - This means going through all messagings and change the icon in the body for the MessageType
- Simplify the messaging:
    - Merge `Message` and `QueueItem`.
    - Make `QueueItem` just a protocol
- Move `MastodonHelper` to `pyxavi`
- Move the Mastodon publish related classes to `pyxavi`
- Make the `git_monitor` to monitor git tags and not only CHANGELOG changes.
- Make a PyPI monitor
- When the Listener starts, loop the status until it gets up and running.
- Rotate the logs

# Done

✅ Fix `Makefile` target `background`.
    ➡️ Moved from targets in `Makefile` to a main runner with commands
✅ Make that the runner `listen` publishes a message when starts listening
    ➡️ the new main runner is more verbose
✅ Organize better the code:
    - Directory for Runners
    - Directory for Configs
    - Split the configs per Common & each Runner and read all together at init
❌ New `Makefile` target `update` or `reload` that: 
    1. brings down the listener
    2. `git pull`
    3. `poetry install` and a possible `poetry lock`
    4. brings up the listener
    ➡️ Won't do, as obscures the tasks to do and now we have a tool to start/stop/status the Listener
✅ Make the `git_monitor` to be able to publish to several other Mastodon accounts (example: own repositories vs. external repositories)
✅ A command to request for the external IP, reusing the logic we already have