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


class PandocReader(BaseReader):
    """Process files written in Pandoc Markdown."""

    enabled = True
    file_extensions = ["md", "markdown", "mkd", "mdown"]

    def read(self, source_path):
        """Parse Pandoc Markdown and return HTML 5 output and metadata."""
        # Check if pandoc is installed and is executable
        if not shutil.which("pandoc"):
            raise Exception("Could not find Pandoc. Please install.")

        content = ""
        with pelican_open(source_path) as file_content:
            content = file_content

        generate_table_of_contents = False
        metadata = ""
        pandoc_cmd = []

        # Get arguments and extensions
        if not self.settings.get("PANDOC_DEFAULT_FILES"):
            arguments = self.settings.get("PANDOC_ARGS", [])
            extensions = self.settings.get("PANDOC_EXTENSIONS", "")
            if isinstance(extensions, list):
                extensions = "".join(extensions)

            # Construct Pandoc command
            pandoc_cmd = [
                "pandoc",
                "--from",
                "markdown" + extensions,
                "--to",
                "html5",
            ]

            self.check_arguments(arguments)

            # Check if we should generate a table of contents
            if "--toc" in arguments:
                generate_table_of_contents = True
            elif "--table-of-contents" in arguments:
                generate_table_of_contents = True

            pandoc_cmd.extend(arguments)
        else:
            default_files_cmd = []
            for filepath in self.settings.get("PANDOC_DEFAULT_FILES"):
                defaults = self.check_defaults(filepath)

                # Check if we need to generate a table of contents
                if not generate_table_of_contents:
                    if defaults.get("table-of-contents", ""):
                        generate_table_of_contents = True

                default_files_cmd.append("--defaults={0}".format(filepath))
            # Construct Pandoc command
            pandoc_cmd = ["pandoc"] + default_files_cmd

        # Generate HTML
        output = self.run_pandoc(pandoc_cmd, content)

        # Replace all occurrences of %7Bstatic%7D to {static},
        # %7Battach%7D to {attach} and %7Bfilename%7D to {filename}
        # so that static links are resolvable by pelican
        for encoded_str, raw_str in ENCODED_LINKS_TO_RAW_LINKS_MAP.items():
            output = output.replace(encoded_str, raw_str)

        # Generate a table of contents if the variable below was set to true
        if generate_table_of_contents:
            # The table of contents is generated using a template which
            # takes effect only in standalone mode
            gen_toc_extra_args = [
                "--standalone",
                "--template",
                os.path.join(TEMPLATES_PATH, TOC_TEMPLATE),
            ]

            # Generate the table of contents
            pandoc_gen_toc_cmd = pandoc_cmd + gen_toc_extra_args
            table_of_contents = self.run_pandoc(pandoc_gen_toc_cmd, content)

            # Parse YAML metadata and add the table of contents to the metadata
            metadata = self._process_metadata(
                list(content.splitlines()), table_of_contents
            )
        else:
            # Parse YAML metadata
            metadata = self._process_metadata(list(content.splitlines()))

        return output, metadata

    @staticmethod
    def run_pandoc(pandoc_cmd, content):
        # Execute Pandoc command
        proc = subprocess.Popen(
            pandoc_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

        # retrieve HTML 5 output
        output = proc.communicate(content.encode("UTF-8"))[0].decode("UTF-8")
        status = proc.wait()
        if status:
            raise subprocess.CalledProcessError(status, pandoc_cmd)
        return output

    @staticmethod
    def check_arguments(arguments):
        """Check to see that only supported arguments have been passed."""
        for argument in arguments:
            if argument in UNSUPPORTED_ARGUMENTS:
                raise ValueError("Argument {0} is not supported.".format(argument))

    @staticmethod
    def check_defaults(filepath):
        """Check if the given Pandoc defaults file has valid values."""
        defaults = {}

        # Convert YAML data to a Python dictionary
        with open(filepath) as defaults_file:
            defaults = safe_load(defaults_file)

        standalone = defaults.get("standalone", "")
        self_contained = defaults.get("self-contained", "")

        # Raise an exception if standalone is true
        if standalone:
            raise ValueError("The default standalone should be set to false.")

        # Raise an exception if self-contained is true
        if self_contained:
            raise ValueError("The default self-contained should be set to false.")

        reader_input = defaults.get("reader", "")
        from_input = defaults.get("from", "")

        # Case where no input format is specified
        if not reader_input and not from_input:
            raise ValueError("No input format specified.")

        # Case where reader is specified
        if reader_input and not from_input:
            reader_prefix = reader_input.replace("+", "-").split("-")[0]

            # Check to see if the reader_prefix matches a valid input type
            if not reader_prefix.startswith(VALID_INPUT_FORMATS):
                raise ValueError("Input type has to be a markdown variant.")

        # Case where from is specified
        if not reader_input and from_input:
            reader_prefix = from_input.replace("+", "-").split("-")[0]

            # Check to see if the reader_prefix matches a valid input type
            if not reader_prefix.startswith(VALID_INPUT_FORMATS):
                raise ValueError("Input type has to be a markdown variant.")

        # Case where both reader and from are specified which is not supported
        if reader_input and from_input:
            raise ValueError(
                (
                    "Specifying both from and reader is not supported."
                    " Please specify just one."
                )
            )

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
            raise ValueError("Output format type must be html or html5.")
        return defaults

    def _process_metadata(self, text, table_of_contents=""):
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

        # Add the table of contents to the content's metadata
        if table_of_contents:
            metadata["toc"] = self.process_metadata("toc", table_of_contents)
        return metadata


def add_reader(readers):
    """Add the PandocReader as the reader for all Pandoc Markdown files."""
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader


def register():
    """Register the PandocReader."""
    signals.readers_init.connect(add_reader)
