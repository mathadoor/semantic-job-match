""" The purpose of this function is to provide a lower level abstraction for the submission form."""

from pdf_parser import PDFParser
import re


class FormUtility:
    """
    A class to confirm submission and email the user for verification
    """

    def __init__(self, name, email=None, frequency=None, job_title=None, resume=None):
        self.name = name
        self.email = email
        self.frequency = frequency
        self.job_title = job_title
        self.resume = resume

    def update_email(self, email):
        """
        Updates the email of the user.
        :param email: The new email
        :return: Validity of the email. The email is only updated if it is valid.
        """
        if self.validate_email():
            self.email = email
            return True
        return False

    def update_frequency(self, frequency):
        """
        Updates the frequency of the user.
        :param frequency: The new frequency
        :return: The new frequency
        """
        self.frequency = frequency
        return self.frequency

    def update_job_title(self, job_title):
        """
        Updates the job title of the user.
        :param job_title: The new job title
        :return: The new job title
        """
        self.job_title = job_title
        return self.job_title

    def update_resume(self, resume):
        """
        Updates the resume of the user.
        :param resume: The new resume
        :return: The new resume
        """
        self.resume = resume
        return self.resume

    def validate_email(self):
        """
        Validates the email

        Returns
        -------
            bool: True if the email is valid, False otherwise
        """
        # Regular expression to validate email
        # [Any alphanumeric character]@[Any alphanumeric character].[At least two alphabetical characters]
        query = r"\b[A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}\b"

        if re.fullmatch(query, self.email):
            return True

        return False

    def send_email(self):
        """
        Sends an email to the user for verification
        """
        # Check if the email is valid
        if not self.validate_email():
            return False
        else:
            # Parse the resume
            parser = PDFParser(self.resume)
            text = parser.extract_text()

            # Send the confirmation email
