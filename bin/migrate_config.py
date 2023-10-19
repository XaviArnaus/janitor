import os
from definitions import ROOT_DIR, CONFIG_DIR
from pyxavi.terminal_color import TerminalColor
from pyxavi.storage import Storage
from string import Template

DEFAULT_CONFIG_FILE_NAME = "config.yaml"
REQUEST_CONFIG_NAME = "Origin config file [$path] (press ENTER to accept default):"

# This represents old location to new location
MAP_OLD_TO_NEW = {
    "app.service": ("main.yaml", "app.service"),
    "app.run_control": ("main.yaml", "app.run_control"),
    "app.schedules": ("schedules.yaml", "schedules"),
    "logger": ("main.yaml", "logger"),
    "queue_storage": ("main.yaml", "queue_storage"),
    "publisher": ("main.yaml", "publisher"),
    "system_info": ("sysinfo.yaml", "system_info"),
    "formatting.system_info.report_item_names_map": ("sysinfo.yaml", "system_info.formatting.report_item_names_map"),
    "formatting.system_info.human_readable": ("sysinfo.yaml", "system_info.formatting.human_readable"),
    "formatting.system_info.human_readable_exceptions": ("sysinfo.yaml", "system_info.formatting.human_readable_exceptions"),
    "directnic_ddns": ("directnic_ddns.yaml", "directnic_ddns"),
    "git_monitor": ("git_monitor.yaml", "git_monitor"),
    "mastodon": ("mastodon.yaml", "mastodon"),
}

def run():
    # Get the origin
    config_path = input(Template(REQUEST_CONFIG_NAME).substitute(
        path=os.path.join(ROOT_DIR, DEFAULT_CONFIG_FILE_NAME)
    ))
    if config_path == "":
        config_path = os.path.join(ROOT_DIR, DEFAULT_CONFIG_FILE_NAME)

    # Load the origin config file. Will fail otherwise.
    origin_file = Storage(config_path)

    try:
        # Ensure that the target CONFIG_DIR exists, otherwise create it.
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            print(f"Created the directory [{CONFIG_DIR}]")

        # Create the target files and keep them in memory
        target_storage = {}
        for origin_key, pair in MAP_OLD_TO_NEW.items():
            target_file, target_key = pair
            target_path = os.path.join(CONFIG_DIR, target_file)

            # Only in case that we did not already instantiate the storage
            if target_file not in target_storage:
                # Ensure that the target file does not already exist
                if os.path.exists(target_path):
                    raise RuntimeError(f"The target config file [{target_path}] already exists. Should not.")

                # Instantiate the storage, which already creates the file
                target_storage[target_file] = Storage(filename=target_path)

            # Bring the parameters from the old config
            origin_value = origin_file.get(origin_key)

            # Could be that the target's parent objects were already created.
            #   Check if they exist to avoid overwritting anything.
            #   Still, if they don't exists, just go on creating the objects.
            if target_key.find(".") > 0:
                target_key_pieces = target_key.split(".")
            else:
                target_key_pieces = [target_key]
            parents = ""
            for piece in target_key_pieces:
                # Get current target value
                current_target_value = target_storage[target_file].get(f"{parents}{piece}", None)

                # So if this object does not exist we have to create something.
                if current_target_value is None:
                    # Wait, are we actually the final object, suposed to hold ve target value?
                    if piece == target_key_pieces[-1]:
                        # Ok, so this is it, let's set the original value here
                        target_storage[target_file].set(f"{parents}{piece}", origin_value)
                    else:
                        # No, it's not. We just set that this is an object and keep on going
                        target_storage[target_file].set(f"{parents}{piece}", {})

                # Update the parents path to the next child object
                parents = f"{parents}{piece}."
            
            # At this point, the value for the old parameter and the value for the new parameter should match.
            target_value = target_storage[target_file].get(target_key, None)
            if origin_value != target_value:
                raise ValueError(f"They copy from key {origin_key} into {target_file}:{target_key} was unsuccessful")
        
        # At this point we only need to write what we hold in memory
        for file, storage_object in target_storage.items():
            storage_object.write_file()
            print(f"{TerminalColor.GREEN_BRIGHT}Config file {file} has been writen{TerminalColor.GREEN_BRIGHT}")
    except Exception as e:
        print(f"{TerminalColor.RED_BRIGHT}{e}{TerminalColor.END}")





