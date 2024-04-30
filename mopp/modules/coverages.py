import logging
from pathlib import Path
from micov._modules import cli_compress


logger = logging.getLogger("mopp")


def calculate_coverages(input_dir, output_dir, genome_lengths):

    cli_compress(
        input_dir,
        output_dir,
        genome_lengths,
        disable_compression=False,
        skip_intermediate=True,
    )


if __name__ == "__main__":
    calculate_coverages()
