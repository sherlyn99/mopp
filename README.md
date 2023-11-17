<h1> <p align ="center"> Welcome to MOPP - Multiomics Processing Pipeline! </p> </h1>

***

This tool helps with processing multiomics sequencing data including metagenomics, 
metatranscriptomics, and metatranslatomics data. There are three typical use 
cases of this pipeline:

(1) To analyze all omics at the same time, run `mopp workflow --help`

(2) To analyze each omic, run `mopp metag --help` .etc

(3) To run a single analysis step, run `mopp trim --help`.etc

***

<h2> <p align ="center"> Documentation </p> </h2>

<h4> <p align ="center"> mopp workflow </p> </h4>

usage: `mopp workflow -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)> -x <Index> -t <Num Threads> -z <zebra-filter Path> -c <Cutoff> -ref <Reference Database> -p <Index Prefix>`

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

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp trim </p> </h4>

usage: `mopp trim -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)>`

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp align </p> </h4>

usage: `mopp align -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)> -o <Pattern> -x <Index> -t <Num Threads>`

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp cov </p> </h4>

usage: `mopp cov -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)> -z <zebra-filter Path>`

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp generate_index </p> </h4>

usage: `mopp generate_index -i <Input Coverage> -o <Output Directory> -c <Cutoff> -ref <Reference Database> -p <Prefix>`

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp feature_table </p> </h4>

usage: `mopp feature_table -i <Input Coverage> -o <Output Directory> -db <Woltka Database> -strat <Stratification>`
