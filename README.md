# Pandoc Reader

Pandoc Reader is a [Pelican][] plugin to render documents written in [Pandoc][] Markdown.

Pandoc's version of Markdown is a flavour of [Markdown][] with extensions and is explained in greater detail [here](https://pandoc.org/MANUAL.html#pandocs-markdown).

## Prerequisites

For this plugin to function you must have Pandoc installed on your system.

Please follow the [installation instructions][] to install Pandoc for your system.

## Installation

This plugin can be installed via:

```bash
python -m pip install pelican-pandoc-reader
```

## Usage

You may use this plugin whenever you wish to write your source files in Pandoc's Markdown and have them rendered as HTML 5.

This plugin expects to have metadata in YAML format at the top of every Markdown as shown below:

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

Additional command line options may be passed to Pandoc via the `PANDOC_ARGS` parameter.

```python
PANDOC_ARGS = [
  '--mathjax',
  '--toc'
]
```

Pandoc's markdown extensions may be enabled or disabled via the `PANDOC_EXTENSIONS` parameter.

```python
PANDOC_EXTENSIONS = [
  '+footnotes',
  '-pipe_tables'
]
```

More information about Pandoc's extensions can be found [here](https://pandoc.org/MANUAL.html#extensions).

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

## Credits

Originally authored by [Hinrich B. Winther](https://github.com/liob), December 2014, and subsequently enhanced by [Nandakumar Chandrasekhar](https://www.linkedin.com/in/nandakumar-chandrasekhar-a400b45b/).

[installation instructions]: https://pandoc.org/installing.html
[Markdown]: http://daringfireball.net/projects/markdown/
[Pandoc]: https://pandoc.org/
[Pelican]: http://getpelican.com
[existing issues]: https://github.com/pelican-plugins/pandoc-reader/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html
