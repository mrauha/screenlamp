# Sebastian Raschka 2017
#
# `screenlamp` is a Python toolkit for using
# filters and pipelines for hypothesis-driven
# virtual screening.
#
# Copyright (C) 2017 Michigan State University
# License: MIT
#
# SiteInterlock was developed in the
# Protein Structural Analysis & Design Laboratory
# (http://www.kuhnlab.bmb.msu.edu)
#
# Author: Sebastian Raschka <http://sebastianraschka.com>
# Author email: mail@sebastianraschka.com


import argparse
import os

from biopandas.mol2.mol2_io import split_multimol2


def get_mol2_files(dir_path):

    files = []

    if os.path.isdir(dir_path):
        for f in os.listdir(dir_path):
            if f.endswith(('.mol2', 'mol2.gz')):
                file_path = os.path.join(dir_path, f)
                files.append(file_path)

    elif (os.path.isfile(dir_path) and
          dir_path.endswith(('.mol2', 'mol2.gz'))):
        files.append(dir_path)

    return files


def mol2_to_idfile(mol2_files, id_file_path, verbose=0):
    with open(id_file_path, 'w') as f:
        for mol2_file in mol2_files:
            if verbose:
                print('Processing %s' % mol2_file)
            for mol2 in split_multimol2(mol2_file):
                f.write(mol2[0] + '\n')
    if verbose:
        print('Finished')


def main(input_dir, output_file, verbose):
    mol2_files = get_mol2_files(dir_path=input_dir)
    mol2_to_idfile(mol2_files=mol2_files,
                   id_file_path=output_file,
                   verbose=verbose)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description='Write a file with molecule IDs from MOL2 files.',
            epilog='Example: python mol2_to_id.py -i mol2_dir -o ids.txt\n',
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--input',
                        type=str,
                        required=True,
                        help='Input .mol2 or .mol2.gz file,'
                             'or a directory of MOL2 files')
    parser.add_argument('-o', '--output',
                        type=str,
                        required=True,
                        help='Output path for the ID file.'
                             ' For example, ids.txt')
    parser.add_argument('-v', '--verbose',
                        type=int,
                        default=1,
                        help='Verbosity level. If 0, does not print any'
                             ' output.'
                             ' If 1 (default), prints the file currently'
                             ' processing.')

    parser.add_argument('--version', action='version', version='v. 1.0')

    args = parser.parse_args()

    main(args.input, args.output, args.verbose)