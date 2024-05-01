import sys
import click
import logging
from pathlib import Path
from mopp._defaults import (
    MSG_WELCOME,
    MSG_WELCOME_WORKFLOW,
    DESC_MD,
    DESC_INPUT,
    DESC_INPUT_SAM,
    DESC_OUTPUT,
    DESC_INDEX,
    DESC_NTHREADS,
    DESC_RANK,
    DESC_STRAT,
    DESC_WOLTKA_DB,
    DESC_PATTERN,
    DESC_GENOME_LENGTHS,
    DESC_CUTOFF,
    DESC_INPUT_TRIMMED,
    DESC_PREFIX,
    DESC_REFDB,
    DESC_INPUT_COV,
)
from mopp.modules.trim import trim_files
from mopp.modules.align import align_files
from mopp.modules.coverages import calculate_coverages
from mopp.modules.index import genome_extraction
from mopp.modules.features import ft_generation
from mopp.modules.utils import create_folder_without_clear, logger_setup


my_logger = logging.getLogger("mopp")


@click.group(help=MSG_WELCOME)
def mopp():
    pass


@mopp.command(help=MSG_WELCOME_WORKFLOW)
# fmt: off
@click.option("-i", "--input-dir", required=True, help=DESC_INPUT)
@click.option("-o", "--output-dir", required=True, help=DESC_OUTPUT)
@click.option("-m", "--metadata", required=True, help=DESC_MD)
@click.option("-x", "--index", required=True, help=DESC_INDEX)  # wol bt2 index
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
@click.option("-g", "--genome-lengths", type=click.Path(exists=True), required=True, help=DESC_GENOME_LENGTHS)
@click.option("-c", "--cutoff", type=float, required=True, help=DESC_CUTOFF)
@click.option("-ref", "--refdb", required=True, help=DESC_REFDB)  # index wol.fna
@click.option("-p", "--prefix", required=True, help=DESC_PREFIX)  # index prefix
@click.option(
    "-r",
    "--rank",
    type=click.Choice(["species", "genus", "genus,species"]),
    required=True,
    help=DESC_RANK,
)
@click.option(
    "-db", "--woltka_database", required=True, help=DESC_WOLTKA_DB
)  # woltka db (wol-20April2021)
@click.option(
    "-strat", "--stratification", is_flag=True, default=False, help=DESC_STRAT
)
# fmt: on
def workflow(
    input_dir,
    output_dir,
    metadata,
    index,
    threads,
    genome_lengths,
    cutoff,
    refdb,
    prefix,
    rank,
    woltka_database,
    stratification,
):
    create_folder_without_clear(Path(output_dir))
    logger = logger_setup(my_logger, output_dir)

    try:
        outdir_trimmed = Path(output_dir) / "cat"
        outdir_aligned_metaG = Path(output_dir) / "aligned_metaG"
        outdir_aligned_metaG_samfiles = outdir_aligned_metaG / "samfiles"
        outdir_aligned = Path(output_dir) / "aligned"
        outdir_aligned_samfiles = outdir_aligned_metaG / "samfiles"
        outdir_cov = Path(output_dir) / "coverages"
        outdir_cov_file = Path(output_dir) / "coverages" / "coverage_percentage.txt"
        outdir_index = Path(output_dir) / "index"
        outdir_index_path = outdir_index / f"{prefix}_bt2index" / prefix
        outdir_features = Path(output_dir) / "features"

        trim_files(input_dir, outdir_trimmed, metadata, threads)
        align_files(
            outdir_trimmed, outdir_aligned_metaG, "*metaG*.fq.gz", index, threads
        )
        calculate_coverages(
            str(outdir_aligned_metaG_samfiles), str(outdir_cov), genome_lengths
        )
        genome_extraction(outdir_cov_file, cutoff, refdb, outdir_index, prefix, threads)
        align_files(
            outdir_trimmed, outdir_aligned, "*.fq.gz", str(outdir_index_path), threads
        )
        rank_list = [s.strip() for s in rank.split(",")]
        ft_generation(
            outdir_aligned_samfiles,
            outdir_features,
            woltka_database,
            rank_list,
            stratification,
        )
        logger.info("Workflow finished")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
@click.option("-i", "--input-dir", required=True, help=DESC_INPUT)
@click.option("-o", "--output-dir", required=True, help=DESC_OUTPUT)
@click.option("-m", "--metadata", required=True, help=DESC_MD)
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
def trim(input_dir, output_dir, metadata, threads):
    create_folder_without_clear(Path(output_dir))

    logger = logger_setup(my_logger, output_dir)

    try:
        trim_files(input_dir, output_dir, metadata, threads)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
@click.option("-i", "--input-dir", required=True, help=DESC_INPUT_TRIMMED)
@click.option("-o", "--output-dir", required=True, help=DESC_OUTPUT)
@click.option("-p", "--pattern", required=True, help=DESC_PATTERN)
@click.option("-x", "--index", required=True, help=DESC_INDEX)
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
def align(input_dir, output_dir, pattern, index, threads):
    create_folder_without_clear(Path(output_dir))

    logger = logger_setup(my_logger, output_dir)

    try:
        align_files(input_dir, output_dir, pattern, index, threads)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
# fmt: off
@click.option("-i", "--input-dir", type=click.Path(exists=True), required=True, help=DESC_INPUT_SAM,)
@click.option("-o", "--output-dir", type=click.Path(exists=False), required=True, help=DESC_OUTPUT)
@click.option("-g", "--genome-lengths", type=click.Path(exists=True), required=True, help=DESC_GENOME_LENGTHS)
# fmt: on
def cov(input_dir, output_dir, genome_lengths):
    create_folder_without_clear(output_dir)
    logger = logger_setup(my_logger, output_dir)

    logger.info("Calculation of genome covarges started.")
    try:
        calculate_coverages(input_dir, output_dir, genome_lengths)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
    else:
        logger.info("Calculation of genome covarges finished.")


@mopp.command()
@click.option("-i", "--input-cov", required=True, help=DESC_INPUT_COV)
@click.option("-c", "--cutoff", type=float, required=True, help=DESC_CUTOFF)
@click.option("-ref", "--refdb", required=True, help=DESC_REFDB)
@click.option("-o", "--output-dir", required=True, help=DESC_OUTPUT)
@click.option("-p", "--prefix", required=True, help=DESC_PREFIX)
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
def generate_index(input_cov, cutoff, refdb, output_dir, prefix, threads):
    create_folder_without_clear(Path(output_dir))

    logger = logger_setup(my_logger, output_dir)

    try:
        genome_extraction(input_cov, cutoff, refdb, output_dir, prefix, threads)

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
@click.option("-i", "--input-dir", required=True, help=DESC_INPUT_SAM)
@click.option("-o", "--output-dir", required=True, help=DESC_OUTPUT)
@click.option(
    "-r",
    "--rank",
    type=click.Choice(["species", "genus", "genus,species"]),
    required=True,
    help=DESC_RANK,
)
@click.option("-db", "--woltka_database", required=True, help=DESC_WOLTKA_DB)
@click.option(
    "-strat", "--stratification", is_flag=True, default=False, help=DESC_STRAT
)
def feature_table(rank, input_dir, output_dir, woltka_database, stratification):
    create_folder_without_clear(Path(output_dir))

    logger = logger_setup(my_logger, output_dir)

    rank_list = [s.strip() for s in rank.split(",")]

    try:
        ft_generation(input_dir, output_dir, woltka_database, rank_list, stratification)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


if __name__ == "__main__":
    mopp()
