import sys
import logging
import pandas as pd
from pathlib import Path
from glob import glob


logger = logging.getLogger("mopp")


def autogenerate_metadata(indir):
    """Auto-generate the metadata without valdating it"""
    file_list = list(
        set(glob(indir + "/*.fastq.gz") + glob(indir + "/*.fq.gz"))
    )
    file_list = [str(Path(file).name) for file in file_list]

    md = pd.DataFrame({"sample_name": file_list})
    filenames = md["sample_name"].astype(str).str.split("/").str[-1]
    filenames_nosuffix = filenames.str.split(".fastq.gz|.fq.gz").str[0]
    md["identifier"] = filenames_nosuffix.str.split("_meta|_R").str[0]
    md["omic"] = (
        "meta"
        + filenames_nosuffix.str.split("_meta|_R").str[1].str.split("_").str[0]
    )
    md["strand"] = (
        "r"
        + filenames_nosuffix.str.split("_meta|_R").str[2].str.split("_").str[0]
    )
    return md


def validate_metadata(md_df, paired=False, multiomics=False):
    _validate_md(md_df, paired, multiomics)


def load_metadata_to_df_with_validation(
    md_path, paired=False, multiomics=False
):
    md_df = _md_to_df(md_path, paired, multiomics)
    return md_df


def load_metadata_to_dict_with_validation(
    md_path, paired=False, multiomics=False
):
    md_df = _md_to_df(md_path, paired, multiomics)
    md_dict = _df_to_dict(md_df)
    return md_dict


def _md_to_df(md_path, paired=False, multiomics=False):
    """Load metadata into a pandas dataframe and validate it"""
    md_df = pd.read_csv(md_path, sep="\t", low_memory=False)
    _validate_md(md_df, paired, multiomics)

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
        _validate_paired_end(md_df)

    # check if all identifiers have metaG, metaT, and metaRS
    if multiomics:
        _validate_multiomics(md_df)


def _validate_paired_end(md_df):
    """For any omics other than metaRS, check if the same identifier + omic
    group has both r1 and r2"""
    df = md_df[md_df["omic"] != "metaRS"]
    grouped = df.groupby(["identifier", "omic"])["strand"].apply(
        lambda x: set(x)
    )
    invalid_groups = grouped[grouped.apply(lambda x: x != {"r1", "r2"})]
    if not invalid_groups.empty:
        err = (
            f"Missing a strand for the following identifier + omic groups: "
            + "; ".join(
                [
                    f"{identifier}_{omic}"
                    for (identifier, omic), strands in invalid_groups.items()
                ]
            )
        )
        logger.error(err)
        sys.exit(1)


def _validate_multiomics(md_df):
    """For all identifier, check if it has metaG, metaT, and metaRS"""
    grouped = md_df.groupby(["identifier"])["omic"].apply(lambda x: set(x))
    invalid_groups = grouped[
        grouped.apply(lambda x: x != {"metaG", "metaRS", "metaT"})
    ]
    if not invalid_groups.empty:
        err = (
            f"Missing at least one omic for the following identifiers: "
            + "; ".join(
                [
                    f"{identifier}"
                    for identifier, omics in invalid_groups.items()
                ]
            )
        )
        logger.error(err)
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
            md_dict[identifier][omic] = [-1]
        if strand == "r1":
            md_dict[identifier][omic][0] = sample_name
        elif strand == "r2" and omic != "metaRS":
            md_dict[identifier][omic].append(sample_name)
    logger.info("Metadata loaded into a dictionary")
    return md_dict
