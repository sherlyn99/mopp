from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = ''

setup(
    name='mopp',
    version=VERSION,
    author='Sherlyn Weng (@sherlyn99)',
    author_email='y1weng@ucsd.edu',
    description=DESCRIPTION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Click','pandas'],
    entry_points={
        'console_scripts': [
            'mopp = mopp.mopp:mopp',
        ],
    },
)
