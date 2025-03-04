<h1> <p align ="center"> Welcome to MOPP - Multiomics Processing Pipeline! </p> </h1>

<h3> <p align = "center"> How can MOPP help me? </p> </h3>

This tool helps with processing multiomics sequencing data including metagenomics, metatranscriptomics, and metatranslatomics data. There are two typical use 
cases of this pipeline:

(1) To analyze all omics at the same time, run `mopp workflow --help`

(2) To run a single analysis step, run `mopp trim --help`.etc

The culmination of the pipelines is the creation of a feature count table which enumerates the taxon and function of the samples examined. 

<h3> <p align = "center"> What do I need to run MOPP? </p> </h3>

Different use cases may have more requirements, but for every use case, the following are necessary:
1. An input folder with your sequencing data
2. A tab-delimited metadata file describing the sequencing data you would like processed and follows this [template](https://github.com/sherlyn99/mopp/blob/main/test/data/metadata.tsv). Please avoid '.' in naming files unless . is used before suffix. Please avoid '_Rxx' in naming files unless it is for indicating strand (e.g. _R1, _R2). If any data is not meant to be paired, just put 'r1' in the strand column.
3. A microbial genome database. We recommend [Web of Life 2 (WoLr2)](http://ftp.microbio.me/pub/wol2/).


***
<h2> <p align ="center"> Installation </p> </h2>

To install the most up-to-date version of mopp, run the following command. Depending on which system you are on, you can use either `mopp_mac.yml` or `mopp_linux.yml`. 
```
git clone https://github.com/sherlyn99/mopp.git
cd mopp
conda env create -f mopp_<os>.yml -n mopp
conda activate mopp
pip install -e .
```
MOPP uses `micov` for calculating genome coverages and filtering genomes based on coverage thresholds. Micov runs on matplotlib >= 3.9 and polars-u64-idx >= 1.21. Learn more about it [here](https://github.com/biocore/micov).
```
# do not deactivate the conda environment
# install the coverage-calculation tool, micov, separately
cd ..
git clone https://github.com/biocore/micov.git
cd micov
pip install -e .
```


Run the following command to make sure the installation is complete.
```
micov --help

mopp --help
```

Note that if the creation of conda environment using yml files fails, an alternative is try the following
```
conda create -n mopp_dev_sherlyn python=3.12 -c conda-forge -c bioconda matplotlib scipy polars click tqdm numba duckdb pyarrow bowtie2 trim-galore woltka
```

If you did `pip install -e .`, which is a local installation, you need to keep the source code for the package to run.

***
<h2> <p align ="center"> Dependencies </p> </h2>

The Web of Life (WoL) Database is used by MOPP as a reference for microbe phylogenies. This database is not included in the distribution and must be downloaded independently [here](http://ftp.microbio.me/pub/wol2/). You can use the following command to download the required database files. 
```
# make sure you are in mopp directory
mkdir wol2
cd wol2
wget --no-check-certificate -nH -np -r --cut-dirs=1  http://ftp.microbio.me/pub/wol2/ --reject="index.html*"
```
***

<h2> <p align ="center"> Documentation </p> </h2>

<h4> <p align ="center"> test runs </p> </h4>

Use case 1: `mopp workflow`

If you want to use one command for all processing steps, run the following test command. See 'mopp workflow' section for more information.
```bash
mopp workflow -i ./tests/test_data \                                          # input directory containing fastq.gz
              -m ./tests/test_data/metadata_template.tsv \                    # metadata
              -o ./tests/test_out_wf \                                        # set output folder
              -x ./tests/test_database/wol2_test/databases/bowtie2/WoLr2 \    # bowtie2 index of microbial genome database
              -l ./tests/test_database/wol2_test/genomes/length.map \         # genome length
              -c 20 \                                                         # coverage threshold (min: 0.0, max: 100.0)
              -ref ./tests/test_database/wol2_test/genomes/all.fna \          # reference genomes
              -p wol2_subset \                                                # prefix of subset index
              -db ./tests/test_database/wol2_test \                           # microbial genome database with functional annotations
              -r genus,species \                                              # set rank for feature tables
              -strat \                                                        # generate stratified tables
              -t 4                                                            # number of threads
```

Use case 2: `mopp <module>`

If you prefer to run each step separately, run the following test command.
```bash
# step 1a: auto-generate metadata
mopp metadata \
   -i ./tests/test_data \
   -o ./tests/test_out/metadata/metadata.tsv \
   -p \
   -m

# step 1b: validate metadata
mopp metadata \
   -i ./tests/test_out/metadata/metadata.tsv \
   -p \
   -m

# step 2: trim data
mopp trim \
   -i ./tests/test_data \
   -o ./tests/test_out/trimmed \
   -m ./tests/test_out/metadata/metadata.tsv \
   -t 4

# step 3: align metagenomics data to the reference database for coverage calculation
mopp align \
   -i ./tests/test_out/trimmed \
   -p '*metaG*.fq.gz' \
   -x ./tests/test_database/wol2_test/databases/bowtie2/WoLr2 \
   -o ./tests/test_out/aligned_metaG \
   -t 4 \
   --compress-samfiles

# step 4: calculate coverages
mopp cov \
   -i ./tests/test_out/aligned_metaG/samfiles \
   -o ./tests/test_out/cov \
   -l ./tests/test_database/wol2_test/genomes/length.map

# step 5: generate subset reference database which contains only genomes above a certain coverage cutoff (20 here).
mopp index \
   -i ./tests/test_out/cov/coverage_calculation.tsv \
   -c 20 \
   -ref ./tests/test_database/wol2_test/genomes/all.fna \
   -o  ./tests/test_out/index \
   -p wol2_subset

# step 6: align all trimmed data to the subset reference database index
mopp align \
   -i ./tests/test_out/trimmed \
   -p '*.fq.gz' \
   -x ./tests/test_out/index/wol2_subset_bt2index/wol2_subset \
   -o ./tests/test_out/aligned \
   -t 4 \
   --compress-samfiles

# step 7: generate feature tables
mopp features \
   -i ./tests/test_out/aligned/samfiles \
   -o ./tests/test_out/features \
   -db ./tests/test_database/wol2_test \
   -r genus,species \
   -strat
```

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp workflow </p> </h4>

usage: `mopp workflow -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)> -x <Index> -t <Num Threads> -l <Genome Lengths Path> -c <Cutoff> -ref <Reference Database> -p <Subset Index Prefix>`

example: 
```
mopp workflow -i ./tests/test_data \                                          
              -m ./tests/test_data/metadata_template.tsv \                   
              -o ./tests/test_out_wf \                                        
              -x ./tests/test_database/wol2_test/databases/bowtie2/WoLr2 \    
              -l ./tests/test_database/wol2_test/genomes/length.map \        
              -c 20 \                                                         
              -ref ./tests/test_database/wol2_test/genomes/all.fna \          
              -p wol2_subset \                                                
              -db ./tests/test_database/wol2_test \                           
              -r genus,species \                                              
              -strat \                                                        
              -t 4                                                            
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

<h4> <p align ="center"> mopp metadata </p> </h4>

usage: `mopp metadata -i <Input Directory/Input Path> -o <Output Path>`

This module is for creating and/or validating metadata. An accurate and 
correctly formatted metadata is essential for downstream processing and 
analysis. Here is a template of metadata used by MOPP. Note that values like 
'r1' and 'r2' under the column `strand` should be in small caps. 

If the input is a directory,  MOPP is going to search for all files end 
in '.fastq.gz' or 'fq.gz' and then auto-generate a  metadata based on the 
results of the search and the auto-generated metadata will be  validated. 

If you already have a manually created metadata, MOPP will validate it when 
the input is a path to the metadata file. By default, MOPP checks if the 
metadata is in the correct format.

If `--paired` is specified,  MOPP will check if all metaG/metaT data has both 
R1 and R2. If `--multiomics` is specified,  MOPP will check if all samples have 
metaG, metaT, and metaRS.

A log file will be created in the output directory, which can be used for 
troubleshooting. 

example 1 (Auto-generate & validat a metadata file): 
```
mopp metadata \
   -i ./tests/test_data \
   -o ./tests/test_out/metadata/metadata.tsv \
   -p \
   -m
```

example 2 (Validate a metadata file)

In this case, you do not need to specify an output directory. The log file 
will be generated in the directory containing the `metadata.tsv`. `-o` argument,
if supplied, will be ignored. 
```
mopp metadata \
   -i ./tests/test_out/metadata/metadata.tsv \
   -p \
   -m
```

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp trim </p> </h4>

`mopp trim` trims sequencing data provided in the input directory. The metadata
 indicates which type of data it is (metaG, metaT, or metaRS) so that optimal 
 trimming parameters can be selected case-by-case.

usage: `mopp trim -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)>`

example: 
```
mopp trim \
   -i ./tests/test_data \
   -o ./tests/test_out/trimmed \
   -m ./tests/test_out/metadata/metadata.tsv \
   -t 4
```

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp align </p> </h4>

usage: `mopp align -i <Input Directory> -o <Output Directory> -p <Pattern> -x <Index> -t <Num Threads>`

example:
```
mopp align \
   -i ./tests/test_out/trimmed \
   -p '*metaG*.fq.gz' \
   -x ./tests/test_database/wol2_test/databases/bowtie2/WoLr2 \
   -o ./tests/test_out/aligned_metaG \
   -t 4 \
   --compress-samfiles
```

`mopp align` aligns the sequencing data provided in the input directory to the reference index. Providing a file pattern `-p` allows for specification of files with certain name patterns (e.g. '*.fq.gz' aligns all files with filenames ending with `.fq.gz`). Allocating more threads to this command `-t` can reduce processing time.

The `-x` argument accepts the path and prefix of the index files created by the bowtie2-build command. bowtie2-build outputs the forward (.bt2) and reverse (rev.bt2) index files. Our parameter requests the common prefix that is shared by all these files, before the forward/reverse designation.



<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp cov </p> </h4>

usage: `mopp cov -i <Input Directory> -o <Output Directory> -m <Metadata (tsv)> -l <Genome Lengths Path>`

`mopp cov` uses micov's `compress` to produce a spreadsheet with calculated genome coverages. This is essential for selecting an optimal coverage threshold when generating a subset index.

example: 
```
mopp cov \
   -i ./tests/test_out/aligned_metaG/samfiles \
   -o ./tests/test_out/cov \
   -l ./tests/test_database/wol2_test/genomes/length.map
```

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp generate_index </p> </h4>

usage: `mopp index -i <Input Coverage> -o <Output Directory> -c <Cutoff> -ref <Reference Database> -p <Prefix>`

`-c` is the coverage cutoff used for creating a subset index containing all 
genomes that have a coverage equal to or greater than the cutoff. Cutoff ranges
from 0 to 100. 

example: 
```
mopp index \
   -i ./tests/test_out/cov/coverage_calculation.tsv \
   -c 20 \
   -ref ./tests/test_database/wol2_test/genomes/all.fna \
   -o  ./tests/test_out/index \
   -p wol2_subset
```

align to the new index:
```
mopp align \
   -i ./tests/test_out/trimmed \
   -p '*.fq.gz' \
   -x ./tests/test_out/index/db_subset_bt2index/db_subset \
   -o ./tests/test_out/aligned \
   -t 4 \
   --compress-samfiles
```

`mopp index` creates a subset index from a larger database, given a cutoff threshold. For example, `-c 0.2` would generate a subset that only contains genomes with 20% or greater coverage.

<h2> <p align ="center"> </p> </h2>

<h4> <p align ="center"> mopp feature_table </p> </h4>

usage: `mopp features-i <Input Directory> -o <Output Directory> -db <Woltka Database> -r <rank> -strat <Stratification> `

`mopp features` is the culmination of the processing pipeline. Given the processed sequencing files, the command produces a feature count table using the Woltka database. Stratification options include `species`, `genus`, and `genus,species`

example: 
```
mopp features \
   -i ./tests/test_out/aligned/samfiles \
   -o ./tests/test_out/features \
   -db ./tests/test_database/wol2_test \
   -r genus,species \
   -strat
```

***
<h2> <p align ="center"> FAQs </p> </h2>
See 'issues' for common errors encountered when running MOPP. 
