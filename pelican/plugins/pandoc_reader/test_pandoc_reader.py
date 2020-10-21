"""Tests for pandoc-reader plugin."""
import os
import shutil
import unittest

from pandoc_reader import PandocReader
from pelican.tests.support import get_settings

DIR_PATH = os.path.dirname(__file__)
CONTENT_PATH = os.path.abspath(os.path.join(DIR_PATH, "content"))
DEFAULTS_PATH = os.path.abspath(os.path.join(DIR_PATH, "defaults"))

# Test settings that will be set in pelicanconf.py by plugin users
PANDOC_ARGS = ["--mathjax"]
PANDOC_EXTENSIONS = ["+smart", "+citations", "+implicit_figures"]


class TestPandocReader(unittest.TestCase):
    """Test class for pandoc-reader plugin."""

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
        self.assertEqual("Could not find metadata header '...' or '---'.", message)

    def test_metadata_block_end(self):
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
        self.assertEqual("Argument --self-contained is not supported.", message)

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
                '<h1 id="valid-content">Valid Content</h1>\n<p>This'
                " is some valid content that should pass."
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
        source_path = os.path.join(CONTENT_PATH, "valid_content_with_raw_paths.md")
        output, metadata = pandoc_reader.read(source_path)

        # Setting this so that assert is able to execute the difference
        self.maxDiff = None

        self.assertEqual(
            (
                '<h1 id="valid-content-with-fictitious-raw-paths">'
                "Valid Content with Fictitious Raw Paths</h1>\n"
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

    # Tests using default files
    def test_invalid_standalone(self):
        """Check if exception is raised if standalone is true."""
        pandoc_default_files = [os.path.join(DEFAULTS_PATH, "standalone_true.yaml")]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("The default standalone should be set to false.", message)

    def test_invalid_self_contained(self):
        """Check if exception is raised if self-contained is true."""
        pandoc_default_files = [os.path.join(DEFAULTS_PATH, "selfcontained_true.yaml")]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("The default self-contained should be set to false.", message)

    def test_no_input_format(self):
        """Check if exception is raised if no input format is specified."""
        pandoc_default_files = [os.path.join(DEFAULTS_PATH, "no_input_format.yaml")]

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
        pandoc_default_files = [os.path.join(DEFAULTS_PATH, "no_output_format.yaml")]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Output format type must be html or html5.", message)

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
        self.assertEqual("Output format type must be html or html5.", message)

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
        self.assertEqual("Output format type must be html or html5.", message)

    def test_valid_file_with_valid_defaults(self):
        """Check if we get the appropriate output specifying defaults."""
        pandoc_default_files = [os.path.join(DEFAULTS_PATH, "valid_defaults.yaml")]

        settings = get_settings(PANDOC_DEFAULT_FILES=pandoc_default_files)

        pandoc_reader = PandocReader(settings)

        source_path = os.path.join(CONTENT_PATH, "valid_content.md")
        output, metadata = pandoc_reader.read(source_path)

        self.assertEqual(
            (
                '<h1 id="valid-content">Valid Content</h1>\n<p>This'
                " is some valid content that should pass."
                " If it does not pass we"
                " will know something is wrong.</p>\n"
            ),
            output,
        )

        self.assertEqual("Valid Content", str(metadata["title"]))
        self.assertEqual("My Author", str(metadata["author"]))
        self.assertEqual("2020-10-16 00:00:00", str(metadata["date"]))

    def test_mathjax_with_valid_defaults(self):
        """Check if mathematics is rendered correctly with defaults."""
        pandoc_default_files = [os.path.join(DEFAULTS_PATH, "valid_defaults.yaml")]

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


if __name__ == "__main__":
    unittest.main()
