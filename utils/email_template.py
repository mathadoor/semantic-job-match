"""The purpose of this script is to create custom verification templates for the AWS SES service."""

import boto3
import json
import os
import logging

# Get email template from the config file
parent_dir = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(parent_dir, "aws-app/chalicelib/app_config.json"), "r") as f:
    config = json.load(f)

config = config["INFRA"]["AWS"]["SES"]

template_input = {
    "TemplateName": config["TEMPLATE_NAME"],
    "SubjectPart": "Please confirm your email address",
    "HtmlPart": """<html>
                      <head></head>
                      <body style='font-family:sans-serif;'>
                        <h1 style='text-align:center'>You are one click away from getting a job!</h1>
                        <p>We here at Example Corp are happy to have you on
                          board! There's just one last step to complete before
                          you can start sending email. Just click the following
                          link to verify your email address. Once we confirm that
                          you're really you, we'll give you some additional
                          information to help you get started with ProductName.</p>
                      </body>
                      </html>""",
}

# Check if the template exists
ses_client = boto3.client("ses")
response = ses_client.list_templates()
if config["TEMPLATE_NAME"] not in [template["Name"] for template in response["TemplatesMetadata"]]:
    response = ses_client.create_template(Template=template_input)
else: # Update the template
    response = ses_client.update_template(Template=template_input)
