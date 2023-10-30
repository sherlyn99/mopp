import click
from glob import glob
import time
import logging
from os import path

from mopp._defaults import (DESC_MD, DESC_INPUT)
from mopp.modules import (load_metadata, md_to_dict, trim, align)

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=f'md_main_{timestamp}.log',
    level=logging.DEBUG, 
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

@click.group
def mopp():
    pass

@mopp.command()
@click.option('-p', '--project_dir', required=True, help=DESC_MD)
@click.option('-i', '--input_dir', required=True, help=DESC_INPUT)
@click.option('-m', '--metadata', required=True, help=DESC_MD)
def workflow(project_dir, input_dir, metadata):
    # load metadata
    md = load_metadata(metadata)
    logging.info('Metadata loaded')
    # parse input files
    if path.isdir(input):
        file_list = glob(input + '/*.fastq.gz')
    else: raise FileNotFoundError(input)


    #my_func2()
    #click.echo("This is the metag command")

@mopp.command()
@click.option('-p', '--project_dir', required=True, help=DESC_MD)
@click.option('-i', '--input_dir', required=True, help=DESC_INPUT)
@click.option('-m', '--metadata', required=True, help=DESC_MD)
def trim_stuff(project_dir, input_dir, metadata):
    md = md_to_dict(load_metadata(metadata))
    trim.trim_files(input_dir, project_dir, md)

#@mopp.command()
#@click.option('-p', '--project_dir', required=True, help=DESC_MD)
#@click.option('-i', '--input_dir', required=True, help=DESC_INPUT)
#@click.option('-m', '--metadata', required=True, help=DESC_MD)
#@click.option('-x', '--index', required=True, help=DESC_MD)
#def align(project_dir, input_dir, metadata, index):
#    md = load_metadata(metadata)
#    align.align_files(input_dir, project_dir, md, index)


    


if __name__ == '__main__':
    mopp()
