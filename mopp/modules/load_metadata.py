import pandas as pd

# check each identifier has 5 files, with 2 metaG, 2 metaT, and 1 metaRS
# check each concat(identifier_omic_strand) is unique. If not report which one might be duplicated

def load_metadata(md_path):
    """Load metadata."""
    md = pd.read_csv(md_path, sep='\t', index_col=0, low_memory=False)
    return md

def validate_metadata(md):
    """
    Validate metadata in three ways. 

    1) each identifier has 5 files, with 2 metaG, 2 metaT, and 1 metaRS
    2) concat(identifier_omic_strand) is unique. If not report which one might be duplicated.
    """
    return

def md_to_dict(md):
    md_dict = {}
    md['omic'] = md['omic'].str.lower()
    md['strand'] = md['strand'].str.lower()
    for index, row in md.iterrows():
        sample_name = index.strip()
        identifier = row['identifier'].strip()
        omic = row['omic'].strip()
        strand = row['strand'].strip()

        if identifier not in md_dict:
            md_dict[identifier] = {
                'metag': [-1, -1],
                'metat': [-1, -1],
                'metars': [-1]}

        if strand == 'r1':
                md_dict[identifier][omic][0] = sample_name
        elif strand == 'r2':
                md_dict[identifier][omic][1] = sample_name
    return md_dict


if __name__ == '__main__':
    res = md_to_dict()
    print(res)


