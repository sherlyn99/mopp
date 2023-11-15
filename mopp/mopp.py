import time
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
)
from mopp.modules.trim import trim_files
from mopp.modules.align import align_files
from mopp.modules.coverages import calculate_genome_coverages
from mopp.modules.index import genome_extraction
from mopp.modules.features import ft_generation


logger = logging.getLogger("mopp")
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")


@click.group(help=MSG_WELCOME)
def mopp():
    pass


@mopp.command(help=MSG_WELCOME_WORKFLOW)
@click.option("-i", "--input_dir", required=True, help=DESC_INPUT)
@click.option("-o", "--output_dir", required=True, help=DESC_OUTPUT)
@click.option("-m", "--metadata", required=True, help=DESC_MD)
@click.option("-x", "--index", required=True, help=DESC_INDEX)  # wol bt2 index
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
@click.option("-z", "--zebra", required=True, help="DESC_ZEBRA")
@click.option("-c", "--cutoff", type=float, required=True, help="DESC_CUTOFF")
@click.option("-ref", "--refdb", required=True, help="DESC_REFDB")  # index wol.fna
@click.option("-p", "--prefix", required=True, help="DESC_PREFIX")  # index prefix
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
def workflow(
    input_dir,
    output_dir,
    metadata,
    index,
    threads,
    zebra,
    cutoff,
    refdb,
    prefix,
    rank,
    woltka_database,
    stratification,
):
    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(f"mopp_{timestamp}.log")
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        outdir_trimmed = Path(output_dir) / "trimmed"
        outdir_aligned_metaG = Path(output_dir) / "aligned_metaG"
        outdir_aligned_metaG_samfiles = outdir_aligned_metaG / "samfiles"
        outdir_aligned = Path(output_dir) / "aligned"
        outdir_aligned_samfiles = outdir_aligned_metaG / "samfiles"
        outdir_cov = Path(output_dir) / "coverages"
        outdir_cov_file = Path(output_dir) / "coverages" / "coverages.tsv"
        outdir_index = Path(output_dir) / "index"
        outdir_index_path = outdir_index / f"{prefix}_bt2index" / prefix
        outdir_features = Path(output_dir) / "features"

        trim_files(input_dir, outdir_trimmed, metadata)
        align_files(
            outdir_trimmed, outdir_aligned_metaG, "*metaG*.fq.gz", index, threads
        )
        calculate_genome_coverages(zebra, outdir_aligned_metaG_samfiles, outdir_cov)
        genome_extraction(outdir_cov_file, cutoff, refdb, outdir_index, prefix)
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
@click.option("-i", "--input_dir", required=True, help=DESC_INPUT)
@click.option("-o", "--output_dir", required=True, help=DESC_OUTPUT)
@click.option("-m", "--metadata", required=True, help=DESC_MD)
def trim(input_dir, output_dir, metadata):
    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(f"mopp_{timestamp}.log")
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        trim_files(input_dir, output_dir, metadata)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
@click.option("-i", "--input_dir", required=True, help="DESC_INPUT_TRIMMED")
@click.option("-o", "--output_dir", required=True, help=DESC_OUTPUT)
@click.option("-p", "--pattern", required=True, help=DESC_PATTERN)
@click.option("-x", "--index", required=True, help=DESC_INDEX)
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
def align(input_dir, output_dir, pattern, index, threads):
    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(f"mopp_{timestamp}.log")
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        align_files(input_dir, output_dir, pattern, index, threads)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
@click.option("-i", "--input_dir", required=True, help=DESC_INPUT_SAM)
@click.option("-o", "--output_dir", required=True, help=DESC_OUTPUT)
@click.option("-z", "--zebra", required=True, help="DESC_ZEBRA")
def cov(input_dir, output_dir, zebra):
    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(f"mopp_{timestamp}.log")
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        calculate_genome_coverages(zebra, input_dir, output_dir)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
@click.option("-i", "--input_cov", required=True, help="DESC_INPUT_COV")
@click.option("-c", "--cutoff", type=float, required=True, help="DESC_CUTOFF")
@click.option("-ref", "--refdb", required=True, help="DESC_REFDB")
@click.option("-o", "--output_dir", required=True, help=DESC_OUTPUT)
@click.option("-p", "--prefix", required=True, help="DESC_PREFIX")
def generate_index(input_cov, cutoff, refdb, output_dir, prefix):
    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(f"mopp_{timestamp}.log")
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        genome_extraction(input_cov, cutoff, refdb, output_dir, prefix)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
@click.option("-i", "--input_dir", required=True, help=DESC_INPUT_SAM)
@click.option("-o", "--output_dir", required=True, help=DESC_OUTPUT)
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
    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(f"mopp_{timestamp}.log")
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    rank_list = [s.strip() for s in rank.split(",")]

    try:
        ft_generation(input_dir, output_dir, woltka_database, rank_list, stratification)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


if __name__ == "__main__":
    mopp()
