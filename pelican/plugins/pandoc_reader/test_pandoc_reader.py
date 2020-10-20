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

    settings = get_settings(
        PANDOC_EXTENSIONS=PANDOC_EXTENSIONS, PANDOC_ARGS=PANDOC_ARGS
    )

    pandoc_reader = PandocReader(settings)

    def test_pandoc_installed(self):
        """Check if Pandoc is installed."""
        source_path = os.path.join(CONTENT_PATH, "empty.md")

        if not shutil.which("pandoc"):
            # Case where pandoc is not installed
            with self.assertRaises(Exception) as context_manager:
                self.pandoc_reader.read(source_path)

            message = str(context_manager.exception)
            self.assertEqual("Could not find Pandoc. Please install.", message)
        else:
            # Case where pandoc is installed
            message = "Pandoc is installed."
            self.assertEqual("Pandoc is installed.", message)

    def test_empty_file(self):
        """Check if a file is empty."""
        source_path = os.path.join(CONTENT_PATH, "empty.md")

        # If the file is empty retrieval of metadata should fail
        with self.assertRaises(Exception) as context_manager:
            self.pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find metadata. File is empty", message)

    def test_non_empty_file_no_metadata(self):
        """Check if a file has no metadata."""
        source_path = os.path.join(CONTENT_PATH, "no_metadata.md")

        # If the file is not empty but has no metadata it should fail
        with self.assertRaises(Exception) as context_manager:
            self.pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find metadata header '---' or '...'", message)

    def test_metadata_block_end(self):
        """Check if the metadata block ends."""
        source_path = os.path.join(CONTENT_PATH, "no_metadata_end.md")

        # Metadata blocks should end with '___' or '...' if not it should fail
        with self.assertRaises(Exception) as context_manager:
            self.pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find end of metadata block.", message)

    def test_invalid_metadata_block_end(self):
        """Check if the metadata block end is wrong."""
        source_path = os.path.join(CONTENT_PATH, "no_metadata_end.md")

        # Metadata blocks should end with '___' or '...' if not it should fail
        with self.assertRaises(Exception) as context_manager:
            self.pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find end of metadata block.", message)

    def test_valid_file(self):
        """Check if we get the appropriate output for valid input."""
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")
        output, metadata = self.pandoc_reader.read(source_path)

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
        source_path = os.path.join(CONTENT_PATH, "mathjax_content.md")
        output, metadata = self.pandoc_reader.read(source_path)

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

    def test_invalid_standalone(self):
        """Check if exception is raised if standalone is true."""
        pandoc_default_files = [
            os.path.join(DEFAULTS_PATH, "standalone_true.yaml")
        ]

        settings = get_settings(
            PANDOC_DEFAULT_FILES=pandoc_default_files
        )

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

        settings = get_settings(
            PANDOC_DEFAULT_FILES=pandoc_default_files
        )

        pandoc_reader = PandocReader(settings)
        source_path = os.path.join(CONTENT_PATH, "valid_content.md")

        with self.assertRaises(ValueError) as context_manager:
            pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual(
            "The default self-contained should be set to false.", message
        )

if __name__ == "__main__":
    unittest.main()
