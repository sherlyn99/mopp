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
This is the central tool to MOPP, where you can analyze all omics at the same time.
With your provided metadata, the tool is able to properly process metagenomic, metatranscriptomic,
and metatranslatomic data to produce count tables that classify by genus and stratify species by
uniref annotation. 

The workflow takes the following steps:

1) Trim adapters off of all sequencing files.

2) Align metagenomic files to the entire Web of Life Database and 
   calculate genome coverages. A subset index of the Web of Life Database
   is created based on a desired genome coverage threshold.

3) Align metagenomic, metatranscriptomic, and metatranslatomic data to the subset index.

4) Generate genus classification and Species|Uniref stratification count tables using Woltka.

[Insert paper citation here]

"""
MSG_WELCOME_METADATA = """
This module is for creating and/or validating metadata. If the input is a directory, 
MOPP is going to search for all files end in '.fastq.gz' or 'fq.gz' and then auto-generate a 
metadata based on the results of the search and the auto-generated metadata will be 
validated. If an output path to a new metadata file is not created, the metadata 
and log will be created in the input directory. 

If the input is a path to the metadata file, MOPP will validate it. 
By default, MOPP checks if the metadata is in the correct format. If '-paired' is specified, 
MOPP will check if all metaG/metaT data has both R1 and R2. If '-multiomics' is specified, 
MOPP will check if all samples have metaG, metaT, and metaRS.
"""

# descriptions
DESC_MD = "Sample metadata file in tsv format. See README for a template."
DESC_MD_OR_DIR = "Sample metadata file in tsv format (See README for a template) or a directory containing rawdata end in '.fastq.gz' or 'fq.gz'."
DESC_MD_OUTPUT = "Output path to a new metadata file."
DESC_INPUT = "Input: Directory of metaG/metaT/metaRS files."
DESC_INPUT_SAM = "Input: Directory of metaG/metaT/metaRS samfiles."
DESC_INPUT_TRIMMED = "Input: Directory of metaG/metaT/metaRS trimmed files."
DESC_OUTPUT = "Output: Output directory. Must be a new directory that currently does not exist."
DESC_VALIDATE_PAIRED_END = "Enable metadata validation for paired-end data."
DESC_VALIDATE_MULTIOMICS = "Enable metadata validation for multiomics data"
DESC_INDEX = "Genome index."
DESC_NTHREADS = "Number of threads. [default: 4]."
DESC_LOG_TRANSFORM = "Provides density plot with log transformed x-axis."
# module: align
DESC_PATTERN = "File patterns to include for alignment."
DESC_COMPRESS_SAM = "If yes, samfiles generated will be compressed."
# module: features
DESC_RANK = "Taxonomic rank."
DESC_STRAT = (
    "Enables uniref stratification. Applies to all ranks. Default: off"
)
DESC_WOLTKA_DB = "Path to woltka database."

# module: index
DESC_GENOME_LENGTHS = "Path to a file with genome lengths, a tsv with the first column as genome id and the second column as genome length (bp)."
DESC_CUTOFF = (
    "The genome coverage cutoff threshold for generating the subset index. Ranges from 0 to 100."
)
DESC_REFDB = "Path to the reference database file (.fna, .fna.gz, .fna.xz)."
DESC_PREFIX = "Prefix for generated files."
DESC_INPUT_COV = "Path to the coverage file in tab-separated format."

# module: features
DESC_SUFFIX = "Suffix of output files. e.g. 'biom' or 'tsv'. Default: tsv"
DESC_COORDS_MAP = "Path to the coords.txt.xz file."
DESC_TAX_MAP = "Path to the mapping file from genome id to taxa name."
DESC_FUNC_MAP = "Path to the mapping file from gene coords to others (e.g. uniref, ko .etc)."
DESC_DIVIDE = "If true, count each target feature as 1/k (k is the number of targets mapped to a source). Otherwise, count as one."



# try:
#     subprocess.check_output(commands)
#     logging.info('Trimming finsihed')
# except subprocess.CalledProcessError as e:
#     #print(e.stderr)
#     #print(e.stdout)
#     logging.error(f'Trimming failed with error {e.output}')
