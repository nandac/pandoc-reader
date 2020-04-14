"""Reader that processes Pandoc Markdown and returns HTML 5."""
import subprocess

from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open


class PandocReader(BaseReader):
    """Process files written in Pandoc Markdown."""

    enabled = True
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def read(self, source_path):
        """Parse Pandoc Markdown and return HTNL 5 output and metadata."""
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

        return output, metadata

    def _process_metadata(self, text):
        """Process YAML metadata and export."""
        metadata = {}

        # Find the end of the YAML block
        lines = text[1:]
        yaml_end = ""
        for line_num, line in enumerate(lines):
            if line in ["---", "..."]:
                yaml_end = line_num
                break

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
