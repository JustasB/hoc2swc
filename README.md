[![Build Status](https://travis-ci.com/JustasB/pylmeasure.svg?branch=master)](https://travis-ci.com/JustasB/pylmeasure)
[![Coverage Status](https://coveralls.io/repos/github/JustasB/pylmeasure/badge.svg?branch=master)](https://coveralls.io/github/JustasB/pylmeasure?branch=master)
[![PyPI version](https://badge.fury.io/py/pylmeasure.svg)](https://badge.fury.io/py/pylmeasure)

# PyLMeasure: A Python Wrapper for L-Measure.

[PyLMeasure](https://pypi.org/project/pylmeasure/) is a Python wrapper library for the [command-line interface](http://cng.gmu.edu:8080/Lm/help/cmdLineUsageDoc.html) of the neuronal morphology analysis tool [L-Measure](http://cng.gmu.edu:8080/Lm/help/index.htm).

# Installation

To install the library, simply type in `pip install pylmeasure` in your terminal.

The above command includes the necessary binaries -- no need to download L-Measure separatelly or install Java.

# Usage

The basic usage is:

```
from pylmeasure import *

# Specify the L-Measure to compute, full list: http://cng.gmu.edu:8080/Lm/help/index.htm
LMOutput = getMeasure(['Surface', 'Diameter'], ["path/to/file.swc"])

#                                              V-- measure index           V-- file index
print("Surface area of first file:",  LMOutput[0]["WholeCellMeasuresDict"][0]["TotalSum"])
print("Mean diameter in first file:", LMOutput[1]["WholeCellMeasuresDict"][0]["Average"])
```

For more examples, see [this Jupyter notebook](https://github.com/JustasB/pylmeasure/blob/master/PyLMeasure%20Usage.ipynb).

# Issues
If you encounter an issues, first make sure it's not due to L-Measure itself -- this library simply wraps the L-Measure executables. If it is, please contact the [L-Measure team](http://cng.gmu.edu:8080/Lm/). If the issue is with this library, please create an [issue on Github](https://github.com/JustasB/pylmeasure/issues).

# Contributing

To contribute, please open an issue first and discuss your plan for contributing. Then fork this repository and commit a pull-request with your changes.

# Acknowledgements

This wrapper library project was initialy started by [Ajayrama Kumaraswamy](https://github.com/ajkswamy). View [the original source](https://github.com/ajkswamy/python-Lmeasure).
