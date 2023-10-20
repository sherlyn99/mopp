import click
from glob import glob
import time
import logging
import pandas as pd
from os import path

from mopp._defaults import (DESC_MD, DESC_INPUT)
from mopp.modules import load_metadata, my_func2

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=f'md_main_{timestamp}.log',
    level=logging.DEBUG, 
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

@click.group
def mopp():
    pass

@mopp.command()
@click.option('-m', '--metadata', required=True, help=DESC_MD)
@click.option('-i', '--input', required=True, help=DESC_INPUT)
def workflow(metadata):
    # load metadata
    md = load_metadata(metadata)
    logging.info('Metadata loaded')
    # parse input files
    if path.isdir(input):
        file_list = glob(input + '/*.fastq.gz')
    else: raise FileNotFoundError(input)


    #my_func2()
    #click.echo("This is the metag command")

if __name__ == '__main__':
    mopp()
