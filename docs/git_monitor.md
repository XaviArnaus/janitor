# 💻 Git rempositories monitor

Janitor can monitor one or more Git repositories and publish a post to a Mastodon API - like when a change in the `CHANGELOG.md` is identified.

## ⚙️ Configuration

In the config file there is the `git_monitor` section with all the possible parameters. There are 3 main ones:
- `git_monitor.file` identifies which file will handle the state for the last known version per repository
- `git_monitor.repositories` is a list of objects where each one represents all the parameters for a repository to monitor. Below we'll go deeper on this.
- `git_monitor.mastodon` is an object very similar to the main `mastodon` one that contains the Mastodon instance parameters and credentials for the account that will be used to publish the updates. This means that the there can be a different user responsible for the change updates, different from the common Janitor one.

### Repository configuration

The following is the configuration params responsible to set up one repository to monitor. I've used real life values.
```yaml
      # [String] Name of the project. Only used for displaying
      name: pyxavi
      # [String] URL of the project. Only used to link it when displaying
      url: https://github.com/XaviArnaus/pyxavi
      # [List] of Strings that will be added to the message body as a list of Tags
      tags: ["#Python", "#library"]
      # [String] URL for the repository. Can be SSH or HTTPS,
      #   but may require extra authentication in your side.
      git: git@github.com:XaviArnaus/pyxavi.git
      # [String] Where to find or to clone the repository
      path: "storage/repos/pyxavi"
      # Parameters to parse the Changelog
      changelog:
        # [String] Which file contains the changelog
        #   It is expected to be a Markdown file with:
        #   - The title of each update is the version
        #   - The body of each update is a list of changes
        # Note: Trying to support Common Changelog
        file: "CHANGELOG.md"
        # [String] Separator used to split sections
        #   defaults to "\n## "
        section_separator: "\n## "
        # [String] Regex to extract the version from the section title
        # Note: backslashes need to be doubled
        #   defaults to "\\[(v[0-9]+\\.[0-9]+\\.?[0-9]?)\\]"
        version_regex: "\\[(v[0-9]+\\.[0-9]+\\.?[0-9]?)\\]"  
```

Remember that this is a set of parameters that represent a repository. It goes set up inside `git_monitor.repositories`, which is a list. It is meant to handle several repositories, for example:

```yaml
git_monitor:
  file: "storage/git_monitor.yaml"
  repositories:
    -
      name: pyxavi
      url: https://github.com/XaviArnaus/pyxavi
      tags: ["#Python", "#library"]
      git: git@github.com:XaviArnaus/pyxavi.git
      path: "storage/repos/pyxavi"
      changelog:
        file: "CHANGELOG.md"
    -
      name: Janitor
      url: https://github.com/XaviArnaus/janitor
      tags: ["#Python", "#bot"]
      git: git@github.com:XaviArnaus/janitor.git
      path: "storage/repos/janitor"
      changelog:
        file: "CHANGELOG.md"
```

## ▶️ Run

To run it one time you can use the following commad:
```bash
bin/jan git_changes
```

### ⏱️ Scheduler set up

To set up Janitor to be run scheduled, follow the [Scheduler set up](./scheduler.md) instructions and ensure you're setting up one of the following actions:

- `git_changes`: Discovers changes in the monitored Git repositories and publishes them