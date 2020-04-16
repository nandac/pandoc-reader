"""Reader that processes Pandoc Markdown and returns HTML 5."""
import subprocess

from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open

ENCODED_LINK_TO_RAW_LINK_MAP = {
    "%7Bstatic%7D": "{static}",
    "%7Battach%7D": "{attach}",
    "%7Bfilename%7D": "{filename}"
}


class PandocReader(BaseReader):
    """Process files written in Pandoc Markdown."""

    enabled = True
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def read(self, source_path):
        """Parse Pandoc Markdown and return HTML 5 output and metadata."""
        content = ""

        with pelican_open(source_path) as file_content:
            content = file_content

        # Parse metadata
        metadata = self._process_metadata(list(content.splitlines()))

        # Get arguments and extensions
        extra_args = self.settings.get('PANDOC_ARGS', [])
        extensions = self.settings.get('PANDOC_EXTENSIONS', '')
        if isinstance(extensions, list):
            extensions = ''.join(extensions)

        # Construct Pandoc command
        pandoc_cmd = [
            "pandoc", "-f", "markdown" + extensions, "-t", "html5"
        ]
        pandoc_cmd.extend(extra_args)

        # Execute and retrieve HTML 5 output
        proc = subprocess.Popen(
            pandoc_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

        output = proc.communicate(content.encode('utf-8'))[0].decode('utf-8')
        status = proc.wait()
        if status:
            raise subprocess.CalledProcessError(status, pandoc_cmd)

        # Replace all occurrences of %7Bstatic%7D to {static},
        # %7Battach%7D to {attach} and %7Bfilename%7D to {filename}
        # so that static links are resolved by pelican
        for encoded_str, raw_str in ENCODED_LINK_TO_RAW_LINK_MAP.items():
            output = output.replace(encoded_str, raw_str)

        return output, metadata

    def _process_metadata(self, text):
        """Process YAML metadata and export."""
        metadata = {}

        # Check that the first line of the file
        # starts with a YAML header
        if text[0].strip() not in ["---", "..."]:
            raise Exception("Could not find metadata header '---' or '...'")

        # Find the end of the YAML block
        lines = text[1:]
        yaml_end = ""
        for line_num, line in enumerate(lines):
            if line.strip() in ["---", "..."]:
                yaml_end = line_num
                break

        # Check if the end of the YAML block was found
        if not yaml_end:
            raise Exception("Could not find end of metadata block.")

        # Process the YAML block
        for line in lines[:yaml_end]:
            metalist = line.split(':', 1)
            if len(metalist) == 2:
                key, value = metalist[0].lower(), metalist[1].strip()
                metadata[key] = self.process_metadata(key, value)
        return metadata


def add_reader(readers):
    """Add the PandocReader as the reader for all Pandoc Markdown files."""
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader


def register():
    """Register the PandocReader."""
    signals.readers_init.connect(add_reader)
