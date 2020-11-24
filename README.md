# Pandoc Reader

The Pandoc Reader is a [Pelican](http://getpelican.com) plugin that converts documents written in [Pandoc's Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown) into HTML 5.

## Prerequisites

The plugin has a number of dependencies:

1. Python >= 3.7
1. Pelican >= 4.5.1
1. Pandoc >= 2.11.0
1. PyYAML >= 5.3.1

All three **must** be installed locally on your machine or webserver.

To find out how to install Python please see [here](https://wiki.python.org/moin/BeginnersGuide/Download)

To install Pandoc follow these [installation instructions](https://pandoc.org/installing.html).

[PyYAML](https://pypi.org/project/PyYAML/) and Pelican can be installed using [pip](https://pip.pypa.io/en/stable/installing/) as shown below

```bash
pip install pelican
pip install PyYAML
```

The plugin should function correctly on newer versions of the above dependencies as well.

## Installation

to install the plugin execute the following command.

```bash
python -m pip install pelican-pandoc-reader
```

## Usage

This plugin only converts Pandoc's Markdown into HTML 5. Conversion to formats other than HTML 5 is not supported.

Other flavors of Markdown are supported but requires the use of a default file as described [here](https://github.com/nandac/pandoc-reader#method-two-using-pandoc-defaults-files).

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

**Note: Pelican's recommended format for metadata is different to what is specified here. You may need to rewrite the metadata in your files if you stop using this plugin.**

More information about Pelican's predefined metadata is available [here](https://docs.getpelican.com/en/stable/content.html#file-metadata).

### Specifying Pandoc Options

The plugin supports two **mutually exclusive** methods to pass options to Pandoc.

#### Method One: Using Settings in `pelicanconf.py`

The first method involves configuring two settings in your `pelicanconf.py` file:

* `PANDOC_ARGS`
* `PANDOC_EXTENSIONS`

In the `PANDOC_ARGS` parameter you may specify any argument supported by Pandoc as shown below.

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

Here is a simple example of content that should be available in a Pandoc default file:

```yaml
reader: markdown
writer: html5
```

Using default files has the added benefit of allowing you to use other Markdown flavors supported by Pandoc such as [CommonMark](https://commonmark.org/) and [GitHub-Flavored Markdown](https://docs.github.com/en/free-pro-team@latest/github/writing-on-github).

Please see [Pandoc Default files](https://pandoc.org/MANUAL.html#default-files) for a more complete example of the options available for this file.

**Note: In both methods specifying the arguments `--standalone` or `--self-contained` is not supported.**

### Generating a Table of Contents

If you desire to create a Table of Contents, for your posts or pages, you may do so by specifying the `--toc` or `--table-of-contents` argument in the `PANDOC_ARGS` setting as shown.

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

To set this in a default file use the syntax below.

```yaml
table-of-contents: true
```

The table of contents will be available for use in templates using the `{{ article.toc }}` or `{{ page.toc }}` Jinja template variables.

### Enabling Citations

You may enable citations for your posts or pages by specifying the `citations` extension and the `-C` or `--citeproc` option.

Set the `PANDOC_ARGS` and `PANDOC_EXTENSIONS` in `pelicanconf.py` as shown below.

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

If you are using a default file you need the following as a bare minimum.

```yaml
reader: markdown+citations
writer: html5

citeproc: true
```

Without these settings citations will not be processed by the plugin.

You may write your bibliography in any format supported by Pandoc with the appropriate extensions specified. However, you **must** name the bibliography file the same as your blog.

For example a blog with the file name `my-blog.md` should have a bibliography file called `my-blog.bib`, `my-blog.json`, `my-blog.yaml` or `my-blog.bibtex`in the same directory as your blog or in a subdirectory of the directory that your blog resides in. Failing to so will mean that the citations will not be picked up.

### Calculating and Displaying Reading Time

The plugin also has the capability to calculate the reading time for an article or page. To enable the calculation of the reading time you will have to set the `CALCULATE_READING_TIME` setting to `True` in your `pelicanconf.py` file as shown below.

```python
CALCULATE_READING_TIME = True
```

You may access the reading time in templates by using `{{ article.reading_time }}` or `{{ page.reading_time }}` variables.

The reading time is calculated by dividing the number of words by the words per minute. The default value for the words per minutes is 200 words.

This value may be customized by setting the `WORDS_PER_MINUTE_READ_TIME` to the desired value in `pelicanconf.py`.

```python
WORDS_PER_MINUTE_READ_TIME = <words-per-minute>
```

The number of words in a document is calculated by a Pandoc Lua Filter called [wordcount.lua](https://github.com/pandoc/lua-filters/blob/master/wordcount/wordcount.lua), which has the benefit of omitting words in metadata fields and code blocks, providing an accurate word count.

### Known Issues

The posts and pages of your site can take several seconds to be converted to HTML if linking to a Citation Style Language (CSL) specification, using a URL, as shown below:

```python
PANDOC_ARGS = [
   '--csl=https://www.zotero.org/styles/ieee-with-url'
]
```

or

```yaml
csl: "https://www.zotero.org/styles/ieee-with-url"
```

This is due to the need to re-download the CSL specification for every post or page causing long processing times.

Therefore, we recommend downloading the CSL specification to your machine or webserver, and giving the `csl` argument a relative path to the file. This speeds up processing time by 10x.

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues](https://github.com/pelican-plugins/pandoc-reader/issues).

To start contributing to this plugin, review the [Contributing to Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation, beginning with the **Contributing Code** section.

## Credits

Originally authored by [Hinrich B. Winther](https://github.com/liob), December 2014, and subsequently forked and enhanced by [Nandakumar Chandrasekhar](https://www.linkedin.com/in/nandakumar-chandrasekhar-a400b45b/) through the addition of several features in October 2020.
