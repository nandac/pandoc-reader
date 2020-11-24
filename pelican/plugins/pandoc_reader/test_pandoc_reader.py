"""Tests for pandoc-reader plugin."""
# pylint: disable=too-many-lines
import os
import shutil
import unittest

from pelican.tests.support import get_settings

from pandoc_reader import PandocReader

DIR_PATH = os.path.dirname(__file__)
CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "content"))
DEFAULTS_PATH = os.path.abspath(os.path.join(DIR_PATH, "defaults"))

# Test settings that will be set in pelicanconf.py by plugin users
PANDOC_ARGS = ["--mathjax"]
PANDOC_EXTENSIONS = ["+smart", "+implicit_figures"]
CALCULATE_READING_TIME = True
FORMATTED_FIELDS = ["summary"]


class TestGeneralTestCases(unittest.TestCase):
    """Test installation of Pandoc."""

    # Test using pelicanconf settings variables
    def test_pandoc_installed(self):
        """Check if Pandoc is installed."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "empty.md")

        if not shutil.which("pandoc"):
            # Case where pandoc is not installed
            with self.assertRaises(Exception) as context_manager:
                pandoc_reader.read(source_path)

            message = str(context_manager.exception)
            self.assertEqual("Could not find Pandoc. Please install.", message)
        else:
            # Case where pandoc is installed
            message = "Pandoc is installed."
            self.assertEqual("Pandoc is installed.", message)

    def test_default_wpm_reading_time(self):
        """Check if 200 words per minute give us reading time of 2 minutes."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS,
            PANDOC_ARGS=PANDOC_ARGS,
            CALCULATE_READING_TIME=CALCULATE_READING_TIME,
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "reading_time_content.md")

        _, metadata = pandoc_reader.read(source_path)

        self.assertEqual("2", str(metadata["reading_time"]))

    def test_user_defined_wpm_reading_time(self):
        """Check if 100 words per minute user defined gives us 4 minutes."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS,
            PANDOC_ARGS=PANDOC_ARGS,
            CALCULATE_READING_TIME=CALCULATE_READING_TIME,
            WORDS_PER_MINUTE_READ_TIME=100,
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "reading_time_content.md")

        _, metadata = pandoc_reader.read(source_path)

        self.assertEqual("4", str(metadata["reading_time"]))

    def test_invalid_user_defined_wpm(self):
        """Check if exception is raised if words per minute is not a number."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS,
            PANDOC_ARGS=PANDOC_ARGS,
            CALCULATE_READING_TIME=CALCULATE_READING_TIME,
            WORDS_PER_MINUTE_READ_TIME="my words per minute",
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "reading_time_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "WORDS_PER_MINUTE_READ_TIME must be a number.", message
        )

    def test_summary(self):
        """Check if summary output is valid."""

        pandoc_default_files = [
            os.path.join(
                DEFAULTS_PATH, "valid_defaults_with_toc_and_citations.yaml"
            )
        ]

        settings = get_settings(
            PANDOC_DEFAULT_FILES=pandoc_default_files,
            FORMATTED_FIELDS=FORMATTED_FIELDS,
        )
        pandoc_reader = PandocReader(settings)

        source_path = os.path.join(
            CONTENT_PATH, "valid_content_with_citation.md"
        )

        _, metadata = pandoc_reader.read(source_path)

        self.assertEqual(
            (
                "<p>But this foundational principle of science has now been"
                " called into question by"
                ' <a href="https://www.britannica.com/science/string-theory">'
                "String Theory</a>.</p>\n"
            ),
            str(metadata["summary"]),
        )


