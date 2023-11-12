import pandas as pd
import logging
import time

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
logging.basicConfig(
    filename=f'metadata_{timestamp}.log',
    level=logging.DEBUG, 
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

# check each identifier has 5 files, with 2 metaG, 2 metaT, and 1 metaRS
# check each concat(identifier_omic_strand) is unique. If not report which one might be duplicated

def load_metadata(md_path):
    """Load metadata."""
    md = pd.read_csv(md_path, sep='\t', index_col=0, low_memory=False)
    print(md)
    return md

def validate_metadata(md):
    """
    Validate metadata in three ways. 
    1) each identifier has 5 files, with 2 metaG, 2 metaT, and 1 metaRS
    2) concat(identifier_omic_strand) is unique. If not report which one might be duplicated.
    """

    ## Check if metaG and metaT files are provided adequately

    for identifier in md:
         print(md[identifier])
         if (-1 in md[identifier]["metaG"]):
              #Log error that incomplete amount of files provided for metaG

              return False
         elif (-1 in md[identifier]["metaT"]):
              #Log error that incomplete amount of files provided for metaT

              return False
         elif (-1 in md[identifier]["metaRS"]):
              #Log error that incomplete amount of files provided for metaRS
              
              return False
    
    ## Check if files are unique. Identifers must inherently be unique or else the dictionary creation would fail
    ## Is this necessary?????? The above check will catch lack of uniqueness.

    return True

def md_to_dict(md):

    md_dict = {}
    md['omic'] = md['omic']
    md['strand'] = md['strand'].str.lower()

    check_fordupes = []
    for index, row in md.iterrows():
        sample_name = index.strip()
        identifier = row['identifier'].strip()
        omic = row['omic'].strip()
        strand = row['strand'].strip()

        check_fordupes.append(identifier+omic+strand)

        if identifier not in md_dict:
            md_dict[identifier] = {
                'metaG': [-1, -1],
                'metaT': [-1, -1],
                'metaRS': [-1]}

        if strand == 'r1':
                md_dict[identifier][omic][0] = sample_name
        elif strand == 'r2':
                md_dict[identifier][omic][1] = sample_name

    duplicates = []
    seen = set()

    for item in check_fordupes:
        if item in seen:
            duplicates.append(str(item))
        else:
            seen.add(item)

    if duplicates:
        logging.error("Duplicates found: %s" % duplicates)
    else:
        logging.info("No duplicates found.")

    return md_dict


if __name__ == '__main__':
    res = validate_metadata(md_to_dict(load_metadata("./test/data/metadata.tsv")))
    print(res)





