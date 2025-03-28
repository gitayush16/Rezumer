import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API Key is missing! Check your .env file.")
else:
    genai.configure(api_key=api_key)

# Set Tesseract path (Windows users only)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")

    print("Falling back to OCR for image-based PDF.")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")

    return text.strip()

# Function to get response from Gemini AI
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    base_prompt = f"""
    You are an experienced HR with technical expertise in various job roles. 
    Your task is to review the provided resume and provide insights.
    
    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""
        Compare this resume to the following job description:
        
        Job Description:
        {job_description}
        """
    
    response = model.generate_content(base_prompt)  # Always execute this

    return response.text.strip()

# Streamlit app
st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("AI Resume Analyzer")
st.write("Analyze your resume and match it with job descriptions using Google Gemini AI.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("Enter Job Description:", placeholder="Paste the job description here...")

if uploaded_file:
    st.success("Resume uploaded successfully!")

    with open("resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf("resume.pdf")

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing resume..."):
            try:
                analysis = analyze_resume(resume_text, job_description)
                st.success("Analysis complete!")
                st.write(analysis)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                
                #Footer
                st.markdown("---")
                st.markdown("""<p style= 'text-align: center;'> powered by <a href="https://gemini.google.com/">Google Gemini AI</a></p>""", unsafe_allow_html=True)
                
