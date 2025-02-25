<h1> <p align ="center"> Welcome to MOPP - Multiomics Processing Pipeline! </p> </h1>

<h3> <p align = "center"> How can MOPP help me? </p> </h3>

This tool helps with processing multiomics sequencing data including metagenomics, 
metatranscriptomics, and metatranslatomics data. There are three typical use 
cases of this pipeline:

(1) To analyze all omics at the same time, run `mopp workflow --help`

(2) To analyze each omic, run `mopp metag --help` .etc

(3) To run a single analysis step, run `mopp trim --help`.etc

The culmination of the pipelines is the creation of a feature count table using Woltka. 

<h3> <p align = "center"> What do I need to run MOPP? </p> </h3>

Different use cases may have more requirements, but for every use case, the following are necessary:
1. An input folder with your sequencing data
2. A tab-delimited metadata file describing the sequencing data you would like processed and follows this [template](https://github.com/sherlyn99/mopp/blob/main/test/data/metadata.tsv). Please avoid . in naming files unless . is used before suffix. Please avoid _Rxx in namig files unless it is for indicating strand (e.g. _R1, _R2). If any data is not meant to be paired, just put 'R1' in the strand column.


***
<h2> <p align ="center"> Installation </p> </h2>

To install the most up-to-date version of mopp, run the following command
```
git clone https://github.com/sherlyn99/mopp.git
cd mopp
conda env create -f mopp_<os>.yml -n mopp
conda activate mopp
pip install -e .

# do not deactivate the conda environment at this moment
# install the coverage-calculation tool, micov, separately
cd ..
git clone https://github.com/biocore/micov.git
cd micov
pip install -e .
```
or use mamba for faster installation. 

Run the following command to make sure the installation is complete.
```
micov --help

mopp --help
```

Note that if the creation of conda environment using yml files fails, an alternative is to do the following
```
conda create -n mopp_dev_sherlyn python=3.12 -c conda-forge -c bioconda \
  matplotlib scipy polars click tqdm numba duckdb pyarrow bowtie2 trim-galore woltka
```

Micov runs on matplotlib >= 3.9 and polars-u64-idx >= 1.21.

Note that if you did `pip install -e .`, which is a local installation, you need to keep the source code (do not delete it) for the package to run.

***
<h2> <p align ="center"> Dependencies </p> </h2>

The Web of Life (WoL) Database is used by MOPP as a reference for microbe phylogenies. This database is not included in the distribution and must be downloaded independently [here](https://biocore.github.io/wol/download). You can use the following command to download the required database files. 
```
# make sure you are in mopp directory
mkdir mopp_db
cd mopp_db
wget --no-check-certificate -nH -np -r --cut-dirs=1  https://ftp.microbio.me/pub/wol-20April2021/ --reject="index.html*"
```

Create bowtie2 index of the WoL database by running the followig commands.
```
cd wol-20April2021
mkdir -p databases/bowtie2
xzcat genomes/concat.fna.xz > /tmp/input.fna
bowtie2-build --seed 42 /tmp/input.fna databases/bowtie2/WoLr1
rm /tmp/input.fna
```

MOPP uses `micov` for calculating genome coverages and filtering genomes based on coverage thresholds. This library is included in the conda environment. Learn more about it [here](https://github.com/biocore/micov).

***

<h2> <p align ="center"> Documentation </p> </h2>

<h4> <p align ="center"> mopp workflow </p> </h4>

usage: `mopp workflow -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)> -x <Index> -t <Num Threads> -l <Genome Lengths Path> -c <Cutoff> -ref <Reference Database> -p <Index Prefix>`

example: 
```
mopp workflow -i ./test/data \
              -o ./test/data/out3/ \
              -m ./test/data/metadata.tsv \
              -x ./test/data/wol_subset_index/wol_subset0.1_index \
              -t 4 \
              -l /home/y1weng/genome_lengths.tsv \
              -c 0.1 \
              -ref ./test/data/wol_subset_index/wol_above10.concat.fna \
              -p myTest \
              -r genus,species \
              -db /panfs/y1weng/01_woltka_db/wol1/wol-20April2021 \
              -strat \
              -r genus,species
```

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

example: 
```
mopp trim -i ./test/data \
   -o ./test/data/out3/cat \
   -m ./test/data/metadata.tsv
```

`mopp trim` trims sequencing data provided in the input directory. The metadata indicates which type of data it is (metaG, metaT, or metaRS) so that optimal trimming parameters can be selected case-by-case. 


<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp align </p> </h4>

usage: `mopp align -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)> -p <Pattern> -x <Index> -t <Num Threads>`

example:
```
mopp align -i ./test/data/out3/cat \
   -p *.fq.gz \
   -o ./test/data/out3/aligned \
   -x ./test/data/wol_subset_index/wol_subset0.1_index \
   -t 4
```

`mopp align` aligns the sequencing data provided in the input directory to the reference index. Providing a file pattern `-p` allows for specification of files with certain name patterns. Allocating more threads to this command `-t` can reduce processing time.

The `-x` argument accepts the path and prefix of the index files created by the bowtie2-build command. bowtie2-build outputs the forward (.bt2) and reverse (rev.bt2) index files. Our parameter requests the common prefix that is shared by all these files, before the forward/reverse designation.



<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp cov </p> </h4>

usage: `mopp cov -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)> -l <Genome Lengths Path>`

example: 
```
mopp cov -i ./test/data/out3/aligned/samfiles \
   -o ./test/data/out3/cov \
   -l /home/y1weng/genome_lengths.tsv
```

`mopp cov` uses micov's `compress` to produce a spreadsheet with calculated genome coverages. This is essential for selecting an optimal coverage threshold when generating a subset index.

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp generate_index </p> </h4>

usage: `mopp generate-index -i <Input Coverage> -o <Output Directory> -c <Cutoff> -ref <Reference Database> -p <Prefix>`

example: 
```
mopp generate-index -i ./test/data/out2/cov/coverages.tsv \
   -c 0.1 \
   -ref ./test/data/wol_subset_index/wol_above10.concat.fna \
   -o ./test/data/out3/index \
   -p myTest
```

`mopp generate-index` creates a subset index from a larger database, given a cutoff threshold. For example, `-c 0.2` would generate a subset that only contains genomes with 20% or greater coverage.

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp feature_table </p> </h4>

usage: `mopp feature-table -i <Input Directory> -o <Output Directory> -db <Woltka Database> -strat <Stratification>`

example: 
```
mopp feature-table -i ./test/data/out3/aligned/samfiles \
   -o ./test/data/out2/features \
   -db /panfs/y1weng/01_woltka_db/wol1/wol-20April2021 \
   -strat \
   -r genus,species
```

`mopp feature_table` is the culmination of the processing pipeline. Given the processed sequencing files, the command produces a feature count table using the Woltka database. Stratification options include `species`, `genus`, and `genus,species`

***
<h2> <p align ="center"> FAQs </p> </h2>
coming soon
