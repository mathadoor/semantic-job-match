""" The purpose of this function is to provide a lower level abstraction for the submission form."""

from pdf_parser import PDFParser
import re
import boto3
import json
import os


def load_config():
    """
    Loads the configuration from the config file
    """
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(parent_dir, "aws-app/chalicelib/app_config.json"), "r") as f:
        config = json.load(f)
    return config


class UserProfile:
    """
    A class to confirm submission and email the user for verification
    """

    def __init__(self, name=None, email=None, frequency=None, job_title=None, resume=None):
        self.name = name
        self.email = email
        self.frequency = frequency
        self.job_title = job_title
        self.resume = resume
        self.ses_client = boto3.client('ses')
        self.db_client = boto3.client('dynamodb')
        self.config = load_config()

        if self.resume is not None:
            self.resume = PDFParser(self.resume).extract_text()

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

    def update_job_title(self, job_title):
        """
        Updates the job title of the user.
        :param job_title: The new job title
        :return: The new job title
        """
        self.job_title = job_title

    def update_resume(self, resume):
        """
        Updates the resume of the user.
        :param resume: The new resume
        """
        self.resume = resume
        self.resume = PDFParser(self.resume).extract_text()

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

    def validate_profile(self):
        """
        Validates the user profile

        Returns
        -------
            str: "valid" if the profile is valid, "existing" if the profile already exists, "invalid" otherwise
        """
        # Check if the profile is valid
        if (
                not self.validate_email()
                or self.resume is None
                or self.name == ""
                or self.frequency is None
                or self.job_title is None
        ):
            return "invalid"
        else:
            # Check if the user already exists
            # TODO: Implement this Functionality

            return "valid"

    def upload_profile(self):
        """
        Uploads the profile to the AWS Database
        """
        if self.validate_profile() == "valid":
            db_config = self.config["INFRA"]["AWS"]["DYNAMODB"]

            # Check if the table exists, if not create it
            if db_config["CANDIDATE_TABLE"] not in self.db_client.list_tables()["TableNames"]:
                self.db_client.create_table(
                    TableName=db_config["CANDIDATE_TABLE"],
                    KeySchema=[
                        {"AttributeName": "email", "KeyType": "HASH"}
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "email", "AttributeType": "S"}
                    ]
                )
                print("Table Created")
            response = self.db_client.put_item(
                TableName=db_config["CANDIDATE_TABLE"],
                Item={
                    "email": {"S": self.email},
                    "name": {"S": self.name},
                    "frequency": {"S": self.frequency},
                    "job_title": {"S": self.job_title},
                    "resume": {"S": self.resume}
                }
            )

    def send_email(self, custom=False):
        """
        Sends an email to the user for verification
        """
        # Check if the profile is valid
        if self.validate_profile() == "valid":
            # Load the configuration
            ses_config = self.config["INFRA"]["AWS"]["SES"]

            # Upload Profile to the Database
            self.upload_profile()

            # Send the confirmation email
            # DO NOT USE CUSTOM TEMPLATES TILL PRODUCTION SES GRANTED
            if custom:
                response = self.ses_client.send_custom_verification_email(
                    EmailAddress=self.email,
                    TemplateName=ses_config["TEMPLATE_NAME"]
                )
            else:
                response = self.ses_client.verify_email_identity(EmailAddress=self.email)

            return response
