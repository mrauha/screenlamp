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


import os
import argparse
import sys
import pandas as pd
import time
from mputil import lazy_imap
from biopandas.mol2 import split_multimol2
from biopandas.mol2 import PandasMol2


def parse_distance_string(s):
    dist = [int(p.strip()) for p in s.split('-')]
    return dist


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


def parse_selection_string(s, df_name='pdmol.df'):

    columns = ['(atom_id', '(atom_name', '(atom_type',
               '(subst_id', '(subst_name', '(charge']
    lst = [subs.strip() for subs in s.split('-->')]
    parsed = []

    for subs in lst:
        for c in columns:
            subs = subs.replace(c, '(%s.%s' % (df_name, c[1:]))
        parsed.append(subs)
    return parsed


def data_processor(mol2):

    pdmol = PandasMol2().read_mol2_from_list(mol2_lines=mol2[1],
                                             mol2_code=mol2[0])

    coordinates = pdmol.df.loc[pd.eval(SELECTION[0]), ['x', 'y', 'z']].values

    pdmol._df = pdmol._df[pd.eval(SELECTION[1])]

    for xyz in coordinates:

        distances = pdmol.distance(xyz)

        match = ((distances.values >= DISTANCE[0]).any() and
                 (distances.values <= DISTANCE[1]).any())

        if match:
            return mol2[0]

    return ''


def read_and_write(mol2_files, id_file_path, verbose):

    with open(id_file_path, 'w') as f:

        for mol2_file in mol2_files:
            if verbose:
                start = time.time()
                sys.stdout.write('Processing %s' % os.path.basename(mol2_file))
                sys.stdout.flush()

            cnt = 0
            for chunk in lazy_imap(data_processor=data_processor,
                                   data_generator=split_multimol2(mol2_file),
                                   n_cpus=0):
                _ = [f.write('%s\n' % mol2_id)for mol2_id in chunk if mol2_id]
                cnt += len(chunk)

            if verbose:
                elapsed = time.time() - start
                sys.stdout.write(' | %d mol/sec\n' % (cnt / elapsed))
                sys.stdout.flush()


def main(input_dir, output_file, verbose):
    dirpath = os.path.dirname(output_file)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    mol2_files = get_mol2_files(dir_path=input_dir)
    read_and_write(mol2_files=mol2_files,
                   id_file_path=output_file,
                   verbose=verbose)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description='A command line tool for filtering mol2 files.',
            formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--input',
                        type=str,
                        help='Input directory with .mol2 and .mol2.gz files')
    parser.add_argument('-o', '--output',
                        type=str,
                        help='Directory for writing the output files')
    parser.add_argument('-s', '--selection',
                        type=str,
                        required=True,
                        help='Selection string For example, ...')
    parser.add_argument('-v', '--verbose',
                        type=int,
                        default=1,
                        help='Verbosity level. If 0, does not print any'
                             ' output.'
                             ' If 1 (default), prints the file currently'
                             ' processing.')
    parser.add_argument('-d', '--distance',
                        type=str,
                        help='Distance as "lowerbound-upperbound"')
    parser.add_argument('--processes',
                        type=int,
                        default=1,
                        help='Number of processes to run in parallel.'
                             ' If processes>0, the specified number of CPUs'
                             ' will be used.'
                             ' If processes=0, all available CPUs will'
                             ' be used.'
                             ' If processes=-1, all available CPUs'
                             ' minus `processes` will be used.')

    parser.add_argument('--version', action='version', version='v. 1.0')

    args = parser.parse_args()
    DISTANCE = parse_distance_string(args.distance)
    if len(DISTANCE) != 2:
        raise ValueError("Make sure you only have an lower and upper bound"
                         " for --distance"
                         "\nFor example '13-20'")

    SELECTION = parse_selection_string(args.selection)
    if len(SELECTION) != 2:
        raise ValueError("Make sure you only have 2 --selection criteria"
                         " separated via '-->', for example,"
                         "\n\"((atom_type == 'S.3') |"
                         " (atom_type == 'S.o2'))\"")

    main(args.input, args.output, args.verbose)
