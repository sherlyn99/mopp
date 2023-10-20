# descriptions
DESC_MD='Sample metadata file in tsv format. See README for a template.'
DESC_INPUT='Directory of metaG/metaT/metaRS files.'
DESC_OUTPUT=('Output directory. Will create if does not exist. ',
            'Will append if exists')


# try:
#     subprocess.check_output(commands)
#     logging.info('Trimming finsihed')
# except subprocess.CalledProcessError as e:
#     #print(e.stderr)
#     #print(e.stdout)
#     logging.error(f'Trimming failed with error {e.output}')