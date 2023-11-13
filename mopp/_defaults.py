# welcome messages
MSG_WELCOME = """
Welcome to MOPP - Multiomics Processing Pipeline!

This tool helps with processing multiomics sequencing data including metagenomics, 
metatranscriptomics, and metatranslatomics data. There are three typical use 
cases of this pipeline:

(1) To analyze all omics at the same time, run `mopp workflow --help`

(2) To analyze each omic, run `mopp metag --help` .etc

(3) To run a single analysis step, run `mopp trim --help`.etc
"""
MSG_WELCOME_WORKFLOW = """
Insert introduction to complete workflow & paper citation
"""

# descriptions
DESC_MD = "Sample metadata file in tsv format. See README for a template."
DESC_INPUT = "Directory of metaG/metaT/metaRS files."
DESC_INPUT_SAM = "Directory of metaG/metaT/metaRS trimmed files."
DESC_OUTPUT = "Output directory. Will create if does not exist. Will erase if exists."
DESC_INDEX = "Genome index."
DESC_NTHREADS = "Number of threads. Default: 4."


# try:
#     subprocess.check_output(commands)
#     logging.info('Trimming finsihed')
# except subprocess.CalledProcessError as e:
#     #print(e.stderr)
#     #print(e.stdout)
#     logging.error(f'Trimming failed with error {e.output}')
