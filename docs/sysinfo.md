# System metrics collection and alerting

As the initial Janitor's goal, it is designed to collect system metrics in a periodical fashion, compare them to a given set of thresholds, and publish an alert to a Mastodon-like API in case they are crossed.

## 3 run modes

### 1️⃣ - *Local* instance

This a typical setup for most of the cases, where there is only one machine running Janitor. Once set up, it will:

1. Check the metrics
2. Compare the values to the defined thresholds
3. If thresholds are crossed,
    1. Builds an alerting message based on the given configuration
    2. Publishes it to the Mastodon-like API account given in the config file.

This mode does not make use of the Janitor's client-server functionality.

### 2️⃣ - *Remote* instance

This is a setup where a host is configured to listen for messages (see the 3rd mode *Listener* below) and one or more other hosts are collecting and sending the metrics to the listener. Once set up, it will:

1. Check the metrics
2. Send the metrics to the host defined in the configuration file

This mode does not analyse the metrics per host. Besides that, all metrics are centrally analysed in the listener host.

### 3️⃣ - *Listener* instance

This is the setup that comes together with the *Remote* instance above, where this host is configured to receive all metrics from the *Remote* instances. Once set up, it will:

1. Listen for incomming HTTP messages through the IP and host defined in the configuration file
2. Once a message is received,
    1. Compare the values to the defined thresholds
    2. If thresholds are crossed,
        1. Builds an alerting message based on the given configuration
        2. Publishes it to the Mastodon-like API account given in the config file.

#### Accepting also arbitrary messages

This *Listener* mode actually brings up 2 endpoints: one to receive metrics as explained above and another one `message` to receive arbitrary `POST` messages.

## ⚙️ Configuration

The set up is made through the configuration file. The parameters for every mode depends on which functionality each makes use. This is:

- 1️⃣ - *Local* instance:
    - General Janitor set up
    - Thresholds set up
    - Publish formatting set up
    - Mastodon API set up

- 2️⃣ - *Remote* instance:
    - General Janitor set up
    - Remote URL set up

- 3️⃣ - *Listener* instance
    - General Janitor set up
    - Thresholds set up
    - Publish formatting set up
    - Mastodon API set up
    - Listener set up

### General Janitor set up

- `app.run_control.dry_run`: Set it to `False` when you're ready to start publishing. This lets you run the bot without an actual publishing. It also relates to the ability to send data away for the *Remote* mode, so with `False` it won't send anything.

### Thresholds set up

The configuration file comes with a set of default values that just works. You can fine tune them through the following parameters:

- `system_info.thresholds.[metric].value`: This is the value that will be compared to in a *greater than* fashion.
- `system_info.thresholds.[metric].message_type`: This is the type of the message when sending. The idea is that every type means a severity and will be formatted accordingly.

### Publish Formatting set up

Once again, the configuration file comes with a set of default values that just works. You can fine tune them through the following parameters:

- `formatting.system_info.report_item_names_map.[metric]`: These are the labels that will be used to display every metric.
- `formatting.system_info.human_readable`: Setting it to `True`, it makes the values round and to a human scale when displaying.
- `formatting.system_info.human_readable_exceptions`: If the previous parameter is `True`, we can add here exceptions where the metric value won't be touched.

### Mastodon API set up

Here is where we have the major configuration. This whole `mastodon` parameter set is shared with all other Janitor functionalities that publish through the Mastodon-like API.

At the moment, Janitor is able to publish in the following APIs:
- Mastodon
- Pleroma / Akkoma
- Firefish / Calckey

Let's go through the parameters:

- `mastodon.app_name`: Name of the application. It is used when generating the secrets and to register the app into the instance for the Mastodon API
- `mastodon.api_base_url`: The URL (with protocol) where we connect to deliver the posts to publish.
- `mastodon.instance_type`: The type of instance we connect to. The possible values are:
    - `"mastodon"` for Mastodon
    - `"pleroma"` for Pleroma / Akkoma
    - `"firefish"` for Firefish / Calckey
- `mastodon.credentials.client_file`: When creating the app (see below) Janitor generates a file in the root of the project with the Client credentials, named according to this parameter.
- `mastodon.credentials.user_file`: When logging into the Mastodon instance for the first time, Janitor generates a file in the root of the project with the User credentials, named according to this parameter.
- `mastodon.credentials.user.email`: The email to be used for logging into the Mastodon instance for the first time.
    - This field is ignored by the `firefish` instance type.
    - After the initial login where the `mastodon.credentials.user_file` is written, this email information is not needed anymore here.
