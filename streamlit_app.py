import re
import streamlit as st

# function to validate email


st.markdown('''# Semantic Job Matcher''')

st.markdown('''The Semantic Job Matcher is a tool that uses state of the art NLP techniques to match your resume
to relevant job postings. Please add your information below, along with your resume and a preferred job title. 
We will then match your resume to relevant job postings on a regular basis and send you an email.''')

st.markdown('''## Personal Information''')

name = st.text_input('Name')




email = st.text_input('Email')
frequency = st.selectbox('Email Frequency', ['Daily', 'Weekly', 'Monthly'])

st.markdown('''## Please Enter Your Preferred Job Title''')
st.selectbox('Job Title', ['Data Scientist', 'Data Analyst', 'Software Engineer', 'Machine Learning Engineer'])

st.markdown('''## Please Upload Your Resume''')
resume = st.file_uploader('Resume', type=['pdf'])

# Button to submit information
if st.button('Submit'):
    st.write(f'Thank you for submitting your information. We will send you job postings '
             f'that match your resume on {frequency.text} basis.')
