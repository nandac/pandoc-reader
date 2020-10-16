"""Tests for pandoc-reader plugin."""
import os
import unittest

from pandoc_reader import PandocReader


class TestPandocReader(unittest.TestCase):
    """Test class for pandoc-reader plugin."""

    def test_pandoc_installed(self):
        """Check if Pandoc is installed."""
        with self.assertRaises(Exception) as context:
            PandocReader.read(os.getcwd())
        self.assertTrue("Could not find Pandoc. Please install." in context.exception)


if __name__ == "__main__":
    unittest.main()