- `mastodon.credentials.user.password`: The password to be used for logging into the Mastodon instance for the first time.
    - This field is meant to store the *user token* for the `firefish` instance type. This means that you first need to generate a token in Firefish and then paste it as a value of this password paramenter.
    - After the initial login where the `mastodon.credentials.user_file` is written, this password information is not needed anymore here.
- `mastodon.status_post.max_length`: This is the maximum length for the status to be published. Any content longer that this will be sliced.
- `mastodon.status_post.content_type`: The content type to publish to the *Pleroma* / *Akkoma* instances. *Mastodon* and *Firefish* instances will ignore this setting. The possible values are:
    - `"text/plain"`: Common plain text
    - `"text/markdown"`: Markdown text
    - `"text/html"`: HTML text
    - `"text/bbcode"`: BBcode text
- `mastodon.status_post.visibility`: The visibility of the status published. The possible values are:
    - `"direct"`: post will be visible only to mentioned users. For firefish this will be mapped to `specified`.
    - `"private"`: post will be visible only to followers. For firefish this will be mapped to `followers`.
    - `"unlisted"`: post will be public but not appear on the public timeline. For firefish this is not mapped.
    - `"public"`: post will be public. For firefish this will be mapped to `public`.
    - There is no mapping for firefish's `home`.
- `mastodon.status_post.username_to_dm`: This is the username in the mastodon form `@username` that will be added in the status post so that it gets mentioned by it.

### Remote URL set up

- `app.service.remote_url`: URL where to send the collected metrics to.

### Listener set up

- `app.service.listen.host`: From which host do we listen to. With `127.0.0.1` Janitor will listen only from localhost. With `0.0.0.0` listens from all IPs that reach out.
- `app.service.listen.port`: Which port to listen to.
- `app.service.listen.debug`: Defaults to `False`, and defines if the internal server is spawn in debug mode, which allows code changes without having to restart the server and includes a bit more extensive logging.

## ▶️ Run

Once the configuration is set up, run the command line tool with the appropiate command, depending on the mode you want:

### 1️⃣ - *Local* instance

```bash
bin/jan sys_info local
```

If the parameter `logger.loglevel` is set to `20` (INFO), this is the usual output:
```
[2023-03-17 08:24:57,891] INFO     janitor Init Local Runner
[2023-03-17 08:24:57,891] INFO     janitor Run local app
[2023-03-17 08:24:58,893] INFO     janitor No issues found. Ending here.
```

### 2️⃣ - *Remote* instance

```bash
bin/jan sys_info remote
```

If the parameter `logger.loglevel` is set to `20` (INFO), this is the usual output:
```
[2023-03-17 08:24:57,891] INFO     janitor Init Remote Runner
[2023-03-17 08:24:57,891] INFO     janitor Run remote app
[2023-03-17 08:24:58,893] INFO     janitor Sending sys_data away
```

### 3️⃣ - *Listener* instance

#### Starting the listener

```bash
bin/jan listener start
```

If the listener is not yet started, it will answer with something like:
```
Listener is running with the PID: 76328
```

If the listener was already running, it will answer with something like:
```
Listener already running with PID: 76328. Skipping
```

#### Stopping the listener

```bash
bin/jan listener stop
```

If the listener was running, it will answer with something like:
```
Stopping listener under PID: 76328
Listener is NOT running
```

If the listener is not yet started, it will answer with something like:
```
Listener is NOT running
```

#### Requesting for the status of the listener

```bash
bin/jan listener status
```

If the listener was running, it will answer with something like:
```
Listener is running with the PID: 76984
```

If the listener is not yet started, it will answer with something like:
```
Listener is NOT running
```

#### Arbitrary messages

As mentioned above, once the listener is started it also accepts receiving arbitrary messages that will get published. It has an endpoint `message` that accepts a `POST` message with the following fields:
- `hostname`: Mandatory. Defines who sends the message.
- `message`: Mandatory. The message itself to publish
- `summary`: Optional. If present, the published post will have the `summary` as Spoiler Text, having this "show more" button.
- `message_type`: Optional. If present it will present an emoji according to the type of message (see the table below). If `summary` is also present, the emoji will appear in the beginning of the Spoiler Text, otherwise it will appear in the beginning of the main text.

