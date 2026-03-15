import streamlit as st
import io
import os
import requests
import PyPDF2
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

st.set_page_config(page_title="AI Resume Reviewer", page_icon="📄", layout="centered")

st.title("AI Resume Reviewer")
st.markdown("Upload your resume and get feedback on how to improve it!")

if not NVIDIA_API_KEY:
    st.error("NVIDIA API key not found. Please add it to your .env file.")
    st.stop()

upload_file = st.file_uploader("UPLOAD YOUR RESUME (PDF, TXT)", type=["pdf","txt"])
job_role = st.text_input("ENTER THE JOB ROLE YOU'RE TARGETING (OPTIONAL)")
analyse = st.button("ANALYSE MY RESUME")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    else:
        return uploaded_file.read().decode("utf-8")

if analyse and upload_file:
    try:
        file_content = extract_text_from_file(upload_file)

        if not file_content.strip():
            st.error("File does not contain readable text.")
            st.stop()

        prompt = f"""
You are an expert HR recruiter and resume reviewer.

Analyze the following resume and provide constructive feedback.

Focus on:
1. Content clarity and impact
2. Skills presentation
3. Experience descriptions
4. Improvements for {job_role if job_role else "general job applications"}

Resume:
{file_content}

Provide structured suggestions and actionable improvements.
"""

        url = "https://integrate.api.nvidia.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-ai/deepseek-v3.2",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert resume reviewer with HR experience."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 2048
        }

        with st.spinner("Analyzing your resume..."):
            response = requests.post(url, headers=headers, json=data)

        result = response.json()

        st.markdown("### Analysis Results")

        if "choices" in result:
            st.write(result["choices"][0]["message"]["content"])
        else:
            st.error("API Error Response")
            st.json(result)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif analyse:
    st.error("Please upload a resume file to analyze.")