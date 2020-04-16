# pandoc_reader

A [Pandoc] [Markdown] reader plugin for the [Pelican] static site generator.

Pandoc's version of Markdown is a flavour of Markdown with extensions and is explained in greater detail [here](https://pandoc.org/MANUAL.html#pandocs-markdown).

## Requirements

For this plugin to function you must have Pandoc installed on your system.

Please follow the instructions [here](https://pandoc.org/installing.html) to install Pandoc for your system.

## Installation

For instructions on installing Pelican plugins please see the [Pelican Plugins](https://github.com/getpelican/pelican-plugins/blob/master/Readme.rst) documentation.

## Configuration

The plugin expects to have metadata at the top of every Markdown file in YAML format like so:

```yaml
---
title: <post-title>
author: <author-name>
---
```

or

```yaml
...
title: <post-title>
author: <author-name>
...
```

Failing to provide this metadata will cause the plugin to fail.

Additional command line parameters can be passed to Pandoc via the `PANDOC_ARGS` parameter.

```python
PANDOC_ARGS = [
  '--mathjax',
  '--toc',
  '--toc-depth=2',
  '--number-sections',
  '--standalone'
]
```

Pandoc's markdown extensions can be enabled or disabled via the `PANDOC_EXTENSIONS` parameter.

```python
PANDOC_EXTENSIONS = [
  '+hard_line_breaks',
  '-citations'
]
```

More information about Pandoc's extensions can be found [here](https://pandoc.org/MANUAL.html#extensions).

## Contributing

To contribute to this project follow the steps below:

1. Fork this project on GitHub.
1. Create your feature branch.

    ```bash
    git checkout -b my-new-feature
    ```

1. Commit your changes.

    ```bash
    git commit -am 'Add some feature'
    ```

1. Push to the branch.

    ```bash
    git push origin my-new-feature
    ```

1. Create new Pull Request on GitHub.

[Markdown]: http://daringfireball.net/projects/markdown/
[Pandoc]: https://pandoc.org/
[Pelican]: http://getpelican.com
