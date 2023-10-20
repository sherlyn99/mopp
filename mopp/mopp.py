import click
from glob import glob
import time
import logging
import pandas as pd
import os
from os import path
import _env
from shutil import rmtree
import json

from mopp._defaults import (DESC_MD, DESC_INPUT)
from mopp.modules import load_metadata, my_func2, workflow_organization


timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=f'md_main_{timestamp}.log',
    level=logging.DEBUG, 
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')


@click.group
def mopp():
    pass


@mopp.command()
@click.argument("name")
@click.option('-m', '--metadata', required=True, help=DESC_MD)
@click.option('-i', '--input', required=True, help=DESC_INPUT)
def create_workflow(name, metadata, input):
    # load metadata
    _env.workflow_metadata = load_metadata(metadata)
    logging.info('Metadata loaded')
    # parse input files
    if path.isdir(input):
        file_list = glob(input + '/*.fastq.gz')
    else: raise FileNotFoundError(input)

    workflow_organization.initialize_workflow(name, input)
    

@mopp.command()
@mopp.argument("name")
def activate(name):
    workflow_list = os.listdir("./workflows")
    if (input in workflow_list):
        _env.workflow_env = name
        with open(f"./workflows/{name}/{name}_metadata.txt", "r") as read_file:
            _env.workflow_metadata = json.load(read_file)
    else:
        logging.error("trying to activate a workflow that doesn't exist")

@mopp.command()
@mopp.argument("name")
def delete(name):
    workflow_list = os.listdir("./workflows")
    if (name in workflow_list):
        _env.workflow_env = ""
        rmtree(f"./workflows/{name}")
    else:
        logging.error("trying to delete a workflow that doesn't exist")



#my_func2()
    #click.echo("This is the metag command")

if __name__ == '__main__':
    _env.workflow_env = ""
    mopp()
