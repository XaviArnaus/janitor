import os
from definitions import CONFIG_DIR
from pyxavi.terminal_color import TerminalColor
from pyxavi.storage import Storage
from pyxavi.debugger import full_stack
from string import Template
import copy

REQUEST_CONFIG_NAME = "Origin config file [$path] (press ENTER to accept default):"
DEBUG = True
SEPARATOR = "."

# This represents old location to new location
# When some internals are moved, the siblings need to be pointed individually
# In this case, this is only a very minimal config edition
MAP_OLD_TO_NEW = {
    "main.yaml": {
        "logger.to_file": ("main.yaml", "logger.file.active"),
        "logger.filename": ("main.yaml", "logger.file.filename"),
        "logger.to_stdout": ("main.yaml", "logger.stdout.filename"),
    }
}


def get_config_from_user(file_path: str) -> Storage:
    # Get the origin
    config_path = input(Template(REQUEST_CONFIG_NAME).substitute(path=file_path))
    if config_path == "":
        log("Using suggested default config path and name")
        config_path = file_path
    else:
        log(f"Using user input config: [{config_path}]")

    # Load the origin config file. Will fail otherwise.
    origin_storage = Storage(config_path)
    log("Original config file loaded")

    return origin_storage


def run():
    try:
        # Ensure that the target CONFIG_DIR exists, otherwise create it.
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            log(f"Created the target directory [{CONFIG_DIR}]")

        # Create the target files and keep them in memory
        target_storage = {}
        for origin_file, target_info in MAP_OLD_TO_NEW.items():
            log(f"Starting to move for file [{origin_file}]")

            # Load the origin config file defined by the user. Will fail otherwise.
            origin_storage = get_config_from_user(
                file_path=os.path.join(CONFIG_DIR, origin_file)
            )

            for origin_key, pairs in target_info.items():
                if isinstance(pairs, list):
                    log(f"We have to copy {origin_key} into {len(pairs)} destinations!")
                else:
                    log(
                        f"We have to copy {origin_key} into only one destination. " +
                        "Emulating a list of 1 element"
                    )
                    pairs = [pairs]
                pair_iteration = 0
                for pair in pairs:
                    pair_iteration += 1
                    log(f"Starting iteration {pair_iteration}")
                    target_file, target_key = pair
                    log(f"Processing {origin_file}:{origin_key} => {target_file}:{target_key}")
                    target_path = os.path.join(CONFIG_DIR, target_file)
                    log(f"Real target file name and path is [{target_path}]")

                    # Only in case that we did not already instantiate the storage
                    if target_file not in target_storage:
                        # Instantiate the storage, which already creates the file
                        target_storage[target_file] = Storage(filename=target_path)
                        log("Target storage is loaded")
                    else:
                        log("Target storage was already loaded")

                    # What do we do here?
                    #   Actually, it is just a rename of an inner dict's key,
                    #   that is behind a list. Dictionary has support for wildcards
                    #   and a get -> set would be straight forward, But the set() is meant
                    #   to apply the same value in all occurences of the wildcard,
                    #   so does not serve good here. We have to do it manually.
                    #
                    #   As usual, it is a bit overengineered (we actually know origin
                    #   and target and we could code it directly), but serves also as a
                    #   propotype for a close future "move_param" functionality.
                    #
                    # How do we do it?
                    #   1. Get origin param_names after resolving wildcards
                    #   2. Get target param_names after resolving wildcards
                    #       a. First get the parent path
                    #       b. Resolve its wildcards
                    #       c. Add the Last Key into the parent path
                    #   3. Ensure that we have the same amount of resolved param_names
                    #   4. Execute the copy get() -> set().
                    #       Until here we could abstract it as a "copy_param"
                    #   5. [Optional] verify that we have what we want where we want.
                    #   6. Remove the original keys.
                    #
                    if Storage.needs_resolving(param_name=origin_key):
                        # This means that we need to do something to ALL iterations of a list
                        # The get() and set() already support wildcards,
                        #   but the returned values change.
                        # So we have to expect here a list of param_names,
                        #   one for each resolved path.
                        origin_keys = origin_storage.resolve_wildcards(origin_key)
                        log(
                            "Origin key needs resolving. " +
                            f"Got {len(origin_keys)} resolved param_names"
                        )

                    else:
                        # So there is only one path, let's emulate that we received
                        #   several by making ita list of one
                        origin_keys = [origin_key]
                        log("Origin key does not need resolving.")

                    # Now we do the same with the target, but just for the parent path,
                    #   because this is a rename.
                    #   Later on we'll add the last key for the target to be built.
                    parent_param_name = SEPARATOR.join(target_key.split(SEPARATOR)[:-1])
                    if Storage.needs_resolving(param_name=parent_param_name):
                        # This means that we need to do something to ALL iterations of a list
                        # The get() and set() already support wildcards,
                        #   but we need to set a specific value in each occurrence.
                        # So we have to expect here a list of param_names,
                        #   one for each resolved path.
                        target_keys = target_storage[target_file].resolve_wildcards(
                            parent_param_name
                        )
                        log(
                            "Target key needs resolving. " +
                            f"Got {len(origin_keys)} resolved param_names"
                        )

                    else:
                        # So there is only one path, let's emulate that we received
                        #   several by making it a list of one
                        target_keys = [parent_param_name]
                        log("Target key does not need resolving.")

                    # Now we place back the last key to each target key,
                    #   so we know where the new value goes.
                    target_last_key = target_key.split(SEPARATOR)[-1]
                    target_keys = list(
                        map(lambda x: f"{x}{SEPARATOR}{target_last_key}", target_keys)
                    )
                    log(f"Added the Last Key into {len(target_keys)} Target paths.")

                    # And before we begin anything, let's make sure we have the
                    #   same amount of keys in the origin and in the target,
                    #   as we'll relate them by list index.
                    assert len(origin_keys) == len(target_keys)
                    log(
                        "The length of both origin and target paths " +
                        f"are the same: {len(origin_keys)}"
                    )

                    # We now copy the values respecting the position in each list.
                    #   We rely here in the deterministic position of the elements in both.
                    for index in range(0, len(origin_keys)):
                        # Get the param_names
                        origin_param_name = origin_keys[index]
                        target_param_name = target_keys[index]
                        log(
                            f"Will copy now from [{origin_param_name}] " +
                            f"to [{target_param_name}]..."
                        )

                        # Do we have to initialise the parent?
                        if target_storage[target_file].get_parent(param_name=target_param_name
                                                                  ) is None:
                            log("The target does not have the parent. Initialising")
                            target_storage[target_file].initialise_recursive(
                                param_name=target_param_name
                            )

                        # Execute the copy
                        value = origin_storage.get(param_name=origin_param_name)
                        target_storage[target_file].set(
                            param_name=target_param_name, value=copy.deepcopy(value)
                        )
                        log(
                            f"Copy of param_names in index {index} of " +
                            f"{len(origin_keys)} is done."
                        )

                    # Verify from outside that the copy is correct
                    #   To do that we get the very original path names given without processing
                    #       and compare
                    #   Yes, it has to be the same, and here lays the beauty of the
                    #       verification.
                    values_in_origin_param_names = origin_storage.get(param_name=origin_key)
                    values_in_target_param_names = target_storage[target_file].get(
                        param_name=target_key
                    )

                    log(f"Verifying original [{origin_key}] with target [{target_key}]")
                    if type(values_in_origin_param_names) == type(values_in_target_param_names):
                        log("Types are the same")
                        if isinstance(values_in_origin_param_names, (dict, list, set, tuple)):
                            log(
                                f"Original [{origin_key}] " +
                                f"({len(values_in_origin_param_names)} paths) " +
                                f"vs. target [{target_key}] " +
                                f"({len(values_in_target_param_names)} paths)"
                            )
                            for index in range(0, len(values_in_origin_param_names)):
                                assert values_in_origin_param_names[
                                    index] == values_in_target_param_names[index]
                                log(f"Values in index {index} are correct.")
                        else:
                            log("Not a dict, list, set nor tuple")
                            log(
                                f"Original [{origin_key}] " +
                                f"({values_in_origin_param_names} paths) " +
                                f"vs. target [{target_key}] " +
                                f"({values_in_target_param_names} paths)"
                            )
                            assert values_in_origin_param_names == values_in_target_param_names
                            log("Values are correct.")

                    # Reaching here means that the copy was correct.
                    #   Now the deletion part of the rename.
                    log("Proceeding to delete the original param_names")
                    # There is a thought here. If the config files are actually the same
                    #   (they are), we have open the same file as origin_storage and in
                    #   the target_storage[target_file]. As the internal behaviour of the
                    #   Storage class, it is loaded once and written also once and on
                    #   demand, so if we change the origin storage, the target storage real
                    #   file will change below the control of the target's Storage object,
                    #   and whatever new state that we have in the origin Storage real
                    #   file will be overwritten when the target's Storage object writes the
                    #   changes.
                    # Conclusion:
                    #   It would have been even easier to do all the stuff with one single
                    #   config object in this specific case, and working only with the
                    #   param_names. But we intend to make a generic solution (remember,
                    #   we're overengineering here), so:
                    #
                    #   For same files:
                    #       - We delete the origin param_names from the Target Storage.
                    #       - We close the Origin Storage without saving.
                    #   For different files:
                    #       - We delete the origin param_names from the Origin Storage.
                    #       - We save and close the Origin Storage.
                    #   In all cases:
                    #       - We save and close the Target Storage.
                    if origin_file == target_file:
                        log("Origin and Target files are the same. We delete from Target.")
                        for index in range(0, len(origin_keys)):
                            result = target_storage[target_file].delete(
                                param_name=origin_keys[index]
                            )
                            result = "Success" if result else "Failed"
                            log(f"Deleting [{origin_keys[index]}] from Target: {result}")
                        log(
                            f"{TerminalColor.GREEN_BRIGHT}Saving the file" +
                            f" {target_file}{TerminalColor.END}"
                        )
                        target_storage[target_file].write_file()
                    else:
                        log("Origin and Target files are different. We delete from Origin.")
                        for index in range(0, len(origin_keys)):
                            result = origin_storage.delete(param_name=origin_keys[index])
                            result = "Success" if result else "Failed"
                            log(f"Deleting [{origin_keys[index]}] from Origin: {result}")
                        log(
                            f"{TerminalColor.GREEN_BRIGHT}Saving the file" +
                            f" {target_file}{TerminalColor.END}"
                        )
                        target_storage[target_file].write_file()
                        log(
                            f"{TerminalColor.GREEN_BRIGHT}Saving the file" +
                            f" {origin_file}{TerminalColor.END}"
                        )
                        origin_storage.write_file()

    except Exception as e:
        print(f"{TerminalColor.RED_BRIGHT}{e}{TerminalColor.END}")
        print(full_stack())


def log(message: str):
    if DEBUG:
        message = f"{TerminalColor.BLUE}{message}{TerminalColor.END}"
        print(message)
