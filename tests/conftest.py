import os
import sys
import pytest


@pytest.fixture(scope="session", autouse=True)
def add_parent_directory_to_path():
    app_dir = os.path.join(os.path.dirname(__file__), "../aws-app")
    utils_dir = os.path.join(os.path.dirname(__file__), "../utils")

    sys.path.append(utils_dir)
    sys.path.append(app_dir)