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

Earlier versions of these dependencies will not be supported.

## Installation

The plugin may be installed using pip:

```bash
python -m pip install pelican-pandoc-reader
```

## Usage

This plugin converts Pandoc's Markdown into HTML 5. Conversion to formats other than HTML 5 will not be supported.

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

### Specifying Pandoc Options

The plugin supports two methods to pass options to Pandoc that are **mutually exclusive**. These methods are described in the sections below.

#### Method One: Using Settings in `pelicanconf.py`

The first method involves configuring two settings in your `pelicanconf.py` file:

* `PANDOC_ARGS`
* `PANDOC_EXTENSIONS`

In the `PANDOC_ARGS` parameter you may specify any argument supported by Pandoc as shown below:

```python
PANDOC_ARGS = [
    '--mathjax'
    '--citeproc'
]
```

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

Here is a simple example of content that should be available in a Pandoc defaults file:

```yaml
reader: markdown
writer: html5
```

Please see [Pandoc Default files](https://pandoc.org/MANUAL.html#default-files) for a more complete example of the options available for this file.

**Note: In both methods specifying the arguments `--standalone` or `--self-contained` is not supported.**

### Generating a Table of Contents

If you desire to create a Table of Contents for your posts or pages you may do so by specifying the `--toc` or `--table-of-contents` argument in the `PANDOC_ARGS` setting as shown:

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

To specify this setting in a defaults file use the syntax below:

```yaml
table-of-contents: true
```

The table of contents will be available for use in templates using the `{{ article.toc }}` or `{{ page.toc }}` Jinja variables.

### Citation Support

You may enable citations for your posts or pages by specifying the `citations` extension and the `-C` or `--citeproc` option.

Set the `PANDOC_ARGS` and `PANDOC_EXTENSIONS` in `pelicanconf.py` as shown below:

```python
PANDOC_ARGS = [
    '--citeproc'
]
```

or

```python
PANDOC_ARGS = [
    '-C'
]
```

and

```python
PANDOC_EXTENSIONS = [
    '+citations'
]
```

If you are using a defaults file you should specify the following as a bare minimum.

```yaml
reader: markdown+citations
writer: html5

citeproc: true
```

Without these settings citations will not be processed by the plugin.

You may write your citations in any format supported by Pandoc with the appropriate extension.

However, you **must** name it the same as your blog. For example a blog with the file name `my-blog.md` should have a citations file called `my-blog.bib` or `my-blog.json`or `my-blog.yaml` or `my-blog.bibtex`.

You **must** place the citations file in the same directory that your blog resides or in a subdirectory of that directory. Otherwise the citations will not be picked up.

### Known Issues

The posts and pages of your site can take several seconds to be converted to HTML, if linking to a Citation Style Language (CSL) specification using a URL, as shown below:

```python
PANDOC_ARGS = [
   '--csl=https://www.zotero.org/styles/ieee-with-url'
]
```

or

```yaml
csl: "https://www.zotero.org/styles/ieee-with-url"
```

This is due to the need to download the CSL specification for every post or page each time which causing very long processing times.

Therefore, we recommend downloading the CSL specification to your machine or webserver, and giving the `csl` argument a relative path to the file. This speeds up processing time by 10x.

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues](https://github.com/pelican-plugins/pandoc-reader/issues).

To start contributing to this plugin, review the [Contributing to Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation, beginning with the **Contributing Code** section.

## Credits

Originally authored by [Hinrich B. Winther](https://github.com/liob), December 2014, and subsequently forked and enhanced by [Nandakumar Chandrasekhar](https://www.linkedin.com/in/nandakumar-chandrasekhar-a400b45b/) through the addition of several features in October 2020.