class TestInvalidCasesWithArguments(unittest.TestCase):
    """Invalid test cases using Pandoc arguments and extensions."""

    def test_empty_file(self):
        """Check if a file is empty."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "empty.md")

        # If the file is empty retrieval of metadata should fail
        with self.assertRaises(Exception) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find metadata. File is empty.", message)

    def test_non_empty_file_no_metadata(self):
        """Check if a file has no metadata."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "no_metadata.md")

        # If the file is not empty but has no metadata it should fail
        with self.assertRaises(Exception) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "Could not find metadata header '...' or '---'.", message
        )

    def test_no_metadata_block_end(self):
        """Check if the metadata block ends."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "no_metadata_end.md")

        # Metadata blocks should end with '___' or '...' if not it should fail
        with self.assertRaises(Exception) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find end of metadata block.", message)

    def test_invalid_metadata_block_end(self):
        """Check if the metadata block end is wrong."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "no_metadata_end.md")

        # Metadata blocks should end with '___' or '...' if not it should fail
        with self.assertRaises(Exception) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find end of metadata block.", message)

    def test_invalid_standalone_argument(self):
        """Check that specifying --standalone raises an exception."""
        pandoc_arguments = ["--standalone"]
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=pandoc_arguments
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Argument --standalone is not supported.", message)

    def test_invalid_self_contained_argument(self):
        """Check that specifying --self-contained raises an exception."""
        pandoc_arguments = ["--self-contained"]
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=pandoc_arguments
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "Argument --self-contained is not supported.", message
        )


