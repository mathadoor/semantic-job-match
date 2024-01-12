import os
import sys
import pytest


@pytest.fixture(scope="session", autouse=True)
def add_parent_directory_to_path():
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(parent_dir)
