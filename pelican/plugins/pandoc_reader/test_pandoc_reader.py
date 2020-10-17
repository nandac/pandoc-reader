"""Tests for pandoc-reader plugin."""
import os
import shutil
import unittest

from pandoc_reader import PandocReader
from pelican.tests.support import get_settings

FILE_PATH = os.path.join(os.getcwd(), "fixtures")


class TestPandocReader(unittest.TestCase):
    """Test class for pandoc-reader plugin."""

    settings = get_settings()
    pandoc_reader = PandocReader(settings)

    def test_pandoc_installed(self):
        """Check if Pandoc is installed."""
        source_path = os.path.join(FILE_PATH, "empty.md")

        if not shutil.which("pandoc"):
            # Case where pandoc is not installed
            with self.assertRaises(Exception) as context_manager:
                self.pandoc_reader.read(source_path)

            message = str(context_manager.exception)
            self.assertEqual("Could not find Pandoc. Please install.", message)
        else:
            # Case where pandoc is installed
            self.assertTrue("Pandoc is installed.")

    def test_empty_file(self):
        """Check if a file is empty."""
        source_path = os.path.join(FILE_PATH, "empty.md")

        # If the file is empty retrieval of metadata should fail
        with self.assertRaises(Exception) as context_manager:
            self.pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find metadata. File is empty", message)

    def test_non_empty_file_no_metadata(self):
        """Check if a file has no metadata."""
        source_path = os.path.join(FILE_PATH, "no_metadata.md")

        # If the file is not empty but has no metadata it should fail
        with self.assertRaises(Exception) as context_manager:
            self.pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find metadata header '---' or '...'", message)

    def test_metadata_block_end(self):
        """Check if the metadata block ends."""
        source_path = os.path.join(FILE_PATH, "no_metadata_end.md")

        # Metadata blocks should end with '___' or '...' if not it should fail
        with self.assertRaises(Exception) as context_manager:
            self.pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find end of metadata block.", message)

    def test_invalid_metadata_block_end(self):
        """Check if the metadata block end is wrong."""
        source_path = os.path.join(FILE_PATH, "no_metadata_end.md")

        # Metadata blocks should end with '___' or '...' if not it should fail
        with self.assertRaises(Exception) as context_manager:
            self.pandoc_reader.read(source_path)

        message = str(context_manager.exception)
        self.assertEqual("Could not find end of metadata block.", message)


if __name__ == "__main__":
    unittest.main()