class TestValidCasesWithArguments(unittest.TestCase):
    """Valid test cases using Pandoc arguments and extensions."""

    def test_valid_file(self):
        """Check if we get the appropriate output for valid input."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")
        output, metadata = pandoc_reader.read(source_path)

        self.assertEqual(
            (
                "<p>This is some valid content that should pass."
                " If it does not pass we"
                " will know something is wrong.</p>\n"
            ),
            output,
        )

        self.assertEqual("Valid Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_mathjax_content(self):
        """Check if mathematics is rendered correctly."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "mathjax_content.md")
        output, metadata = pandoc_reader.read(source_path)

        self.assertEqual(
            (
                '<p><span class="math display">\\[\ne^{i\\theta} = '
                "\\cos\\theta + i \\sin\\theta.\n\\]</span></p>\n"
            ),
            output,
        )

        self.assertEqual("MathJax Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_encoded_to_raw_conversion(self):
        """Check if raw paths are left untouched in output returned"""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(
            CONTENT_PATH, "valid_content_with_raw_paths.md"
        )
        output, metadata = pandoc_reader.read(source_path)

        # Setting this so that assert is able to execute the difference
        self.maxDiff = None  # pylint: disable=invalid-name

        self.assertEqual(
            (
                "<p>This is some valid content that should pass."
                " If it does not pass we will know something is wrong.</p>\n"
                "<p>Our fictitious internal files are available"
                ' <a href="{filename}/path/to/file">at</a>:</p>\n'
                "<p>Our fictitious static files are available"
                ' <a href="{static}/path/to/file">at</a>:</p>\n'
                "<p>Our fictitious attachments are available"
                ' <a href="{attach}path/to/file">at</a>:</p>\n'
            ),
            output,
        )

        self.assertEqual(
            "Valid Content with Fictitious Raw Paths", str(metadata["title"])
        )
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_valid_content_with_toc(self):
        """Check if output returned is valid and table of contents is valid."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS,
            PANDOC_ARGS=PANDOC_ARGS + ["--toc"],
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content_with_toc.md")
        output, metadata = pandoc_reader.read(source_path)

        # Setting this so that assert is able to execute the difference
        self.maxDiff = None

        self.assertEqual(
            (
                "<p>This is some valid content that should pass."
                " If it does not pass we will know something is wrong.</p>\n"
                '<h2 id="first-heading">First Heading</h2>\n'
                "<p>This should be the first heading in my"
                " table of contents.</p>\n"
                '<h2 id="second-heading">Second Heading</h2>\n'
                "<p>This should be the second heading in my"
                " table of contents.</p>\n"
                '<h3 id="first-subheading">First Subheading</h3>\n'
                "<p>This is a subsection that should be shown as such"
                " in the table of contents.</p>\n"
                '<h3 id="second-subheading">Second Subheading</h3>\n'
                "<p>This is another subsection that should be shown as"
                " such in the table of contents.</p>\n"
            ),
            output,
        )
        self.assertEqual(
            "Valid Content with Table of Contents", str(metadata["title"])
        )
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))
        self.assertEqual(
            '<nav class="toc" role="doc-toc">\n'
            "<ul>\n"
            '<li><a href="#first-heading">First Heading</a></li>\n'
            '<li><a href="#second-heading">Second Heading</a>\n'
            "<ul>\n"
            '<li><a href="#first-subheading">First Subheading</a></li>\n'
            '<li><a href="#second-subheading">Second Subheading</a></li>\n'
            "</ul></li>\n"
            "</ul>\n"
            "</nav>\n",
            str(metadata["toc"]),
        )

    def test_valid_content_with_toc_2(self):
        """Check if output returned is valid and table of contents is valid."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS,
            PANDOC_ARGS=PANDOC_ARGS + ["--table-of-contents"],
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content_with_toc.md")
        output, metadata = pandoc_reader.read(source_path)

        # Setting this so that assert is able to execute the difference
        self.maxDiff = None

        self.assertEqual(
            (
                "<p>This is some valid content that should pass."
                " If it does not pass we will know something is wrong.</p>\n"
                '<h2 id="first-heading">First Heading</h2>\n'
                "<p>This should be the first heading in my"
                " table of contents.</p>\n"
                '<h2 id="second-heading">Second Heading</h2>\n'
                "<p>This should be the second heading in my"
                " table of contents.</p>\n"
                '<h3 id="first-subheading">First Subheading</h3>\n'
                "<p>This is a subsection that should be shown as such"
                " in the table of contents.</p>\n"
                '<h3 id="second-subheading">Second Subheading</h3>\n'
                "<p>This is another subsection that should be shown as"
                " such in the table of contents.</p>\n"
            ),
            output,
        )
        self.assertEqual(
            "Valid Content with Table of Contents", str(metadata["title"])
        )
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))
        self.assertEqual(
            '<nav class="toc" role="doc-toc">\n'
            "<ul>\n"
            '<li><a href="#first-heading">First Heading</a></li>\n'
            '<li><a href="#second-heading">Second Heading</a>\n'
            "<ul>\n"
            '<li><a href="#first-subheading">First Subheading</a></li>\n'
            '<li><a href="#second-subheading">Second Subheading</a></li>\n'
            "</ul></li>\n"
            "</ul>\n"
            "</nav>\n",
            str(metadata["toc"]),
        )

    def test_citations_and_toc(self):
        """Check if output, citations and table of contents CLI are valid."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS + ["+citations"],
            PANDOC_ARGS=PANDOC_ARGS
            + [
                "--toc",
                "-C",
                "--csl=https://www.zotero.org/styles/ieee-with-url",
                "--metadata=link-citations:false",
                "--metadata=reference-section-title:References",
            ],
            FORMATTED_FIELDS=FORMATTED_FIELDS,
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(
            CONTENT_PATH, "valid_content_with_citation.md"
        )
        output, metadata = pandoc_reader.read(source_path)
        self.maxDiff = None

        self.assertEqual(
            (
                '<h2 id="string-theory">String Theory</h2>\n'
                "<p>But this foundational principle of science has"
                " now been called into question by"
                ' <a href="https://www.britannica.com/science/'
                'string-theory">String Theory</a>,'
                " which is a relative newcomer to theoretical physics, but one"
                " that has captured the common imagination, judging by"
                " the popular explanations that abound on the Web"
                ' <span class="citation" data-cites="mann2019 wood2019'
                ' jones2020">[1]–[3]</span>.'
                " And whether string theory is or is not science, Popper"
                " notwithstanding, is an issue that is still up for debate"
                " <span"
                ' class="citation" data-cites="siegel2015 castelvecchi2016'
                ' alves2017 francis2019">[4]–[7]</span>.</p>\n'
                '<h1 class="unnumbered" id="bibliography">References</h1>\n'
                '<div id="refs" class="references csl-bib-body"'
                ' role="doc-bibliography">\n'
                '<div id="ref-mann2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[1]'
                ' </div><div class="csl-right-inline">A. Mann,'
                " <span>“<span>What Is String Theory?</span>”</span>"
                " 20-Mar-2019. [Online]."
                ' Available: <a href="https://www.livescience.com/'
                '65033-what-is-string-theory.html">'
                "https://www.livescience.com/"
                "65033-what-is-string-theory.html</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-wood2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[2] </div>'
                '<div class="csl-right-inline">'
                "C. Wood, <span>“<span>What Is String Theory?</span>."
                " Reference article:"
                " A simplified explanation and brief history of string"
                " theory,”</span> 11-Jul-2019."
                ' [Online]. Available: <a href="https://www.space.com/'
                '17594-string-theory.html">'
                "https://www.space.com/17594-string-theory.html</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-jones2020" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[3]'
                ' </div><div class="csl-right-inline">'
                'A. Z. Jones, <span>“<span class="nocase">The Basics of String'
                " Theory</span>,”</span> 02-Mar-2019. [Online]. Available:"
                ' <a href="https://www.thoughtco.com/'
                'what-is-string-theory-2699363">'
                "https://www.thoughtco.com/what-is-string-theory-2699363</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-siegel2015" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[4]'
                ' </div><div class="csl-right-inline">'
                "E. Siegel, <span>“<span>Why String Theory Is Not A Scientific"
                " Theory</span>,”</span> 23-Dec-2015. [Online]. Available:"
                " <a"
                ' href="https://www.forbes.com/sites/'
                "startswithabang/2015/12/23/"
                'why-string-theory-is-not-science/">https://www.forbes.com/'
                "sites/startswithabang/2015/12/23/"
                "why-string-theory-is-not-science/</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-castelvecchi2016" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[5]'
                ' </div><div class="csl-right-inline">'
                'D. Castelvecchi, <span>“<span class="nocase">'
                "Feuding physicists turn"
                " to philosophy for help</span>. String theory is at the"
                " heart of a debate over the integrity of the scientific"
                " method itself,”</span> 05-Jan-2016. [Online]. Available:"
                ' <a href="https://www.nature.com/news/'
                'feuding-physicists-turn-to-philosophy-for-help-1.19076">'
                "https://www.nature.com/news/"
                "feuding-physicists-turn-to-philosophy-for-help-1.19076</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-alves2017" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[6] </div>'
                '<div class="csl-right-inline">'
                'R. A. Batista and J. Primack, <span>“<span class="nocase">'
                "Is String theory falsifiable?</span>. Can a theory that isn’t"
                " completely testable still be useful to physics?”</span>"
                " [Online]."
                ' Available: <a href="https://metafact.io/factchecks/'
                '30-is-string-theory-falsifiable">'
                "https://metafact.io/factchecks/"
                "30-is-string-theory-falsifiable</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-francis2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[7]'
                ' </div><div class="csl-right-inline">'
                'M. R. Francis, <span>“<span class="nocase">Falsifiability and'
                " physics</span>. Can a theory that isn’t completely testable"
                " still be useful to physics?”</span> 23-Apr-2019."
                " [Online]. Available:"
                ' <a href="https://www.scientificamerican.com/'
                'article/is-string-theory-science/">'
                "https://www.scientificamerican.com/article/is-"
                "string-theory-science/</a>. [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                "</div>\n"
            ),
            output,
        )

        self.assertEqual("Valid Content With Citation", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))
        self.assertEqual(
            (
                '<nav class="toc" role="doc-toc">\n'
                "<ul>\n"
                '<li><a href="#string-theory">String Theory</a></li>\n'
                '<li><a href="#bibliography">References</a></li>\n'
                "</ul>\n</nav>\n"
            ),
            str(metadata["toc"]),
        )
        self.assertEqual(
            (
                "<p>But this foundational principle of science has now been"
                " called into question by"
                ' <a href="https://www.britannica.com/science/string-theory">'
                "String Theory</a>.</p>\n"
            ),
            str(metadata["summary"]),
        )

    def test_citations_and_toc_2(self):
        """Check if output, citations and table of contents CLI are valid."""
        settings = get_settings(
            PANDOC_EXTENSIONS=PANDOC_EXTENSIONS + ["+citations"],
            PANDOC_ARGS=PANDOC_ARGS
            + [
                "--table-of-contents",
                "--citeproc",
                "--csl=https://www.zotero.org/styles/ieee-with-url",
                "--metadata=link-citations:false",
                "--metadata=reference-section-title:References",
            ],
            FORMATTED_FIELDS=FORMATTED_FIELDS,
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(
            CONTENT_PATH, "valid_content_with_citation.md"
        )
        output, metadata = pandoc_reader.read(source_path)
        self.maxDiff = None

        self.assertEqual(
            (
                '<h2 id="string-theory">String Theory</h2>\n'
                "<p>But this foundational principle of science has"
                " now been called into question by"
                ' <a href="https://www.britannica.com/science/'
                'string-theory">String Theory</a>,'
                " which is a relative newcomer to theoretical physics, but one"
                " that has captured the common imagination, judging by"
                " the popular explanations that abound on the Web"
                ' <span class="citation" data-cites="mann2019 wood2019'
                ' jones2020">[1]–[3]</span>.'
                " And whether string theory is or is not science, Popper"
                " notwithstanding, is an issue that is still up for debate"
                " <span"
                ' class="citation" data-cites="siegel2015 castelvecchi2016'
                ' alves2017 francis2019">[4]–[7]</span>.</p>\n'
                '<h1 class="unnumbered" id="bibliography">References</h1>\n'
                '<div id="refs" class="references csl-bib-body"'
                ' role="doc-bibliography">\n'
                '<div id="ref-mann2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[1]'
                ' </div><div class="csl-right-inline">A. Mann,'
                " <span>“<span>What Is String Theory?</span>”</span>"
                " 20-Mar-2019. [Online]."
                ' Available: <a href="https://www.livescience.com/'
                '65033-what-is-string-theory.html">'
                "https://www.livescience.com/"
                "65033-what-is-string-theory.html</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-wood2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[2] </div>'
                '<div class="csl-right-inline">'
                "C. Wood, <span>“<span>What Is String Theory?</span>."
                " Reference article:"
                " A simplified explanation and brief history of string"
                " theory,”</span> 11-Jul-2019."
                ' [Online]. Available: <a href="https://www.space.com/'
                '17594-string-theory.html">'
                "https://www.space.com/17594-string-theory.html</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-jones2020" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[3]'
                ' </div><div class="csl-right-inline">'
                'A. Z. Jones, <span>“<span class="nocase">The Basics of String'
                " Theory</span>,”</span> 02-Mar-2019. [Online]. Available:"
                ' <a href="https://www.thoughtco.com/'
                'what-is-string-theory-2699363">'
                "https://www.thoughtco.com/what-is-string-theory-2699363</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-siegel2015" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[4]'
                ' </div><div class="csl-right-inline">'
                "E. Siegel, <span>“<span>Why String Theory Is Not A Scientific"
                " Theory</span>,”</span> 23-Dec-2015. [Online]. Available:"
                " <a"
                ' href="https://www.forbes.com/sites/'
                "startswithabang/2015/12/23/"
                'why-string-theory-is-not-science/">https://www.forbes.com/'
                "sites/startswithabang/2015/12/23/"
                "why-string-theory-is-not-science/</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-castelvecchi2016" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[5]'
                ' </div><div class="csl-right-inline">'
                'D. Castelvecchi, <span>“<span class="nocase">'
                "Feuding physicists turn"
                " to philosophy for help</span>. String theory is at the"
                " heart of a debate over the integrity of the scientific"
                " method itself,”</span> 05-Jan-2016. [Online]. Available:"
                ' <a href="https://www.nature.com/news/'
                'feuding-physicists-turn-to-philosophy-for-help-1.19076">'
                "https://www.nature.com/news/"
                "feuding-physicists-turn-to-philosophy-for-help-1.19076</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-alves2017" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[6] </div>'
                '<div class="csl-right-inline">'
                'R. A. Batista and J. Primack, <span>“<span class="nocase">'
                "Is String theory falsifiable?</span>. Can a theory that isn’t"
                " completely testable still be useful to physics?”</span>"
                " [Online]."
                ' Available: <a href="https://metafact.io/factchecks/'
                '30-is-string-theory-falsifiable">'
                "https://metafact.io/factchecks/"
                "30-is-string-theory-falsifiable</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-francis2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[7]'
                ' </div><div class="csl-right-inline">'
                'M. R. Francis, <span>“<span class="nocase">Falsifiability and'
                " physics</span>. Can a theory that isn’t completely testable"
                " still be useful to physics?”</span> 23-Apr-2019."
                " [Online]. Available:"
                ' <a href="https://www.scientificamerican.com/'
                'article/is-string-theory-science/">'
                "https://www.scientificamerican.com/article/is-"
                "string-theory-science/</a>. [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                "</div>\n"
            ),
            output,
        )

        self.assertEqual("Valid Content With Citation", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))
        self.assertEqual(
            (
                '<nav class="toc" role="doc-toc">\n'
                "<ul>\n"
                '<li><a href="#string-theory">String Theory</a></li>\n'
                '<li><a href="#bibliography">References</a></li>\n'
                "</ul>\n</nav>\n"
            ),
            str(metadata["toc"]),
        )


class TestInvalidCasesWithDefaultFiles(unittest.TestCase):
    """Invalid test cases using default files."""

    def test_invalid_standalone(self):
        """Check if exception is raised if standalone is true."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "standalone_true.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "The default standalone should be set to false.", message
        )

    def test_invalid_self_contained(self):
        """Check if exception is raised if self-contained is true."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "selfcontained_true.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "The default self-contained should be set to false.", message
        )

    def test_no_input_format(self):
        """Check if exception is raised if no input format is specified."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "no_input_format.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("No input format specified.", message)

    def test_invalid_reader_input_format(self):
        """Check if exception is raised if reader input format is invalid."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "invalid_reader_input_format.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Input type has to be a markdown variant.", message)

    def test_invalid_from_input_format(self):
        """Check if exception is raised if from input format is invalid."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "invalid_from_input_format.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Input type has to be a markdown variant.", message)

    def test_from_reader_both_given(self):
        """Check if exception is raised if from and reader are both given."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "from_reader_both_given.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            (
                "Specifying both from and reader is not supported."
                " Please specify just one."
            ),
            message,
        )

    def test_to_writer_both_given(self):
        """Check if exception is raised if to and writer are both given."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "to_writer_both_given.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            (
                "Specifying both to and writer is not supported."
                " Please specify just one."
            ),
            message,
        )

    def test_no_output_format(self):
        """Check if exception is raised if no output format is specified."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "no_output_format.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "Output format type must be either html or html5.", message
        )

    def test_invalid_writer_output_format(self):
        """Check if exception is raised if writer output format is invalid."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "invalid_writer_output_format.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "Output format type must be either html or html5.", message
        )

    def test_invalid_to_output_format(self):
        """Check if exception is raised if to output format is invalid."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "invalid_to_output_format.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "Output format type must be either html or html5.", message
        )


class TestValidCasesWithDefaultFiles(unittest.TestCase):
    """Valid test cases using default files."""

    def test_valid_file_with_valid_defaults(self):
        """Check if we get the appropriate output specifying defaults."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "valid_defaults.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)

        source_path = os.path.join(CONTENT_PATH, "valid_content.md")
        output, metadata = pandoc_reader.read(source_path)

        self.assertEqual(
            (
                "<p>This is some valid content that should pass."
                " If it does not pass we will know something is wrong.</p>\n"
            ),
            output,
        )

        self.assertEqual("Valid Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_mathjax_with_valid_defaults(self):
        """Check if mathematics is rendered correctly with defaults."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "valid_defaults.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)

        source_path = os.path.join(CONTENT_PATH, "mathjax_content.md")
        output, metadata = pandoc_reader.read(source_path)

        self.assertEqual(
            (
                '<p><span class="math display">\\[\ne^{i\\theta} = '
                "\\cos\\theta + i \\sin\\theta.\n\\]</span></p>\n"
            ),
            output,
        )

        self.assertEqual("MathJax Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_toc_with_valid_defaults(self):
        """Check if output and table of contents are valid with defaults."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "valid_defaults_with_toc.yaml")
        ]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)
        pandoc_reader = PandocReader(settings)

        source_path = os.path.join(CONTENT_PATH, "valid_content_with_toc.md")
        output, metadata = pandoc_reader.read(source_path)

        self.assertEqual(
            (
                "<p>This is some valid content that should pass."
                " If it does not pass we will know something is wrong.</p>\n"
                '<h2 id="first-heading">First Heading</h2>\n'
                "<p>This should be the first heading in my"
                " table of contents.</p>\n"
                '<h2 id="second-heading">Second Heading</h2>\n'
                "<p>This should be the second heading in my"
                " table of contents.</p>\n"
                '<h3 id="first-subheading">First Subheading</h3>\n'
                "<p>This is a subsection that should be shown as such"
                " in the table of contents.</p>\n"
                '<h3 id="second-subheading">Second Subheading</h3>\n'
                "<p>This is another subsection that should be shown as"
                " such in the table of contents.</p>\n"
            ),
            output,
        )
        self.assertEqual(
            "Valid Content with Table of Contents", str(metadata["title"])
        )
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))
        self.assertEqual(
            '<nav class="toc" role="doc-toc">\n'
            "<ul>\n"
            '<li><a href="#first-heading">First Heading</a></li>\n'
            '<li><a href="#second-heading">Second Heading</a>\n'
            "<ul>\n"
            '<li><a href="#first-subheading">First Subheading</a></li>\n'
            '<li><a href="#second-subheading">Second Subheading</a></li>\n'
            "</ul></li>\n"
            "</ul>\n"
            "</nav>\n",
            str(metadata["toc"]),
        )

    def test_citations_and_toc_with_valid_defaults(self):
        """Check if output, citations and table of contents are valid."""

        pandoc_default_files = [
            os.path.join(
                DEFAULTS_PATH, "valid_defaults_with_toc_and_citations.yaml"
            )
        ]

        settings = get_settings(
            PANDOC_DEFAULT_FILES=pandoc_default_files,
            FORMATTED_FIELDS=FORMATTED_FIELDS,
        )
        pandoc_reader = PandocReader(settings)

        source_path = os.path.join(
            CONTENT_PATH, "valid_content_with_citation.md"
        )
        output, metadata = pandoc_reader.read(source_path)
        self.maxDiff = None  # pylint: disable=invalid-name

        self.assertEqual(
            (
                '<h2 id="string-theory">String Theory</h2>\n'
                "<p>But this foundational principle of science has"
                " now been called into question by"
                ' <a href="https://www.britannica.com/science/'
                'string-theory">String Theory</a>,'
                " which is a relative newcomer to theoretical physics, but one"
                " that has captured the common imagination, judging by"
                " the popular explanations that abound on the Web"
                ' <span class="citation" data-cites="mann2019 wood2019'
                ' jones2020">[1]–[3]</span>.'
                " And whether string theory is or is not science, Popper"
                " notwithstanding, is an issue that is still up for debate"
                " <span"
                ' class="citation" data-cites="siegel2015 castelvecchi2016'
                ' alves2017 francis2019">[4]–[7]</span>.</p>\n'
                '<h1 class="unnumbered" id="bibliography">References</h1>\n'
                '<div id="refs" class="references csl-bib-body"'
                ' role="doc-bibliography">\n'
                '<div id="ref-mann2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[1]'
                ' </div><div class="csl-right-inline">A. Mann,'
                " <span>“<span>What Is String Theory?</span>”</span>"
                " 20-Mar-2019. [Online]."
                ' Available: <a href="https://www.livescience.com/'
                '65033-what-is-string-theory.html">'
                "https://www.livescience.com/"
                "65033-what-is-string-theory.html</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-wood2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[2] </div>'
                '<div class="csl-right-inline">'
                "C. Wood, <span>“<span>What Is String Theory?</span>."
                " Reference article:"
                " A simplified explanation and brief history of string"
                " theory,”</span> 11-Jul-2019."
                ' [Online]. Available: <a href="https://www.space.com/'
                '17594-string-theory.html">'
                "https://www.space.com/17594-string-theory.html</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-jones2020" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[3]'
                ' </div><div class="csl-right-inline">'
                'A. Z. Jones, <span>“<span class="nocase">The Basics of String'
                " Theory</span>,”</span> 02-Mar-2019. [Online]. Available:"
                ' <a href="https://www.thoughtco.com/'
                'what-is-string-theory-2699363">'
                "https://www.thoughtco.com/what-is-string-theory-2699363</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-siegel2015" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[4]'
                ' </div><div class="csl-right-inline">'
                "E. Siegel, <span>“<span>Why String Theory Is Not A Scientific"
                " Theory</span>,”</span> 23-Dec-2015. [Online]. Available:"
                " <a"
                ' href="https://www.forbes.com/sites/'
                "startswithabang/2015/12/23/"
                'why-string-theory-is-not-science/">https://www.forbes.com/'
                "sites/startswithabang/2015/12/23/"
                "why-string-theory-is-not-science/</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-castelvecchi2016" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[5]'
                ' </div><div class="csl-right-inline">'
                'D. Castelvecchi, <span>“<span class="nocase">'
                "Feuding physicists turn"
                " to philosophy for help</span>. String theory is at the"
                " heart of a debate over the integrity of the scientific"
                " method itself,”</span> 05-Jan-2016. [Online]. Available:"
                ' <a href="https://www.nature.com/news/'
                'feuding-physicists-turn-to-philosophy-for-help-1.19076">'
                "https://www.nature.com/news/"
                "feuding-physicists-turn-to-philosophy-for-help-1.19076</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-alves2017" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[6] </div>'
                '<div class="csl-right-inline">'
                'R. A. Batista and J. Primack, <span>“<span class="nocase">'
                "Is String theory falsifiable?</span>. Can a theory that isn’t"
                " completely testable still be useful to physics?”</span>"
                " [Online]."
                ' Available: <a href="https://metafact.io/factchecks/'
                '30-is-string-theory-falsifiable">'
                "https://metafact.io/factchecks/"
                "30-is-string-theory-falsifiable</a>."
                " [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                '<div id="ref-francis2019" class="csl-entry"'
                ' role="doc-biblioentry">\n'
                '<div class="csl-left-margin">[7]'
                ' </div><div class="csl-right-inline">'
                'M. R. Francis, <span>“<span class="nocase">Falsifiability and'
                " physics</span>. Can a theory that isn’t completely testable"
                " still be useful to physics?”</span> 23-Apr-2019."
                " [Online]. Available:"
                ' <a href="https://www.scientificamerican.com/'
                'article/is-string-theory-science/">'
                "https://www.scientificamerican.com/article/is-"
                "string-theory-science/</a>. [Accessed: 12-Nov-2020]</div>\n"
                "</div>\n"
                "</div>\n"
            ),
            output,
        )

        self.assertEqual("Valid Content With Citation", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))
        self.assertEqual(
            (
                '<nav class="toc" role="doc-toc">\n'
                "<ul>\n"
                '<li><a href="#string-theory">String Theory</a></li>\n'
                '<li><a href="#bibliography">References</a></li>\n'
                "</ul>\n</nav>\n"
            ),
            str(metadata["toc"]),
        )


if __name__ == "__main__":
    unittest.main()
