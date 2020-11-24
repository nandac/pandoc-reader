# Pandoc Reader

The Pandoc Reader is a [Pelican](http://getpelican.com) plugin that converts documents written in [Pandoc's Markdown](https://pandoc.org/MANUAL.html#pandocs-markdown) into HTML 5.

## Prerequisites

The plugin has a number of dependencies:

* Python >= 3.7
* Pelican >= 4.5.1
* Pandoc >= 2.11.0
* PyYAML >= 5.3.1

All four **must** be installed locally on your machine or webserver.

To find out how to install Python please see [here](https://wiki.python.org/moin/BeginnersGuide/Download)

To install Pandoc follow these [installation instructions](https://pandoc.org/installing.html).

[PyYAML](https://pypi.org/project/PyYAML/) and Pelican can be installed using [pip](https://pip.pypa.io/en/stable/installing/) as shown below

```bash
pip install pelican
pip install PyYAML
```

The plugin should function correctly on newer versions of the above dependencies as well.

## Installation

To install the plugin execute the following command.

```bash
python -m pip install pelican-pandoc-reader
```

## Usage

This plugin converts Pandoc's Markdown into HTML 5. Conversion from other flavours of Markdown are supported but requires the use of a default file as described [here](https://github.com/nandac/pandoc-reader#method-two-using-pandoc-defaults-files).

o formats other than HTML 5 is not supported.

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

**Note: The plugin supports Pandoc's YAML syntax for specifying metadata. However, Pelican's format for metadata is different and may need to be rewritten if you stop using this plugin.

YAML blocks that define more that one level such as YAML lists are not supported although they are supported by Pandoc. This is due to metadata processing limitations. In cases where you would normally add a YAML list use a comma separated string such as when specifying tags.

More information on Pandoc's Metadata blocks are available [here](https://pandoc.org/MANUAL.html#metadata-blocks).

Information about Pelican's predefined metadata is available [here](https://docs.getpelican.com/en/stable/content.html#file-metadata).

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

#### Method Two: Using Pandoc Default Files

The second method involves specifying the path(s) to one or more default file(s) with all your preferences written in YAML format.

These paths should be set in your `pelicanconf.py` file by using the setting `PANDOC_DEFAULT_FILES`. The paths maybe absolute or relative but we recommend using relative paths as they are more portable.

```python
PANDOC_DEFAULT_FILES = [
    '<path/to/default/file_one.yaml>',
    '<path/to/default/file_two.yaml>'
]
```

Here is a minimal example of content that should be available in a Pandoc default file:

```yaml
reader: markdown
writer: html5
```

Using default files has the added benefit of allowing you to use other Markdown flavors supported by Pandoc such as [CommonMark](https://commonmark.org/) and [GitHub-Flavored Markdown](https://docs.github.com/en/free-pro-team@latest/github/writing-on-github).

Please see [Pandoc Default files](https://pandoc.org/MANUAL.html#default-files) for a more complete example.

**Note: In both methods specifying the arguments `--standalone` or `--self-contained` is not supported and will result in an error.**

### Generating a Table of Contents

If you desire to create a Table of Contents for your posts or pages, you may do so by specifying the `--toc` or `--table-of-contents` argument in the `PANDOC_ARGS` setting as shown.

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

If you are using a default file you need the following as a bare minimum to enable citations.

```yaml
reader: markdown+citations
writer: html5

citeproc: true
```

Without these settings citations will not be processed by the plugin.

You may write your bibliography in any format supported by Pandoc with the appropriate extensions specified. However, you **must** name the bibliography file the same as your blog.

For example, a blog with the file name `my-blog.md` should have a bibliography file called `my-blog.bib`, `my-blog.json`, `my-blog.yaml` or `my-blog.bibtex`in the same directory as your blog or in a subdirectory of the directory that your blog resides in. Failing to do so will mean that the citations will not be picked up.

### Calculating and Displaying Reading Time

The plugin can be set to calculate the reading time of articles and pages by setting `CALCULATE_READING_TIME` to `True` in your `pelicanconf.py` file.

```python
CALCULATE_READING_TIME = True
```

You may display the reading time using the `{{ article.reading_time }}` or `{{ page.reading_time }}` template variables. The unit of time will be displayed as minute or minutes depending on whether the reading time is less than or equal to one minute or greater than one minute.

The reading time is calculated by dividing the number of words by the reading speed, which is set to the average number of words read in one minute.

The default value for reading speed is set to 200 words per minute, but may be customized by setting `READING_SPEED` to the desired words per minute integer value in `pelicanconf.py`.

```python
READING_SPEED = <words-per-minute>
```

The number of words in a document is calculated by a Pandoc Lua Filter called [wordcount.lua](https://github.com/pandoc/lua-filters/blob/master/wordcount/wordcount.lua) which omits words in metadata fields and code blocks, providing a more accurate word count.

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

To overcome this issue, you may download a local copy of the CSL file to your machine or webserver, and give the `csl` argument a relative path to the file. This speeds up processing by 10x.

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues](https://github.com/pelican-plugins/pandoc-reader/issues).

To start contributing to this plugin, review the [Contributing to Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation, beginning with the **Contributing Code** section.

## Credits

Authored by [Nandakumar Chandrasekhar](https://www.linkedin.com/in/nandakumar-chandrasekhar-a400b45b/).
