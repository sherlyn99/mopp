import time
import logging
import pandas as pd
from collections import defaultdict
import glob
from pathlib import Path
import re

logger = logging.getLogger("mopp")



def gen_metadata(input_directory, output_directory):
    file_paths = glob.glob(input_directory + '/*.fq.gz') + glob.glob(input_directory + '/*.fastq.gz')

    # Define a function to guess identifier and omic
    def guess_identifier_omic(filename):
        if 'metars' in filename.lower():
            omic = 'metaRS'
        elif 'metat' in filename.lower():
            omic = 'metaT'
        elif 'metag' in filename.lower():
            omic = 'metaG'
        else:
            omic = None
            identifier = None
            logger.error(f"Unable to determine omic and identifier of {filename}")
        
        if omic:
            identifier = filename.split(omic)[0]
        
        
        return identifier, omic

    sample_name = []
    identifiers = []
    omics = []
    strands = []
    for file_path in file_paths:
        
        file_name = file_path.split('/')[-1]
        identifier, omic = guess_identifier_omic(file_name)
        strand = 'R1' if 'R1' in file_name.upper() else 'R2' if 'R2' in file_name.upper() else None
        sample_name.append(file_name)
        #Remove overhang underscores
        identifiers.append(re.sub(r'^_+|_+$', '', identifier))
        omics.append(omic)
        strands.append(strand)

    df = pd.DataFrame({
    'sample_name': sample_name,
    'identifier': identifiers,
    'omic': omics,
    'strand': strands
    })

    df.to_csv(Path(output_directory) / 'metadata.tsv', sep='\t', index=False)
    return Path(output_directory) / 'metadata.tsv'


def load_metadata(md_path):
    md_df = _md_to_df(md_path)
    md_df = _validate_metadata(md_df)
    md_dict = _md_to_dict(md_df)
    return md_dict


def _md_to_df(md_path):
    """Load metadata."""
    md_df = pd.read_csv(md_path, sep="\t", low_memory=False)
    md_df["sample_name"] = md_df["sample_name"].str.strip()
    md_df["identifier"] = md_df["identifier"].str.strip()
    md_df["strand"] = md_df["strand"].str.strip().str.lower()
    return md_df


def _validate_metadata(md_df):
    """
    Validate metadata:
    (1) ncols = 4
    (2) identifier+omic+strand is unique
    """
    # check number of columns
    if md_df.shape[1] != 4:
        err = "Check metadata and make sure it has 4 columns like the template."
        logger.error(err)
        raise ValueError(err)

    # check uniqueness of identifier+omic+strand
    md_df["label"] = md_df["identifier"] + "|" + md_df["omic"] + "|" + md_df["strand"]
    duplicates = md_df["label"].duplicated()
    if duplicates.any():
        err = f'Duplicate entries of identifier+omic+strand found: {md_df[duplicates]["label"].tolist()}'
        logger.error(err)
        raise ValueError(err)
    return md_df


def _md_to_dict(md_df):
    """Stores metadata in a dictionary."""
    md_dict = {}
    for _, row in md_df.iterrows():
        sample_name, identifier, omic, strand = (
            row["sample_name"],
            row["identifier"],
            row["omic"],
            row["strand"],
        )
        if identifier not in md_dict:
            md_dict[identifier] = {"metaG": [-1, -1], "metaT": [-1, -1], "metaRS": [-1]}
            # md_dict[identifier] = {"metaRS": [-1]}
        if strand == "r1":
            md_dict[identifier][omic][0] = sample_name
        elif strand == "r2":
            md_dict[identifier][omic][1] = sample_name
    logger.info("Metadata loaded")
    return md_dict


if __name__ == "__main__":
    load_metadata()
