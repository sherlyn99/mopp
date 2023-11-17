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
   
4) Align metagenomic, metatranscriptomic, and metatranslatomic data to the subset index.
   
5) Generate genus classification and Species|Uniref stratification count tables using Woltka.

[Insert paper citation here]

"""

# descriptions
DESC_MD = "Sample metadata file in tsv format. See README for a template. [required]"
DESC_INPUT = "Input: Directory of metaG/metaT/metaRS files. [required]"
DESC_INPUT_SAM = "Input: Directory of metaG/metaT/metaRS samfiles. [required]"
DESC_INPUT_TRIMMED = "Input: Directory of metaG/metaT/metaRS trimmed files. [required]"
DESC_OUTPUT = "Output: Directory name to generate or overwite. [required]"
DESC_INDEX = "Genome index. [required]"
DESC_NTHREADS = "Number of threads. [default: 4]."
# module: align
DESC_PATTERN = "File patterns to include for alignment"
# module: features
DESC_RANK = "Taxonomic rank."
DESC_STRAT = "Enables uniref stratification. Applies to all ranks. Default: off"
DESC_WOLTKA_DB = "Path to woltka database."

# module: index
DESC_ZEBRA = "Path to zebra-filter directory."
DESC_CUTOFF = "The genome coverage cutoff threshold for generating the subset index."
DESC_REFDB = "Path to the reference database file (.fna, .fna.gz, .fna.xz)."
DESC_PREFIX = "Prefix for generated files."
DESC_INPUT_COV = "Path to the coverage file in tab-separated format."


# try:
#     subprocess.check_output(commands)
#     logging.info('Trimming finsihed')
# except subprocess.CalledProcessError as e:
#     #print(e.stderr)
#     #print(e.stdout)
#     logging.error(f'Trimming failed with error {e.output}')
