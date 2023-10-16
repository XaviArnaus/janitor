# ToDo

- Fix `Makefile` target `background`.
- Make that the runner `listen` publishes a message when starts listening
- New `Makefile` target `update` or `reload` that: 
    1. brings down the listener
    2. `git pull`
    3. `poetry install` and a possible `poetry lock`
    4. brings up the listener
- The `formatter` has the the `MessageType` ignored when building the post
    - This means going through all messagings and change the icon in the body for the MessageType
- Simplify the messaging:
    - Merge `Message` and `QueueItem`.
    - Make `QueueItem` just a protocol
- Organize better the code:
    - Directory for Runners
    - Directory for Configs
    - Split the configs per Common & each Runner and read all together at init
- Move `MastodonHelper` to `pyxavi`
- Move the Mastodon publish related classes to `pyxavi`