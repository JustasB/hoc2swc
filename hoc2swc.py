'''
This file is intended to only be used when Python module of NEURON has not been installed.

Usage should always be in this form: nrniv -python 'path/to/cell.hoc' 'path/to/out.swc'
'''

import os, sys

if len(sys.argv) == 3:
    print("NEURON .HOC -> .SWC converter. Usage: nrniv -python -path/to/cell.hoc -path/to/out.swc")
    quit()

if len(sys.argv) < 5:
    raise Exception("Must specify input HOC and output SWC file paths.")
    quit()

if len(sys.argv) == 5:
    py_file_path = sys.argv[2]
    hoc_path = sys.argv[3]
    swc_path = sys.argv[4]

    # NEURON will load HOC files if they're not escaped
    if hoc_path[0] != "-" or swc_path[0] != "-":
        raise Exception("HOC and SWC paths must be specified with a prescending '-'. E.g. nrniv -python -path/to/cell.hoc -path/to/out.swc")
        quit()

    # Remove the qoutes
    hoc_path = hoc_path[1:]
    swc_path = swc_path[1:]

    # Load the library but retain the working dir
    old_cwd = os.getcwd()
    os.chdir(os.path.abspath(os.path.dirname(py_file_path)))
    from hoc2swc import hoc2swc
    os.chdir(old_cwd)

    hoc2swc(hoc_path, swc_path, separate_process=False)

    quit()

