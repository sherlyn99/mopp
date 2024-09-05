import sys
import logging
import pandas as pd
from collections import defaultdict

logger = logging.getLogger("mopp")


def load_metadata(md_path):
    md_df = _md_to_df(md_path)
    md_dict = _df_to_dict(md_df)
    return md_dict


def _md_to_df(md_path):
    """Load metadata into a pandas dataframe"""
    md_df = pd.read_csv(md_path, sep="\t", low_memory=False)
    _validate_md(md_df)

    md_df["sample_name"] = md_df["sample_name"].str.strip()
    md_df["identifier"] = md_df["identifier"].str.strip()
    md_df["strand"] = md_df["strand"].str.strip().str.lower()
    return md_df


def _validate_md(md_df, paired=False, multiomics=False):
    """
    Validate metadata:
    (1) ncols = 4
    (2) colnames are in ("sample_name", "identifier", "omics", "strand")
    (3) omics are in ("metaG", "metaT", "metaRS")
    (4) identifier+omic+strand is unique
    Does NOT verify if all identifiers have all omics and strands
    """
    # check number of columns
    if md_df.shape[1] != 4:
        err = f"Metadata has {md_df.shape[1]} columns. Please make sure it has 4 columns."
        logger.error(err)
        sys.exit(1)

    # check colnames
    colnames_obs = md_df.columns.tolist()
    colnames_exp = ["sample_name", "identifier", "omic", "strand"]
    for col_o, col_e in zip(colnames_obs, colnames_exp):
        if col_o != col_e:
            err = f"Please change metadata column name '{col_o}' to '{col_e}' and try again."
            logger.error(err)
            sys.exit(1)

    # check omics values
    omics_exp = ["metaG", "metaT", "metaRS"]
    for idx, omic in enumerate(md_df["omic"].tolist()):
        if omic not in omics_exp:
            err = f"Please change the omic value in row {idx+1} (1-indexed) from '{omic}' to one of the following: 'metaG', 'metaT', 'metaRS'."
            logger.error(err)
            sys.exit(1)

    # check uniqueness of identifier+omic+strand
    md_df["label"] = (
        md_df["identifier"] + "|" + md_df["omic"] + "|" + md_df["strand"]
    )
    duplicates = md_df["label"].duplicated()
    if duplicates.any():
        err = f"Duplicate entries of 'identifier|omic|strand' found: {md_df[duplicates]['label'].tolist()}"
        logger.error(err)
        sys.exit(1)

    md_df.drop(columns=["label"], inplace=True)

    # check if all R1's of metaG/metaT data has a corresponding R2
    if paired:
        _valid_paired_end(md_df)

    # check if all identifiers have metaG, metaT, and metaRS
    if multiomics:
        _valid_multiomics(md_df)


def _valid_paired_end(md_df):
    """Need to work on this"""
    paired_dict = {}
    for _, row in md_df.iterrows():
        if row["omic"] != "metaRS":
            curr_key = row["identifier"] + "|" + row["omic"]
            if curr_key not in paired_dict:
                paired_dict[curr_key] = [-1, -1]
    for key, val in paired_dict:
        if -1 in val:
            err = f"{key} is missing a paired-end file."
            sys.exit(1)


def _valid_multiomics(md_df):
    """Need to work on this"""
    multiomics_dict = {}
    for _, row in md_df.iterrows():
        curr_key = row["identifier"]
        if curr_key not in multiomics_dict:
            multiomics_dict[curr_key] = [-1, -1, -1]
    for key, val in multiomics_dict:
        if -1 in val:
            err = f"{key} is missing a paired-end file."
            sys.exit(1)


def _df_to_dict(md_df):
    """Stores metadata in a dictionary"""
    md_dict = {}
    for _, row in md_df.iterrows():
        sample_name, identifier, omic, strand = (
            row["sample_name"],
            row["identifier"],
            row["omic"],
            row["strand"],
        )
        if identifier not in md_dict:
            md_dict[identifier] = {}
        if omic not in md_dict[identifier]:
            if omic == "metaRS":
                md_dict[identifier][omic] = [-1]
            else:
                md_dict[identifier][omic] = [-1, -1]
        if strand == "r1":
            md_dict[identifier][omic][0] = sample_name
        elif strand == "r2" and omic != "metaRS":
            md_dict[identifier][omic][1] = sample_name
    logger.info("Metadata loaded")
    return md_dict


if __name__ == "__main__":
    load_metadata()
