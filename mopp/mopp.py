import time
import click
import logging
from glob import glob
from mopp._defaults import (
    MSG_WELCOME,
    MSG_WELCOME_WORKFLOW,
    DESC_MD,
    DESC_INPUT,
    DESC_INPUT_SAM,
    DESC_OUTPUT,
    DESC_INDEX,
    DESC_NTHREADS,
)
from mopp.modules.trim import trim_files
from mopp.modules.align import align_files


logger = logging.getLogger("mopp")
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")


@click.group(help=MSG_WELCOME)
def mopp():
    pass


# @mopp.command(help=MSG_WELCOME_WORKFLOW)
# @click.option("-p", "--project_dir", required=True, help=DESC_MD)
# @click.option("-i", "--input_dir", required=True, help=DESC_INPUT)
# @click.option("-m", "--metadata", required=True, help=DESC_MD)
# def workflow(project_dir, input_dir, metadata):
#     # load metadata
#     md = load_metadata(metadata)
#     logger.info("Metadata loaded")
#     # parse input files
#     if path.isdir(input):
#         file_list = glob(input + "/*.fastq.gz")
#     else:
#         raise FileNotFoundError(input)
#     # load md
#     # run trim+cat
#     # update md_dict to be cat
#     # run align

#     # my_func2()
#     # click.echo("This is the metag command")


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
@click.option("-i", "--input_dir", required=True, help=DESC_INPUT_SAM)
@click.option("-o", "--output_dir", required=True, help=DESC_OUTPUT)
@click.option("-x", "--index", required=True, help=DESC_INDEX)
@click.option("-t", "--threads", default=4, help=DESC_NTHREADS)
def align(input_dir, output_dir, index, threads):
    logger.setLevel(logging.INFO)
    filer_handler = logging.FileHandler(f"mopp_{timestamp}.log")
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        align_files(input_dir, output_dir, index, threads)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)


if __name__ == "__main__":
    mopp()
