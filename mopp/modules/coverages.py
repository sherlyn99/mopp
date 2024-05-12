import logging
from micov._modules import cli_compress
from mopp.modules.utils import create_folder_without_clear

POLARS_SKIP_CPU_CHECK = True
logger = logging.getLogger("mopp")


def calculate_coverages(input_dir, output_dir, genome_lengths):
    create_folder_without_clear(output_dir)

    cli_compress(
        input_dir,
        output_dir,
        genome_lengths,
        disable_compression=False,
        skip_intermediate=True,
    )


if __name__ == "__main__":
    calculate_coverages()
