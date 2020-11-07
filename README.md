# Pandoc Reader

Pandoc Reader is a [Pelican](http://getpelican.com) plugin to convert documents written in [Pandoc](https://pandoc.org/) Markdown to HTML 5.

[Pandoc's Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown) is a flavour of [Markdown](http://daringfireball.net/projects/markdown/) with extensions.

## Prerequisites

For this plugin to function you must have Pandoc and the [PyYAML](https://pypi.org/project/PyYAML/) python package installed on your system.

Please follow the [installation instructions](https://pandoc.org/installing.html) to install Pandoc.

To install PyYAML execute the following command using [pip](https://pip.pypa.io/en/stable/installing/):

```bash
pip install PyYAML
```

This package has been tested using the following versions of the above dependencies:

* Pandoc 2.11.0
* PyYAML 5.3.1

## Installation

The plugin may be installed using pip:

```bash
python -m pip install pelican-pandoc-reader
```

## Usage

This plugin converts Pandoc's Markdown into HTML 5. Conversion to formats other than HTML 5 will not be supported.

### Specifying Pandoc Options

The plugin supports two methods to pass options to Pandoc and are **mutually exclusive**. These methods are described in the sections below.

#### Method One: Using Settings in `pelicanconf.py`

The first method involves configuring two settings in your `pelicanconf.py` file:

* `PANDOC_ARGS`
* `PANDOC_EXTENSIONS`

In the `PANDOC_ARGS` parameter you may specify any argument supported by Pandoc ah shown below:

```python
PANDOC_ARGS = [
  '--mathjax'
  '--citeproc'
]
```

Generation of a table of contents is supported by this plugin by specifying the `--toc` or `--table-of-contents` argument as shown below:

```python
PANDOC_ARGS = [
  '--toc'
]
```

or

```python
PANDOC_ARGS = [
  '--table-of-contents'
]
```

The table of contents will be available as an HTML snippet in the metadata of an article and can be referenced as `{{ article.toc }}` in templates.

**Note: Specifying the arguments `--standalone` or `--self-contained` are not supported and will throw an error. Arguments that are relevant only in standalone mode such as `--highlight-style` will not take effect except for `--toc` of `table-of-contents`.**

Then in the `PANDOC_EXTENSIONS` parameter you may enable/disable any number of the supported [Pandoc extensions](https://pandoc.org/MANUAL.html#extensions).

```python
PANDOC_EXTENSIONS = [
  '+footnotes',  # Enabled extension
  '-pipe_tables' # Disabled extension
]
```

#### Method Two: Using Pandoc Defaults Files

The second method involves specifying the path(s) to one or more YAML file(s), with all your preferences.

These paths should be set in your `pelicanconf.py` file by using the setting `PANDOC_DEFAULT_FILES`. The paths maybe absolute or relative but we recommend using relative paths as they are more portable.

```python
PANDOC_DEFAULT_FILES = [
  '<path/to/default/file_one.yaml>',
  '<path/to/default/file_two.yaml>'
]
```

Using default files has the added benefit of allowing you to use other markdown flavors supported by Pandoc such as [CommonMark](https://commonmark.org/) and [GitHub-Flavored Markdown](https://docs.github.com/en/free-pro-team@latest/github/writing-on-github).

Here is a simple example of a content that should be available in a Pandoc defaults file:

```yaml
reader: markdown
writer: html5
```

Generation of a table of contents is supported by this plugin by setting the `table-of-contents` to `true` as shown below:

```yaml
table-of-contents: true
```

The table of contents will be available as an HTML snippet in the metadata of an article and can be referenced as `{{ article.toc }}` in templates.

Please see [Pandoc Default files](https://pandoc.org/MANUAL.html#default-files) for a more complete example of the options available for this file.

**Note: If `standalone` or `self-contained` are set to `true` you will get an error message. Specifying fields that are only relevant in standalone mode such as `highlight-style` will not take effect except for `table-of-contents`.**

### Specifying File Metadata

The plugin expects all markdown files to start with a YAML block as shown below.

```yaml
---
title: "<post-title>"
author: "<author-name>"
data: "<date>"
---
```

or

```yaml
...
title: "<post-title>"
author: "<author-name>"
date: "<date>"
...
```

**Note: Pelican's recommended format for metadata is different to what is specified here, and may require you to rewrite the metadata in your files, if you stop using this plugin.**

More information about Pelican's predefined metadata is available [here](https://docs.getpelican.com/en/stable/content.html#file-metadata).

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues](https://github.com/pelican-plugins/pandoc-reader/issues).

To start contributing to this plugin, review the [Contributing to Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation, beginning with the **Contributing Code** section.

## Credits

Originally authored by [Hinrich B. Winther](https://github.com/liob), December 2014, and subsequently forked and enhanced by [Nandakumar Chandrasekhar](https://www.linkedin.com/in/nandakumar-chandrasekhar-a400b45b/) with additional features in October 2020.
