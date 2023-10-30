import os
from definitions import ROOT_DIR, CONFIG_DIR
from pyxavi.terminal_color import TerminalColor
from pyxavi.storage import Storage
from string import Template
import copy

REQUEST_CONFIG_NAME = "Origin config file [$path] (press ENTER to accept default):"
DEBUG = False

# This represents old location to new location
# When some internals are moved, the siblings need to be pointed individually
# In this case, this is only a very minimal config edition
MAP_OLD_TO_NEW = {
    "git_monitor.yaml": {
        "git_monitor.repositories.#.changelog": (
            "git_monitor.yaml", "git_monitor.repositories.#.params"
        ),
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
                        # Ensure that the target file does not already exist
                        if os.path.exists(target_path):
                            raise RuntimeError(
                                f"The target config file [{target_path}] already exists. " +
                                "Should not."
                            )

                        # Instantiate the storage, which already creates the file
                        target_storage[target_file] = Storage(filename=target_path)
                        log("Target storage is loaded")
                    else:
                        log("Target storage was already loaded")

                    # Bring the parameters from the old config
                    origin_value = copy.deepcopy(origin_storage.get(origin_key))
                    log(
                        f"Origin value for {origin_key} is loaded. We have a {type(origin_value)}"
                    )

                    # Could be that the target's parent objects were already created.
                    #   Check if they exist to avoid overwritting anything.
                    #   Still, if they don't exists, just go on creating the objects.
                    if target_key.find(".") > 0:
                        target_key_pieces = target_key.split(".")
                    else:
                        target_key_pieces = [target_key]
                    log(
                        f"Target key {target_key} converted to pieces. " +
                        f"We have {len(target_key_pieces)} pieces."
                    )
                    parents = ""
                    for piece in target_key_pieces:
                        log(f"Starting with piece [{piece}]")
                        # Get current target value
                        current_target_value = target_storage[target_file].get(
                            f"{parents}{piece}", None
                        )
                        is_none = " " if current_target_value is None else " NOT "
                        log(f"The target piece [{parents}{piece}] is{is_none}None")

                        # So if this object does not exist we have to create something.
                        if current_target_value is None:
                            # Are we actually the final object, suposed to hold ve target value?
                            if piece == target_key_pieces[-1]:
                                log(
                                    f"The target piece [{piece}] is the last on the target key "
                                    + f"[{target_key}]"
                                )
                                # Ok, so this is it, let's set the original value here
                                target_storage[target_file].set(
                                    f"{parents}{piece}", origin_value
                                )
                                log(
                                    "The origin_value has been SET at target_storage[target_file] "
                                    + "in the key {parents}{piece}"
                                )
                            else:
                                # No, it's not. We just set that this is an object and keep on going
                                target_storage[target_file].set(f"{parents}{piece}", {})
                                log(
                                    f"As the [{parents}{piece}] was not the last one and None, "
                                    + "only an empty dict is set here"
                                )
                        else:
                            # So there is anything here already.
                            # We only write if it's actually the final object
                            if piece == target_key_pieces[-1]:
                                log(
                                    f"The target piece [{piece}] is the last on the target key "
                                    + f"[{target_key}]"
                                )
                                # Let's merge what we have here with what we bring.
                                # The new data has preference
                                new_value = {**current_target_value, **origin_value}
                                target_storage[target_file].set(f"{parents}{piece}", new_value)
                                log(
                                    "The origin_value has been MERGED at " +
                                    f"target_storage[target_file] in the key {parents}{piece}"
                                )

                        # Update the parents path to the next child object
                        parents = f"{parents}{piece}."

                    # At this point, the value for the old parameter
                    #   and the value for the new parameter should match.
                    # ! THIS DOES NOT WORK IF WE DID MERGING!
                    # That's why we check only if the origin key/values exist in the
                    #   target space if it's an object, or the value only otherwise
                    target_value = target_storage[target_file].get(target_key, None)
                    if isinstance(origin_value, dict):
                        log(f"Verifying that we copied the dict {origin_key} into {target_key}")
                        for o_param, o_value in origin_value.items():
                            log(f"Checking {o_param} key in destination, and comparing values")
                            if o_param not in target_value or target_value[o_param] != o_value:
                                raise ValueError(
                                    f"They copy from key {origin_key} into"
                                    f" {target_file}:{target_key} was unsuccessful,"
                                    f" missing {o_param} or it does not equals to {o_value}"
                                )
                    elif origin_value != target_value:
                        log(
                            f"Verifying that we copied the value {origin_key}" +
                            f" into {target_key} for a non-dict"
                        )
                        raise ValueError(
                            f"They copy from key {origin_key} into"
                            f" {target_file}:{target_key} was unsuccessful"
                        )

        # At this point we only need to write what we hold in memory
        for file, storage_object in target_storage.items():
            storage_object.write_file()
            print(
                f"{TerminalColor.GREEN_BRIGHT}Config file {file}"
                f" has been writen{TerminalColor.GREEN_BRIGHT}"
            )
    except Exception as e:
        print(f"{TerminalColor.RED_BRIGHT}{e}{TerminalColor.END}")


def log(message: str):
    if DEBUG:
        message = f"{TerminalColor.BLUE}{message}{TerminalColor.END}"
        print(message)
