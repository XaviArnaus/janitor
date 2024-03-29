# Upgrading Guide

This document describes the steps to overcome the breaking changes between versions while upgrading.
Please keep in mind that steps are sequential, and to migrate from a 2 versions old status to the latest one, one must follow all steps individually and sequentially from older to newer, in most of the cases.

This document lists the upgrading steps from the most newer version to the oldest version.

## From version `v0.5.1` to `v0.5.3`

- There is a major change in the config structure for the `Logger` module, where the block moves from a flat object to a nested object. See [the note in the dependency `pyxavi` package](https://github.com/XaviArnaus/pyxavi/blob/main/docs/logger.md). The `Logger` module is able to load old and new structure, so no danger here, but the `main.yaml.dist` is updated and the config migration tool should be able to bring the config up-to-date.
- The lock file has been updated. A `poetry lock` and `make init` is needed.

0. [optional] Backup your user data in any external location.
    - Config files (by default in `config/*.yaml`)
    - Client secret file (by default `client.secret`)
    - User secret file (by default `user.secret`)
    - Storages (by default, everything inside `storage/`)
1. Fetch the changes from the original repository
    ```bash
    git fetch
    ```
2. Checkout to the version `0.5.3`
    ```bash
    git checkout v0.5.3
    ```
3. Migrate the `git_config.yaml` config file to the new structure. Do it manually now or use the tool like the following:
    ```bash
    bin/jan migrate_config v0.5.3
    ```
4. Most likely your *Poetry* would complain about the lock file being old. Reset the lock file with the following command
    ```bash
    poetry lock 
    ```
5. Install the dependencies
    ```bash
    make init 
    ```

## From version `v0.5.1` to `v0.5.2`

- There is a minor change in the config structure, where the internal parameter `git_monitor.repositories.#.changelog` got renamed to `git_monitor.repositories.#.params`. The config migration tool should be able to bring the config up-to-date.
- The lock file has been updated. A `poetry lock` and `make init` is needed.

0. [optional] Backup your user data in any external location.
    - Config files (by default in `config/*.yaml`)
    - Client secret file (by default `client.secret`)
    - User secret file (by default `user.secret`)
    - Storages (by default, everything inside `storage/`)
1. Fetch the changes from the original repository
    ```bash
    git fetch
    ```
2. Checkout to the version `0.5.2`
    ```bash
    git checkout v0.5.2
    ```
3. Migrate the `git_config.yaml` config file to the new structure. Do it manually now or use the tool like the following:
    ```bash
    bin/jan migrate_config v0.5.2
    ```
4. Most likely your *Poetry* would complain about the lock file being old. Reset the lock file with the following command
    ```bash
    poetry lock 
    ```
5. Install the dependencies
    ```bash
    make init 
    ```

## From version `v0.5.0` to `v0.5.1`

- There are no significant changes in the configuration files.
- There are changes in the dependencies.

0. [optional] Backup your user data in any external location.
    - Config files (by default in `config/*.yaml`)
    - Client secret file (by default `client.secret`)
    - User secret file (by default `user.secret`)
    - Storages (by default, everything inside `storage/`)
1. Fetch the changes from the original repository
    ```bash
    git fetch
    ```
2. Checkout to the version `0.5.1`
    ```bash
    git checkout v0.5.1
    ```
3. Most likely your *Poetry* would complain about the lock file being old. Reset the lock file with the following command
    ```bash
    poetry lock 
    ```
4. Install the dependencies
    ```bash
    make init 
    ```


## From version `v0.4.0` to `v0.5.0`

There is a major change introduced in this version regarding the structure of the configuration files. Now there is not a single big configuration file but a separated set of configuration files per module or functionality.
There is also a tool delivered to assist in the process of migrating from the old single file to the multiple files. The only drawback is that the tool won't migrate also the comments on the config file, so while the configuration should work out of the box, you will loose the explanations in the new config files. You can always perform the migration manually, by generating the new config files from the distributed examples and then move the parameter values from the old config file to the new one.

0. [optional] Backup your user data in any external location.
    - Config file (by default `config.yaml`)
    - Client secret file (by default `client.secret`)
    - User secret file (by default `user.secret`)
    - Storages (by default, everything inside `storage/`)
1. Fetch the changes from the original repository
    ```bash
    git fetch
    ```
2. Checkout to the version `0.5.0`
    ```bash
    git checkout v0.5.0
    ```
3. Migrate the single config file to the multiple config files. Do it manually now or use the tool like the following:
    ```bash
    bin/jan migrate_config v0.5.0
    ```
4. Install the dependencies again
    ```bash
    make init 
    ```

    Could be that *Poetry* complains about the lock file being old. Reset the lock file with the following command and try again
    ```bash
    poetry lock 
    make init
    ```

At this point you should have a working `0.5.0` version.


## From older versions to version `0.4.0`

There are no explicit instructions for migrating from versions previous to `0.4.0`.
Generically, you would like to move the version `0.4.0` manually and then migrate to a newer one observing every individual step.

To bring your instance to version `0.4.0`:
1. Backup your user data in any external location.
    - Config file (by default `config.yaml`)
    - Client secret file (by default `client.secret`)
    - User secret file (by default `user.secret`)
    - Storages (by default, everything inside `storage/`)
2. Fetch the changes from the original repository
    ```bash
    git fetch
    ```
3. Checkout to the version `0.4.0`
    ```bash
    git checkout v0.4.0
    ```

* The Client and User secret files and the storage files did not change. You should be good to keep them where they where.
* The shape of the config file did not change dramatically, but there are some major changes that you must do manually.
    0. Be sure you have your backup of your old configuration file `config.yaml`
    1. Delete the configuration file you had in the root of the project folder.
        ```bash
        rm config.yaml
        ```
    2. Create a clean new configuration file from the distributed one
        ```bash
        cp config.yaml.dist config.yaml
        ```
    3. Edit the new configuration file
        ```bash
        nano config.yaml
        ```
    4. Manually move the values of the parameters in the old configuration backup file to this new configuration file. The parameters did not change, but they were mostly moved to another location.
    5. Save and exit.

4. Install the dependencies again
    ```bash
    make init 
    ```

    Could be that *Poetry* complains about the lock file being old. Reset the lock file with the following command and try again
    ```bash
    poetry lock 
    make init
    ```

At this point you should have a working `0.4.0` version. To upgrade to a newer version please see the appropiate section in this document.