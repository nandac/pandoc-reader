"""Tests for pandoc-reader plugin."""
import os
import unittest

from pandoc_reader import PandocReader


class TestPandocReader(unittest.TestCase):
    """Test class for pandoc-reader plugin."""

    def test_pandoc_installed(self):
        """Check if Pandoc is installed."""
        self.assertRaises(Exception, PandocReader.read(), os.getcwd())
        with self.assertRaises(TypeError) as context:
            PandocReader.read(os.getcwd())
        self.assertEqual(
            "Could not find Pandoc. Please install.", str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
