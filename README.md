# Janitor

Bot meant to perform maintenance tasks in a crontab fashion and to report via a Mastodon-like API.
The idea is to serve as a framework to keep adding tasks and have this bot as a companion, caring about the system for you.

Current features:
- Collect system metrics and compare them with given thresholds, publishing an alert in case these get grossed.
- Sending the system metrics to another Janitor instance runnining in another host.
- Listening for Janitor metrics cross the network.
- Listening for arbitrary messages to be published to the set up Mastodon-like API, behaving as a generic publisher
- Discovering the current external IP and updating the set up Directnic's Dynamic DNS if needed

[![Tests](https://github.com/XaviArnaus/janitor/actions/workflows/tests.yml/badge.svg)](https://github.com/XaviArnaus/janitor/actions/workflows/tests.yml)
[![yapf](https://github.com/XaviArnaus/janitor/actions/workflows/yapf.yml/badge.svg)](https://github.com/XaviArnaus/janitor/actions/workflows/yapf.yml)
[![flake8](https://github.com/XaviArnaus/janitor/actions/workflows/flake8.yml/badge.svg)](https://github.com/XaviArnaus/janitor/actions/workflows/flake8.yml)
---

## ⭐️ Requirements
- Python 3.9
- Poetry

## ⭐️ Installation

### 0. Install Poetry
Following [the official docs](https://python-poetry.org/docs/#installation), or skip this step if you already have it installed
```
curl -sSL https://install.python-poetry.org | python3 -
```

### 1. Clone the repository
```
git clone git@github.com:XaviArnaus/janitor.git
```

### 2. Move yourself to the directory
```
cd janitor
```

### 3. Settle your config from the example
```
cp config.yaml.dist config.yaml
```

### 4. Edit the new config file
```
nano config.yaml
```

### 5. Change the parameters that make sense to your configuration
Depending on how you'll want this bot instance to behave, there are some mandatory parameters to set up. The config file is quite well documented. Later on this document there are sections explaining which modes can be set, what are they and how to set them up. 

Check the section below to get some tips on which configuration would fit for you.

### 6. Install all Python dependencies
```
make init
```

### 7. Create the app
For the publishing into the Mastodon-like servers we need first to log in and set up the credential files. This is only needed for the "single mode" and the "listener mode", as they are the only ones that publish to the Mastodon API.
```
make create_app
```

And now the app is ready to run!

## ⭐️ Features and configuration

These are the current features and how to set them up.

### 🔍 System metrics collection and alerting

Janitor was initially designed as a bot that collects system metrics periodically, compares the values to a given set of thresholds, and publishes a message to a Mastodon-like API in case they are crossed.

- Read the [System metrics collection and alerting](./docs/sysinfo.md) page

### 🔃 Directnic's Dynamic DNS Updater

Janitor can discover the current external IP and monitor for changes, and then update Directnic's Dynaminc DNS registers.

- Read the [Directnic's Dynamic DNS Updater](./docs/ddns_update.md) page

### 💻 Git repositories monitor

Janitor can monitor changes to CHANGELOG files from given Git repositories and alert via a Mastodon-like API about the changes. This is a gret tool to automatically announce code changes and also to monitor external repositories to be on top of updates to fetch.

- Read the [Git rempositories monitor](./docs/git_monitor.md) page

### ⏱️ Scheduler

Once Janitor can perform multiple tasks, makes sense to proxy the periodicity by having a single Scheduler that sets up the diverse tasks. The Scheduler will read the `crontab` fashion time setup from the configuration file and trigger the defined tasks accordingly.

- Read the [Scheduler](./docs/scheduler.md) page