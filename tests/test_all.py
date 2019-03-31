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

    assert os.system("diff -w " + actual_swc + " " + expected_swc) == 0

def test_nrniv_CA1():
    actual_swc = "tests/testFiles/ca1/CA1-temp.swc"
    expected_swc = "tests/testFiles/ca1/CA1.swc"

    os.system("nrniv -python hoc2swc.py -tests/testFiles/ca1/CA1.hoc -"+actual_swc)

    assert os.path.exists(actual_swc)

    assert os.system("diff -w " + actual_swc + " " + expected_swc) == 0

def test_python_synthetic():
    actual_swc = "tests/testFiles/synthetic/TestCell-temp.swc"
    expected_swc = "tests/testFiles/synthetic/TestCell.swc"

    hoc2swc.hoc2swc("tests/testFiles/synthetic/TestCell.hoc", actual_swc)

    assert os.path.exists(actual_swc)

    assert os.system("diff -w " + actual_swc + " " + expected_swc) == 0

def test_python_granule():
    actual_swc = "tests/testFiles/granule/gc-temp.swc"
    expected_swc = "tests/testFiles/granule/gc.swc"

    hoc2swc.hoc2swc("tests/testFiles/granule/gc-plast.hoc", actual_swc)

    assert os.path.exists(actual_swc)

    assert os.system("diff -w " + actual_swc + " " + expected_swc) == 0

def test_python_multi_granule():
    expected_swc1 = "tests/testFiles/multi-granule/gc_0000.swc"
    expected_swc2 = "tests/testFiles/multi-granule/gc_0001.swc"

    actual_swc1 = "tests/testFiles/multi-granule/gc-temp_0000.swc"
    actual_swc2 = "tests/testFiles/multi-granule/gc-temp_0001.swc"

    hoc2swc.hoc2swc("tests/testFiles/multi-granule/granule.hoc", "tests/testFiles/multi-granule/gc-temp.swc")

    assert os.path.exists(actual_swc1)
    assert os.path.exists(actual_swc2)

    assert os.system("diff -w " + actual_swc1 + " " + expected_swc1) == 0
    assert os.system("diff -w " + actual_swc2 + " " + expected_swc2) == 0

if __name__ == "__main__":
    # test_python_synthetic()
    # test_python_CA1()
    test_python_granule()
    # test_python_multi_granule()