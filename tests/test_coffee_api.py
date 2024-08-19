import os

def test_file_exists():
    assert os.path.isfile('file_to_check.txt'), "file_to_check.txt does not exist."