| message_type | Emoji |
|---|---|
| `none` | (none) |
| `info` | ℹ️ |
| `warning` | ⚠️ |
| `error` | 🔥 |
| `alarm` | 🚨 |

To send a minimal message from a linux shell you could run something like:
```bash
curl -X POST -d "hostname=MyHostname&message=This+is+a+test+message" http://server:5000/message
```

You can also enrich it a bit more, like:
```bash
curl -X POST -d "hostname=MyHostname&message=This+is+the+deep+dump+of+the+incident&summary=We+had+an+warning!&message_type=warning" http://server:5000/message
```

Janitor also has also a command in the CLI tool to send test messages just to ensure that communication (and the publishing configuration in the listener) is working:

```bash
bin/jan test_message
```

## ⏱️ Scheduler set up

To set up Janitor to be run scheduled, follow the [Scheduler set up](./scheduler.md) instructions and ensure you're setting up one of the following actions:

- `sysinfo_local`: Gathers the local System Info, compares with thresholds and publishes if crossed.
- `sysinfo_remote`: Gathers the local System Info and sends them to a listening server to be processed

## Use cases examples
As explained in the section above [Different run modes as per use case](#different-run-modes-as-per-use-case) we can run this bot in a variety of ways depending on the behaviour we want to achieve. This section presents some useful examples to start using it straight away

### Local mode
Clone the repo, adjust the configuration and install the dependencies [as explained above](#installation). Be sure that your schedule item points the action to `run_local`. Then edit your crontab [as explained](#2-add-our-scheduler-into-the-crontab) to set up the scheduler.

### Client-Server mode
In both server and client machines, clone the repo, adjust the configuration and install the dependencies [as explained above](#installation). Be sure that you set up the host and port to listen. 

#### In the Server machine
Run the `make listen` command [as explained](#host-that-listens).

#### In the Client machine for a periodic check of system metrics
Be sure that your schedule item points the action to `run_remote`. Then edit your crontab [as explained](#2-add-our-scheduler-into-the-crontab) to set up the scheduler.

#### In the client machine for an arbitrary message send
Here the things are a bit more interesting. You have most likely a script, maybe a bash script, that performs any particular job. You want to capture the output and to send the execution report (or not) to the listener to be published.

As an example, take a look at this "auto `git pull`" script:
```
#! /bin/bash

urlencode() {
  python3 -c 'import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1], sys.argv[2]))' \
    "$1" "$urlencode_safe"
}

cd /var/www/folder/of-my-project
OUTPUT=$(git pull 2>&1)
ret=$?
if [ $ret -ne 0 ]; then
	encoded=$(urlencode "$OUTPUT")
        curl -X POST -d "hostname=Auto+Git+Pull+at+myhostname&message=$encoded&message_type=error" http://server:5000/message
else
	if [[ "$OUTPUT" != "Already up to date." ]]; then
		encoded=$(urlencode "$OUTPUT")
        	curl -X POST -d "hostname=Auto+Git+Pull+at+myhostname&message=👍+Done:+$encoded&message_type=info" http://server:5000/message
	fi
fi
```

This script just executes a normal `git pull` from which we capture the output and the returning code of it. Depending on the returning code we know if it worked or not, and then we send a message to the listener with an url-encoded text and a defined Message Type that will lead to a related emoji.
At the end of the day we only perform a POST CURL request to our listener with a defined set of parameters that will be posted in the Mastodon-API.


## How does it look like
In the following screenshot we have 3 examples of posts published into an Akkoma instance:
![Screenshot of some alerts in an Akkoma instance](./docs/akkoma-screenshot.png "Screenshot of some alerts in an Akkoma instance")

#### Message 1: Error
This is an arbitrary message sent from the bash script above. It actually happened that [GitHub changed the RSA keys](https://github.blog/2023-03-23-we-updated-our-rsa-ssh-host-key/) and the bot captured the failure.

#### Message 2: Info
This is another arbitrary message sent from the same bash script above. It only communicates that a `git pull` that carried on some changes was done successfully.

#### Message 3: Warning
This is an example of a periodic check of system metrics that identified an excess of CPU usage, publishing the current metrics for further analysis.