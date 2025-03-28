import time
import click
import logging
from pathlib import Path
from mopp._defaults import (
    MSG_WELCOME,
    MSG_WELCOME_WORKFLOW,
    MSG_WELCOME_METADATA,
    DESC_MD,
    DESC_MD_OR_DIR,
    DESC_MD_OUTPUT,
    DESC_INPUT,
    DESC_INPUT_SAM,
    DESC_OUTPUT,
    DESC_VALIDATE_PAIRED_END,
    DESC_VALIDATE_MULTIOMICS,
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
    DESC_COMPRESS_SAM,
    DESC_SUFFIX,
    DESC_COORDS_MAP,
    DESC_TAX_MAP,
    DESC_FUNC_MAP,
    DESC_DIVIDE,
    DESC_LOG_TRANSFORM
)
from mopp.modules.metadata import (
    autogenerate_metadata,
    validate_metadata,
    load_metadata_to_df_with_validation,
)
from mopp.modules.trim import trim_files
from mopp.modules.align import align_files
from mopp.modules.coverages import calculate_coverages
from mopp.modules.index import genome_extraction
from mopp.modules.features_wol import ft_generation
from mopp.modules.utils import create_folder_without_clear
from mopp.modules.features import gen_feature_table


logger = logging.getLogger("mopp")
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
formatter = logging.Formatter(
    "%(asctime)s-%(name)s-%(levelname)s: %(message)s"
)


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
@click.option("-l", "--genome-lengths", type=click.Path(exists=True), required=True, help=DESC_GENOME_LENGTHS)
@click.option("-c", "--cutoff", type=float, required=True, help=DESC_CUTOFF)
@click.option("-ref", "--refdb", required=True, help=DESC_REFDB)  # index wol.fna
@click.option("-p", "--prefix", required=True, help=DESC_PREFIX)  # index prefix
@click.option("-b", "--log-transform", is_flag=True, default=False, help=DESC_LOG_TRANSFORM)
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
    log_transform,
    rank,
    woltka_database,
    stratification,
):
    create_folder_without_clear(Path(output_dir))

    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(
        f"{output_dir}/mopp_workflow_{timestamp}.log"
    )
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
        outdir_aligned_samfiles = outdir_aligned / "samfiles"
        outdir_cov = Path(output_dir) / "coverages"
        outdir_cov_file = (
            Path(output_dir) / "coverages" / "coverage_calculation.tsv"
        )
        outdir_index = Path(output_dir) / "index"
        outdir_index_path = outdir_index / f"{prefix}_bt2index" / prefix
        outdir_features = Path(output_dir) / "features"

        trim_files(input_dir, outdir_trimmed, metadata, threads)
        align_files(
            outdir_trimmed,
            outdir_aligned_metaG,
            "*metaG*.fq.gz",
            index,
            threads,
        )
        calculate_coverages(
            str(outdir_aligned_metaG_samfiles), str(outdir_cov), genome_lengths, log_transform
        )
        genome_extraction(
            outdir_cov_file, cutoff, refdb, outdir_index, prefix, threads
        )
        align_files(
            outdir_trimmed,
            outdir_aligned,
            "*.fq.gz",
            str(outdir_index_path),
            threads,
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


@mopp.command(help=MSG_WELCOME_METADATA)
@click.option("-i", "--input", required=True, help=DESC_MD_OR_DIR)
@click.option("-o", "--outpath", required=False, help=DESC_MD_OUTPUT)
@click.option(
    "-p",
    "--paired-end",
    is_flag=True,
    default=False,
    help=DESC_VALIDATE_PAIRED_END,
)
@click.option(
    "-m",
    "--multiomics",
    is_flag=True,
    default=False,
    help=DESC_VALIDATE_MULTIOMICS,
)
def metadata(input, outpath, paired_end, multiomics):
    if Path(input).is_dir():
        # create and validate metadata
        if outpath:
            output_dir = Path(outpath).parents[0]
            output_path = Path(outpath)
        else:
            output_dir = Path(input)  # for log files
            output_path = Path(input) / "metadata_auto.tsv"
    else:
        # just validate metadata, no output
        output_dir = Path(input).parents[0]  # for log files

    create_folder_without_clear(output_dir)

    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(
        f"{str(output_dir)}/mopp_metadata_{timestamp}.log"
    )
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if Path(input).is_dir():
        # create and validate metadata
        logger.info("Input directory detected. Auto-generating metadata...")
        md_df = autogenerate_metadata(input)

        logger.info("Metadata auto-generated. Validating...")
        validate_metadata(md_df, paired_end, multiomics)

        logger.info("Metadata validated.")

        md_df.to_csv(output_path, sep="\t", index=False, header=True)
        logger.info(f"Metadata written to {output_path}.")
    else:
        # just validate metadata
        md_df = load_metadata_to_df_with_validation(
            input, paired_end, multiomics
        )
        logger.info("Metadata validated.")


@mopp.command()
@click.option("-i", "--input-dir", required=True, help=DESC_INPUT)
@click.option("-o", "--output-dir", required=True, help=DESC_OUTPUT)
@click.option("-m", "--metadata", required=True, help=DESC_MD)
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
def trim(input_dir, output_dir, metadata, threads):
    create_folder_without_clear(Path(output_dir))

    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(
        f"{output_dir}/mopp_trim_{timestamp}.log"
    )
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

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
@click.option("--compress-samfiles", is_flag=True, help=DESC_COMPRESS_SAM)
def align(input_dir, output_dir, pattern, index, threads, compress_samfiles):
    create_folder_without_clear(Path(output_dir))

    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(
        f"{output_dir}/mopp_align_{timestamp}.log"
    )
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        align_files(
            input_dir,
            output_dir,
            pattern,
            index,
            threads,
            compress=compress_samfiles,
        )
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


@mopp.command()
# fmt: off
@click.option("-i", "--input-dir", type=click.Path(exists=True), required=True, help=DESC_INPUT_SAM,)
@click.option("-o", "--output-dir", type=click.Path(exists=False), required=True, help=DESC_OUTPUT)
@click.option("-l", "--genome-lengths", type=click.Path(exists=True), required=True, help=DESC_GENOME_LENGTHS)
@click.option("-b", "--log-transform", is_flag=True, default=False, help=DESC_LOG_TRANSFORM)
# fmt: on
def cov(input_dir, output_dir, genome_lengths, log_transform):
    create_folder_without_clear(output_dir)

    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(
        f"{output_dir}/mopp_cov_{timestamp}.log"
    )
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info("Calculation of genome coverages started.")
    try:
        calculate_coverages(input_dir, output_dir, genome_lengths, log_transform)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
    else:
        logger.info("Calculation of genome coverages finished.")


@mopp.command()
@click.option("-i", "--input-cov", required=True, help=DESC_INPUT_COV)
@click.option("-c", "--cutoff", type=float, required=True, help=DESC_CUTOFF)
@click.option("-ref", "--refdb", required=True, help=DESC_REFDB)
@click.option("-o", "--output-dir", required=True, help=DESC_OUTPUT)
@click.option("-p", "--prefix", required=True, help=DESC_PREFIX)
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
def index(input_cov, cutoff, refdb, output_dir, prefix, threads):
    create_folder_without_clear(Path(output_dir))

    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(
        f"{output_dir}/mopp_index_{timestamp}.log"
    )
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        genome_extraction(
            input_cov, cutoff, refdb, output_dir, prefix, threads
        )

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
def features(
    rank, input_dir, output_dir, woltka_database, stratification
):
    create_folder_without_clear(Path(output_dir))

    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(
        f"{output_dir}/mopp_features_{timestamp}.log"
    )
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    rank_list = [s.strip() for s in rank.split(",")]

    try:
        ft_generation(
            input_dir, output_dir, woltka_database, rank_list, stratification
        )
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


# fmt: off
@mopp.command()
@click.option("-i", "--input-dir", required=True, help=DESC_INPUT_SAM)
@click.option("-o", "--output-dir", required=True, help=DESC_OUTPUT)
@click.option("-s", "--suffix", default="tsv", help=DESC_SUFFIX)
@click.option("-strat", "--stratification", is_flag=True, default=False, help=DESC_STRAT)
@click.option("-c", "--coords-map", help=DESC_COORDS_MAP)
@click.option("-tax", "--tax-map", help=DESC_TAX_MAP)
@click.option("-func", "--func-map", help=DESC_FUNC_MAP)
@click.option("-d", "--divide", is_flag=True, default=False, help=DESC_DIVIDE)
# fmt: on
def features_custom(
    input_dir,
    output_dir,
    suffix,
    stratification,
    coords_map,
    tax_map,
    func_map,
    divide,
):
    create_folder_without_clear(Path(output_dir))

    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(
        f"{output_dir}/mopp_features_{timestamp}.log"
    )
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    gen_feature_table(
        input_dir,
        output_dir,
        suffix,
        stratification,
        coords_map,
        tax_map,
        func_map,
        divide,
    )


if __name__ == "__main__":
    mopp()
