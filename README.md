# Pandoc Reader

Pandoc Reader is a [Pelican](http://getpelican.com) plugin to convert documents written in [Pandoc](https://pandoc.org/) Markdown to HTML 5.

[Pandoc's Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown) is a flavour of [Markdown](http://daringfireball.net/projects/markdown/) with extensions.

## Prerequisites

For this plugin to function you must have Pandoc and the [PyYAML](https://pypi.org/project/PyYAML/) python package installed on your system.

Please follow the [installation instructions](https://pandoc.org/installing.html) to install Pandoc.

To install PyYAML execute the following command using [pip](https://pip.pypa.io/en/stable/installing/):

```bash
pip install PyYAML==5.3.1
```

## Installation

The plugin may be installed using pip:

```bash
python -m pip install pelican-pandoc-reader
```

## Usage

This plugin converts Pandoc's Markdown into HTML 5. Conversion to formats other than HTML 5 will not be supported.

### Specifying Pandoc Options

The plugin supports two methods to pass options to Pandoc and are **mutually exclusive**. These methods are described in the sections below.

#### Method One

You may configure two constants in your `pelicanconf.py` file namely:

* `PANDOC_ARGS`
* `PANDOC_EXTENSIONS`

In the `PANDOC_ARGS` parameter you may specify any arguments supported by Pandoc.

```python
PANDOC_ARGS = [
  '--mathjax',
  '--toc'
]
```

**Note: We do not recommend specifying `--standalone` or `--self-contained` as this would  conflict with you theme's template files.**

In the `PANDOC_EXTENSIONS` parameter you may enable/disable any number of [Pandoc extensions](https://pandoc.org/MANUAL.html#extensions).

```python
PANDOC_EXTENSIONS = [
  '+footnotes',  # Enabled extension
  '-pipe_tables' # Disabled extension
]
```

#### Method Two

The second method is to specify a path to a YAML file, with all your preferences, by setting the `PANDOC_DEFAULT_FILES` constant in your `pelicanconf.py` file.

```python
PANDOC_DEFAULT_FILES = [
  '<path/to/default/file>'
]
```

Using a default file has the added benefit of allowing you to use other markdown flavors supported by Pandoc such as [CommonMark](https://commonmark.org/) and [GitHub-Flavored Markdown](https://docs.github.com/en/free-pro-team@latest/github/writing-on-github).

The format of this file is described [here](https://pandoc.org/MANUAL.html#default-files).

**Note: If `--standalone` or `--self-contained` are set to `true` you will get an error message.**

### Specifying File Metadata

The plugin expects all markdown files to start with a YAML block as shown below.

```yaml
---
title: <post-title>
author: <author-name>
data: <date>
---
```

or

```yaml
...
title: <post-title>
author: <author-name>
date: <date>
...
```

**Note: Specifying the file metadata in the format above does not comply with Pelican's format. If you wish to stop using this plugin and switch back to Pelican's native Markdown you may have to change the metadata format.**

More information about specifying file metadata is available [here](https://docs.getpelican.com/en/stable/content.html#file-metadata).

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues](https://github.com/pelican-plugins/pandoc-reader/issues).

To start contributing to this plugin, review the [Contributing to Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation, beginning with the **Contributing Code** section.

## Credits

Originally authored by [Hinrich B. Winther](https://github.com/liob), December 2014, and subsequently enhanced by [Nandakumar Chandrasekhar](https://www.linkedin.com/in/nandakumar-chandrasekhar-a400b45b/) with additional features.
