import re
import streamlit as st
import boto3
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from user_profile import UserProfile

# User Interface
st.markdown('''# Semantic Job Matcher''')

st.markdown('''The Semantic Job Matcher is a tool that uses state of the art NLP techniques to match your resume
to relevant job postings. Please add your information below, along with your resume and a preferred job title. 
We will then match your resume to relevant job postings on a regular basis and send you an email.''')

st.markdown('''## Personal Information''')

name = st.text_input('Name')


# def validate_email(string):
#     # Regular expression to validate email
#     query = r"\b[A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}\b"
#
#     if re.fullmatch(query, string):
#         return True
#
#     return False


email = st.text_input('Email')

frequency = st.selectbox('Email Frequency', ['Daily', 'Weekly', 'Monthly'])

job_title = st.selectbox('Preferred Job Title',
                         ['Data Scientist', 'Data Analyst', 'Software Engineer', 'Machine Learning Engineer'])

st.markdown('''## Please Upload Your Resume''')
resume = st.file_uploader('Resume', type=['pdf'])

# Button to submit information
if st.button('Submit'):
    # If any of the entries are not valid, display error message in red
    profile = UserProfile(name, email, frequency, job_title, resume)
    status = profile.validate_profile()

    if status == "valid":
        response = profile.send_email()
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            st.write(f'Thank you for submitting your information. An email has been sent to you for verification'
                     f' Once verified, we will send you job postings that match your resume on {frequency} basis.')
    elif status == "existing":
        pass
    else:
        pass
    # if (name == ""
    #         or not validate_email(email)
    #         or resume is None):
    #     st.markdown('<p style="color: red;">Please Enter Valid Information</p>', unsafe_allow_html=True)
    # # else:
    #
    #     st.write(f'Thank you for submitting your information. An email has been sent to you for verification'
    #              f' Once verified, we will send you job postings that match your resume on {frequency} basis.')
    #
    #     # Load the configuration
    #     with open('./aws-app/chalicelib/app_config.json', 'r') as f:
    #         config = json.load(f)
    #
    #     # Check if the bucket exists, if not create it
    #     s3_client = boto3.client('s3')
    #     bucket_name = config['INFRA']['AWS']['S3']['RESUME_BUCKET']
    #     if bucket_name not in [bucket['Name'] for bucket in s3_client.list_buckets()['Buckets']]:
    #         s3_client.create_bucket(Bucket=bucket_name)
    #
    #     # Upload the resume to the bucket
    #     s3_client.upload_fileobj(resume, bucket_name, f"{name}_{email}_resume.pdf")

        # Upload the information to the database
