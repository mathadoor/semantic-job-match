import re
import streamlit as st

# function to validate email


st.markdown('''# Semantic Job Matcher''')

st.markdown('''The Semantic Job Matcher is a tool that uses state of the art NLP techniques to match your resume
to relevant job postings. Please add your information below, along with your resume and a preferred job title. 
We will then match your resume to relevant job postings on a regular basis and send you an email.''')

st.markdown('''## Personal Information''')

name = st.text_input('Name')


def validate_email(string):
    # Regular expression to validate email
    query = r"\b[A-Za-z0-9\._%\+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}\b"

    if re.fullmatch(query, string):
        return True

    return False


email = st.text_input('Email')

frequency = st.selectbox('Email Frequency', ['Daily', 'Weekly', 'Monthly'])

st.selectbox('Preferred Job Title',
             ['Data Scientist', 'Data Analyst', 'Software Engineer', 'Machine Learning Engineer'])

st.markdown('''## Please Upload Your Resume''')
resume = st.file_uploader('Resume', type=['pdf'])

# Button to submit information
if st.button('Submit'):
    # If any of the entries are not valid, display error message in red
    if (name == ""
            or not validate_email(name)
            or resume is None):
        st.markdown('<p style="color: red;">Please Enter Valid Information</p>', unsafe_allow_html=True)
    else:
        st.write(f'Thank you for submitting your information. We will send you job postings '
                 f'that match your resume on {frequency.text} basis.')
