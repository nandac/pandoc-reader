"""Reader that processes Pandoc Markdown and returns HTML 5."""
import os
import shutil
import subprocess

from pelican.readers import BaseReader
from pelican.utils import pelican_open
from yaml import safe_load

from pelican import signals

DIR_PATH = os.path.dirname(__file__)
TEMPLATES_PATH = os.path.abspath(os.path.join(DIR_PATH, "templates"))
TOC_TEMPLATE = "toc-template.html"

ENCODED_LINKS_TO_RAW_LINKS_MAP = {
    "%7Bstatic%7D": "{static}",
    "%7Battach%7D": "{attach}",
    "%7Bfilename%7D": "{filename}",
}

VALID_INPUT_FORMATS = ("markdown", "commonmark", "gfm")
VALID_OUTPUT_FORMATS = ("html", "html5")
UNSUPPORTED_ARGUMENTS = ("--standalone", "--self-contained")
VALID_BIB_EXTENSIONS = ["json", "yaml", "bibtex", "bib"]
FILE_EXTENSIONS = ["md", "markdown", "mkd", "mdown"]


class PandocReader(BaseReader):
    """Convert files written in Pandoc Markdown to HTML 5."""

    enabled = True
    file_extensions = FILE_EXTENSIONS

    def read(self, source_path):
        """Parse Pandoc Markdown and return HTML5 markup and metadata."""
        # Check if pandoc is installed and is executable
        if not shutil.which("pandoc"):
            raise Exception("Could not find Pandoc. Please install.")

        # Open markdown file and read content
        content = ""
        with pelican_open(source_path) as file_content:
            content = file_content

        # Retrieve HTML content and metadata
        output, metadata = self.create_html(source_path, content)

        return output, metadata

    def create_html(self, source_path, content):
        """Creates HTML5 content and takes care of citations and toc."""
        # Get settings set in pelicanconf.py
        default_files = self.settings.get("PANDOC_DEFAULT_FILES", [])
        arguments = self.settings.get("PANDOC_ARGS", [])
        extensions = self.settings.get("PANDOC_EXTENSIONS", [])

        if isinstance(extensions, list):
            extensions = "".join(extensions)

        # Check validity of arguments or default files
        if not default_files:
            self.check_arguments(arguments)
            citations = self.check_if_citations(arguments, extensions)
            table_of_contents = self.check_if_toc(arguments)
        else:
            citations, table_of_contents = self.check_defaults(default_files)

        # Construct preliminary pandoc command
        pandoc_cmd = []
        if not default_files:
            pandoc_cmd = ["pandoc", "--from", "markdown" + extensions, "--to", "html5"]
            pandoc_cmd.extend(arguments)
        else:
            pandoc_cmd.append("pandoc")
            for default_file in default_files:
                pandoc_cmd.append("--defaults={0}".format(default_file))

        # Find and add bibliography if citations are specified
        if citations:
            bib_files = self.find_bibs(source_path)
            for bib_file in bib_files:
                pandoc_cmd.append("--bibliography={0}".format(bib_file))

        # Create HTML content
        output = self.run_pandoc(pandoc_cmd, content)

        # Replace all occurrences of %7Bstatic%7D to {static},
        # %7Battach%7D to {attach} and %7Bfilename%7D to {filename}
        # so that static links are resolvable by pelican
        for encoded_str, raw_str in ENCODED_LINKS_TO_RAW_LINKS_MAP.items():
            output = output.replace(encoded_str, raw_str)

        # Create table of contents if specified
        toc = None
        if table_of_contents:
            toc = self.create_toc(pandoc_cmd, content)

        # Parse YAML metadata and add the table of contents to the metadata
        metadata = self._process_metadata(list(content.splitlines()), toc)

        return output, metadata

    @staticmethod
    def run_pandoc(pandoc_cmd, content):
        """Execute the given pandoc command and return output."""
        output = subprocess.run(
            pandoc_cmd, input=content, capture_output=True, encoding="UTF-8", check=True
        )
        return output.stdout

    def create_toc(self, pandoc_cmd, content):
        """Generate table of contents."""
        toc_args = [
            "--standalone",
            "--template",
            os.path.join(TEMPLATES_PATH, TOC_TEMPLATE),
        ]

        pandoc_cmd = pandoc_cmd + toc_args
        table_of_contents = self.run_pandoc(pandoc_cmd, content)
        return table_of_contents

    def _process_metadata(self, text, table_of_contents=None):
        """Process YAML metadata and export."""
        metadata = {}

        # Check that the given text is not empty
        if not text:
            raise Exception("Could not find metadata. File is empty.")

        # Check that the first line of the file starts with a YAML header
        if text[0].strip() not in ["---", "..."]:
            raise Exception("Could not find metadata header '...' or '---'.")

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
            metalist = line.split(":", 1)
            if len(metalist) == 2:
                key, value = metalist[0].lower(), metalist[1].strip().strip('"')
                metadata[key] = self.process_metadata(key, value)

        # Add the table of contents as a metadata field
        if table_of_contents:
            metadata["toc"] = self.process_metadata("toc", table_of_contents)
        return metadata

    @staticmethod
    def check_if_citations(arguments, extensions):
        """Check if citations are specified."""
        citations = False
        if arguments and extensions:
            if (
                "--citeproc" in arguments or "-C" in arguments
            ) and "+citations" in extensions:
                citations = True
        return citations

    @staticmethod
    def check_if_toc(arguments):
        """Check if a table of contents should be generated."""
        table_of_contents = False
        if arguments:
            if "--toc" in arguments or "--table-of-contents" in arguments:
                table_of_contents = True
        return table_of_contents

    @staticmethod
    def find_bibs(source_path):
        """Find bibliographies recursively in the sourcepath given."""
        bib_files = []
        filename = os.path.splitext(os.path.basename(source_path))[0]
        directory_path = os.path.dirname(os.path.abspath(source_path))
        for root, _, files in os.walk(directory_path):
            for extension in VALID_BIB_EXTENSIONS:
                bib_name = ".".join([filename, extension])
                if bib_name in files:
                    bib_files.append(os.path.join(root, bib_name))
        return bib_files

    @staticmethod
    def check_arguments(arguments):
        """Check to see that only supported arguments have been passed."""
        for arg in arguments:
            if arg in UNSUPPORTED_ARGUMENTS:
                raise ValueError("Argument {0} is not supported.".format(arg))

    def check_defaults(self, default_files):
        """Check if the given Pandoc defaults file has valid values."""
        citations = False
        table_of_contents = False
        for default_file in default_files:
            defaults = {}

            # Convert YAML data to a Python dictionary
            with open(default_file) as file_handle:
                defaults = safe_load(file_handle)

            self.check_if_unsupported_settings(defaults)
            reader = self.check_input_format(defaults)
            self.check_output_format(defaults)

            if not citations:
                if defaults.get("citeproc", "") and "+citations" in reader:
                    citations = True

            if not table_of_contents:
                if defaults.get("table-of-contents", ""):
                    table_of_contents = True

        return citations, table_of_contents

    @staticmethod
    def check_if_unsupported_settings(defaults):
        """Check if unsupported settings are specified in the defaults."""
        for arg in UNSUPPORTED_ARGUMENTS:
            arg = arg[2:]
            if defaults.get(arg, ""):
                raise ValueError("The default {} should be set to false.".format(arg))

    @staticmethod
    def check_input_format(defaults):
        """Check if the input format given is a Markdown variant."""
        reader = ""
        reader_input = defaults.get("reader", "")
        from_input = defaults.get("from", "")

        # Case where no input format is specified
        if not reader_input and not from_input:
            raise ValueError("No input format specified.")

        # Case where both reader and from are specified which is not supported
        if reader_input and from_input:
            raise ValueError(
                (
                    "Specifying both from and reader is not supported."
                    " Please specify just one."
                )
            )

        if reader_input or from_input:
            if reader_input:
                reader = reader_input
            elif from_input:
                reader = from_input

            reader_prefix = reader.replace("+", "-").split("-")[0]

            # Check to see if the reader_prefix matches a valid input
            if not reader_prefix.startswith(VALID_INPUT_FORMATS):
                raise ValueError("Input type has to be a markdown variant.")
        return reader

    @staticmethod
    def check_output_format(defaults):
        """Check if the output format is HTML or HTML5."""
        writer_output = defaults.get("writer", "")
        to_output = defaults.get("to", "")

        # Case where both writer and to are specified which is not supported
        if writer_output and to_output:
            raise ValueError(
                (
                    "Specifying both to and writer is not supported."
                    " Please specify just one."
                )
            )

        # Case where neither writer nor to value is set to html
        if (
            writer_output not in VALID_OUTPUT_FORMATS
            and to_output not in VALID_OUTPUT_FORMATS
        ):
            output_formats = " or ".join(VALID_OUTPUT_FORMATS)
            raise ValueError(
                "Output format type must be either {}.".format(output_formats)
            )


def add_reader(readers):
    """Add the PandocReader as the reader for all Pandoc Markdown files."""
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader


def register():
    """Register the PandocReader."""
    signals.readers_init.connect(add_reader)
