import hoc2swc, os, pytest

def test_nonexistingHOC():
    actual_swc = "tests/testFiles/ca1/CA1-temp.swc"

    with pytest.raises(Exception):
        hoc2swc.hoc2swc("XYZ/test.hoc", actual_swc)

def test_python_CA1():
    actual_swc = "tests/testFiles/ca1/CA1-temp.swc"
    expected_swc = "tests/testFiles/ca1/CA1.swc"

    hoc2swc.hoc2swc("tests/testFiles/ca1/CA1.hoc", actual_swc)

    assert os.path.exists(actual_swc)

    try:
        assert os.system("diff -w " + actual_swc + " " + expected_swc) == 0
    finally:
        os.system("rm " + actual_swc)

def test_nrniv_CA1():
    actual_swc = "tests/testFiles/ca1/CA1-temp.swc"
    expected_swc = "tests/testFiles/ca1/CA1.swc"

    os.system("nrniv -python hoc2swc.py -tests/testFiles/ca1/CA1.hoc -"+actual_swc)

    assert os.path.exists(actual_swc)

    try:
        assert os.system("diff -w " + actual_swc + " " + expected_swc) == 0
    finally:
        os.system("rm " + actual_swc)

if __name__ == "__main__":
    test_python_CA1()