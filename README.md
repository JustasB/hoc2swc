[![Build Status](https://travis-ci.com/JustasB/hoc2swc.svg?branch=master)](https://travis-ci.com/JustasB/hoc2swc)
[![Coverage Status](https://coveralls.io/repos/github/JustasB/hoc2swc/badge.svg?branch=master)](https://coveralls.io/github/JustasB/hoc2swc?branch=master)
[![PyPI version](https://badge.fury.io/py/hoc2swc.svg)](https://badge.fury.io/py/hoc2swc)

# hoc2swc: A Python package to convert NEURON cell HOC files to SWC morphology files

[hoc2swc](https://pypi.org/project/hoc2swc/) is a Python library that converts the morphology of neuron models defined using [NEURON simulator](https://neuron.yale.edu) [HOC files](https://www.neuron.yale.edu/neuron/static/new_doc/programming/hocsyntax.html) to the popular [SWC morphology format](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html). The library can also be used to convert cell morphologies instantiated in NEURON simulator (e.g. models that were build using NEURON+Python).

Once converted to SWC, tools that can consume SWC files can be used to [compute SWC morphology metrics](https://pypi.org/project/pylmeasure/), create [professional 3D neuron morphology visualizations](https://github.com/MartinPyka/SWC2Blender), etc...

# Requirements

hoc2swc requires a working version of NEURON either installed from a [package/installer](https://www.neuron.yale.edu/neuron/download) (easier) or [compiled](https://neurojustas.com/2018/03/27/tutorial-installing-neuron-simulator-with-python-on-ubuntu-linux/) (more challenging). Linux, Mac, and Windows versions are supported.

You must be able to run at least *one* of these commands in a terminal window without errors:
 - `nrniv -python`
 - Or `python -c 'from neuron import h'`

If you cannot run any of these commands, it indicates that there is something amiss with your NEURON installation. Search the error messages on the [NEURON forum](https://www.neuron.yale.edu/phpBB/) for help.

# Installation and Usage

Installation and usage depends on how you installed NEURON simulator (installed vs. compiled). More customizable functionality is available for those who compiled.

## If you installed a downloaded NEURON package
Download and extract [this hoc2swc ZIP file](https://github.com/JustasB/hoc2swc/archive/master.zip) to a known folder. This folder will have a script named `hoc2swc.py`. Note its location.

Then, to convert a HOC file, run the following command in terminal (note the '-'s before the hoc and swc paths):

`nrniv -python path/to/hoc2swc.py -path/to/cell.hoc -path/to/converted.swc`

## If you compiled NEURON+Python

To install the library, simply type in `pip install hoc2swc` in your terminal.

Then in a Python session, run the following to convert a HOC file to SWC.

```
from hoc2swc import hoc2swc

hoc2swc("path/to/cell.hoc", "out.swc")
```

### Exporting non-HOC cells
If a cell is not defined in a HOC file (e.g. defined using a custom script or using Python), you can instantiate the cell in NEURON and when it is ready for export to SWC, use the following Python script lines:

```
# Load your cell
from neuron import h
run_scripts_build_cell_etc()

# Export loaded cell to SWC
from hoc2swc import neuron2swc
neuron2swc("out.swc")
```

Note to packaged NEURON users, if you start `nrniv -python` from the directory where the hoc2swc.py file is located OR append the location to the PYTHONPATH environment variable, the above lines will work for you as well.

# Issues
If you encounter an issues, first make sure it's not due to NEURON itself -- this library simply interacts with the NEURON executables. If it is, please contact the [NEURON team](https://www.neuron.yale.edu/phpBB/). If the issue is with this library, please create an [issue on Github](https://github.com/JustasB/hoc2swc/issues).

# Contributing

To contribute, please open an issue first and discuss your plan for contributing. Then fork this repository and commit a pull-request with your changes.