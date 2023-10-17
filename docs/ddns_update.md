# Directnic's Dynamic DNS update

Janitor also can update your [Directnic's Dynamic DNS](https://directnic.com/knowledge/#/knowledge/article/3726) setup.

## ⚙️ Configuration

In the config file, search for the `directnic_ddns.updates` list parameter and just add a line with the URL given to you in Directnic's control panel. The URL looks like something like:

```
https://directnic.com/dns/gateway/123456abcdef678912346bdf53bd53bbee890dbf0227053ea877e0382a/?data=87.112.34.56
```

The IP address at the end is meant to be replaced with your current external IP, and this *Janitor* will do for you, so we simply remove the IP at the end.
Therefor, edit the configuration so that the `directcni_ddns` section looks like something like the following:

```
# Directnic's Dynamic DNS updater
directnic_ddns:
  # [String] Where to store it
  file: "storage/directnic_ddns.yaml"
  # [List] Items to update
  updates:
    - https://directnic.com/dns/gateway/123456abcdef678912346bdf53bd53bbee890dbf0227053ea877e0382a/?data=
```

You can add all update links that you need, the bot will use them all adding your external IP.

## ▶️ Run

To run it one time you can use the following commad:
```bash
bin/jan update_dns
```

### ⏱️ Scheduler set up

To set up Janitor to be run scheduled, follow the [Scheduler set up](./scheduler.md) instructions and ensure you're setting up one of the following actions:

- `update_ddns`: Discovers the current external IP and updates the Directnic Dynamic DNS registers