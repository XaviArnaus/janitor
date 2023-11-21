# ⏱️ Scheduler

Most likely you intend to add the Janitor runner task into your `crontab` so that it runs periodically. The more you dig into the features of Janitor the more you will want to add in your `crontab`. That's why there's also a runner meant to organize all Janitor tasks in one place.

The Scheduler runner is intended to be the single one command added into your `crontab`, and to proxy the tasks required.

For example, one may want to check the Dynamic DNS registers hourly, monitor a Git repository daily, and collect the system metrics every 5 minutes. With the scheduler one have one single entry in the `crontab` and these tasks set up in the configuration file.

## ⚙️ Configuration

### 1. Define the schedule that should run
In the `schedules.yaml` config file there is a `schedules` parameter that accepts a list of objects representing each task to perform:
- `name` is just to describe what is this task
- `when` is a `crontab` expression defining when this task will be triggered.
- `action` is one of the possible values: "sysinfo_local" or "sysinfo_remote", at this point.

### 2. Add our scheduler into the crontab
Yes, it is all moved by the crontab in your system. Once your crontab pings this scheduler, all the rest of the set up can be done here.

1. Edit the crontab in your system
```
crontab -e
```

2. Add the following line
```
* * * * * cd /path/to/the/repository/janitor; bin/jan scheduler
```

3. Save and exit.

Now every minute our scheduler is triggered and it will perform the tasks whenever it is needed.

## Examples for Janitor tasks in the Config file

### Update Directnic's Dynamic DNS every 20 minutes

```
    - name: "Directnic DDNS"
      when: "0,20,40 * * * *"
      action: "update_ddns"
```

### Monitor the Git repositories every hour at 00

```
    - name: "Git Repositories"
      when: "0 * * * *"
      action: "git_changes"
```

### Collect and send the system metrics to a remote listener every minute

```
    - name: "SysInfo Remote"
      when: "* * * * *"
      action: "sysinfo_remote"
```

## Possible `action` values

At the moment, the following actions are allowed:
- `sysinfo_local`: Gathers the local System Info, compares with thresholds and publishes if crossed.
- `sysinfo_remote`: Gathers the local System Info and sends them to a listening server to be processed
- `update_ddns`: Discovers the current external IP and updates the Directnic Dynamic DNS registers
- `git_changes`: Discovers changes in the monitored Git repositories and publishes them