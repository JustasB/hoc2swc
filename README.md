[![Build Status](https://travis-ci.com/JustasB/hoc2swc.svg?branch=master)](https://travis-ci.com/JustasB/hoc2swc)
[![codecov](https://codecov.io/gh/JustasB/hoc2swc/branch/master/graph/badge.svg)](https://codecov.io/gh/JustasB/hoc2swc)
[![PyPI version](https://badge.fury.io/py/hoc2swc.svg)](https://badge.fury.io/py/hoc2swc)

# hoc2swc: A Python package to convert NEURON cell HOC files to SWC morphology files

[hoc2swc](https://pypi.org/project/hoc2swc/) is a Python library that converts the morphology of neuron models defined using [NEURON simulator](https://neuron.yale.edu) [HOC files](https://www.neuron.yale.edu/neuron/static/new_doc/programming/hocsyntax.html) to the popular [SWC morphology format](http://www.neuronland.org/NLMorphologyConverter/MorphologyFormats/SWC/Spec.html). The library can also be used to convert cell morphologies instantiated in NEURON simulator (e.g. models that were built using NEURON+Python).

Once converted to SWC, tools that can consume SWC files can be used to [compute SWC morphology metrics](https://pypi.org/project/pylmeasure/), create [professional 3D neuron morphology visualizations](https://github.com/MartinPyka/SWC2Blender), etc...

# Requirements

hoc2swc requires a working version of NEURON 7.5+ either installed from a [package/installer](https://www.neuron.yale.edu/neuron/download) (easier) or [compiled](https://neurojustas.com/2018/03/27/tutorial-installing-neuron-simulator-with-python-on-ubuntu-linux/) (more challenging). Linux, Mac, and Windows versions are supported.

You must be able to run at least *one* of these commands in a terminal window without errors:
 - `nrniv -python`
 - Or `python -c 'from neuron import h'`

If you cannot run any of these commands, it indicates that there is something amiss with your NEURON installation. Search the error messages on the [NEURON forum](https://www.neuron.yale.edu/phpBB/) for help.

## MOD files
The library assumes that the .mod files (mechanisms) used by the .hoc file are stored in the same
directory as the .hoc file. You may need to place the .hoc and .mod files in the same folder before running this script.

**Attention Windows users**: Once .mod and .hoc files are in the same location, the .mod files have to be compiled. Follow
 these steps to [compile the .mod files on Windows](https://www.neuron.yale.edu/neuron/static/docs/nmodl/mswin.html#v51).
 Linux and Mac users can skip this step, as the library will compile the .mod files automatically.

# Installation and Usage

Installation and usage depends on how you installed NEURON simulator (installed vs. compiled). More customizable functionality is available for those who compiled.

## If you installed a downloaded NEURON package
Download and extract [this hoc2swc ZIP file](https://github.com/JustasB/hoc2swc/archive/master.zip) to a known folder. This folder will have a script named `hoc2swc.py`. Note its location.

Then, to convert a HOC file, run the following command in terminal (note the '-'s before the hoc and swc paths):

`nrniv -python path/to/hoc2swc.py -path/to/cell.hoc -path/to/converted.swc`

The command will start NEURON, load the HOC file, and convert it to SWC.

## If you compiled NEURON+Python

To install the library, simply type in `pip install hoc2swc` in your terminal.

Then in a Python session, run the following to convert a HOC file to SWC.

```
from hoc2swc import hoc2swc

hoc2swc("path/to/cell.hoc", "out.swc")
```

The command will start NEURON, load the HOC file, and convert it to SWC. NEURON is started in a separate process and the last line can be repeated multiple times to convert multiple HOC files.

See the following Jupyter Notebook for a working example: [hoc2swc NEURON+Python Usage.ipynb](https://github.com/JustasB/hoc2swc/blob/master/hoc2swc%20NEURON%2BPython%20Usage.ipynb)

### Exporting non-HOC or custom cells 
If a cell is not defined in a HOC file (e.g. defined using a custom script or using Python) or requires special steps to load it, you can first instantiate the cell in NEURON and when it is ready for export to SWC, use the following Python script to save all instantiated cells to SWC.

```
# Load your cell
from neuron import h
run_scripts_build_cell_etc()

# Export loaded cell to SWC
from hoc2swc import neuron2swc # this function exports all loaded cells to SWC
neuron2swc("out.swc")
```

Note to packaged NEURON users, if you start `nrniv -python` from the directory where the hoc2swc.py file is located OR append the location to the PYTHONPATH environment variable, the above lines will work for you as well.

# How it works
Surprisingly, [there is no easy way to save cell morphologies built using NEURON as SWC files](https://www.neuron.yale.edu/phpBB/viewtopic.php?t=787). Which means, it's
difficult to compute cell model morphology metrics using tools like [L-Measure](http://cng.gmu.edu:8080/Lm/), or use an [SWC viewer](https://neuroinformatics.nl/HBP/morphology-viewer/), which works with SWC
files. It's possible to [import SWC files into NEURON](https://www.neuron.yale.edu/phpBB/viewtopic.php?t=3257), but not export. There is [NLMorphologyConverter](http://www.neuronland.org/NLMorphologyConverter/NLMorphologyConverter.html), but none of the versions available were able to convert any of the HOC files I tested.

However, NEURON allows traversing all 3D points of an instantiated model. This can then be used to create the list of points for the SWC file.

While this approach requires a running instance of NEURON, it avoids the need to write a NEURON HOC file parser --
it simply leverages NEURON's HOC parser and h.xyzdiam3d() methods. As a side effect, this approach also allows converting 
NEURON cell model morphologies to SWC, even if HOC was not used to build the cell model (e.g. multiple 
HOC files or a Python script).

In theory, one could perform the above steps and implement a Neuron->SWC converter on their own. However, this library has been packaged and made freely available to reduce the above effort to just a few lines of code. If you find any bugs with this library, and were prepared to implement your own converter, consider fixing the bug and submitting a pull-request instead -- it might be faster to fix a bug here than to write the converter from scratch.

# Issues
If you encounter an issue, first make sure it's not due to NEURON itself -- this library simply interacts with the NEURON executables. If it is, please contact the [NEURON team](https://www.neuron.yale.edu/phpBB/). If the issue is with this library, please create an [issue on Github](https://github.com/JustasB/hoc2swc/issues).

# Contributing

To contribute, please open an issue first and discuss your plan for contributing. Then fork this repository and commit a pull-request with your changes.
