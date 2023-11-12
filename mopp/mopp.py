import click
from glob import glob
import time
import logging
from os import path
from mopp._defaults import MSG_WELCOME, MSG_WELCOME_WORKFLOW, DESC_MD, DESC_INPUT
from mopp.modules.metadata import load_metadata


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

#     # my_func2()
#     # click.echo("This is the metag command")


@mopp.command()
@click.option("-i", "--input_dir", required=True, help=DESC_INPUT)
@click.option("-m", "--metadata", required=True, help=DESC_MD)
@click.option("-o", "--output_dir", required=True, help=DESC_MD)
def trim(input_dir, output_dir, metadata):
    md_dict = load_metadata(metadata)
    trim.trim_files(input_dir, output_dir, md_dict)
    logger.info("Trim finished")


# @mopp.command()
# @click.option('-p', '--project_dir', required=True, help=DESC_MD)
# @click.option('-i', '--input_dir', required=True, help=DESC_INPUT)
# @click.option('-m', '--metadata', required=True, help=DESC_MD)
# @click.option('-x', '--index', required=True, help=DESC_MD)
# def align(project_dir, input_dir, metadata, index):
#    md = load_metadata(metadata)
#    align.align_files(input_dir, project_dir, md, index)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")

    filer_handler = logging.FileHandler(f"main_{timestamp}.log")
    filer_handler.setFormatter(formatter)
    logger.addHandler(filer_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    mopp()
