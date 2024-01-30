"""This file contains the tests for PDF parsing functionality."""

import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def pdf_file():
    return os.path.join(os.path.dirname(__file__), "data/test_resume.pdf")


def test_pdf_parser(pdf_file):
    from pdf_parser import PDFParser

    parser = PDFParser(pdf_file)
    text = parser.extract_text()
    print(text)
    assert text is not None
    assert len(text) > 0
    assert isinstance(text, str)