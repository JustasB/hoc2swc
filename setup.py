import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hoc2swc",
    version="0.1",
    author="Justas Birgiolas",
    author_email="justas@asu.edu",
    description="Convert NEURON simulator .HOC files to .SWC morphology format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/justasb/hoc2swc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)