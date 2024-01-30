from pypdf import PdfReader

""" This module is used to parse the pdf file and extract the text from it. """


class PDFParser:
    """
    A simple PDFParser class
    """

    def __init__(self, file):
        self.file = file

    def extract_text(self):
        """
        Extracts the text from the pdf file

        Returns
        -------
            text: A string containing the text from the pdf file

        """
        reader = PdfReader(self.file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text

    def convert_to_json(self):
        """
        Converts the text from the pdf file to a json format

        Returns
        -------
            json: A json object containing the text from the pdf file
        """

        text = self.extract_text()
        return {"text": text}
