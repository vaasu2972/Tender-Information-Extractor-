import streamlit as st
from io import StringIO
import pdfplumber
import docx2txt
import re

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    return docx2txt.process(file)

def extract_product(text):
    # Example pattern to find product name after words like 'Product:', 'Item:', etc.
    match = re.search(r'Product\s*[:\-]\s*([^\n\r]+)', text, re.I)
    if match:
        return match.group(1).strip()
    return "Not Found"

def extract_product_specifications(text):
    # Extract text block between 'Specifications' and 'EMD' keywords as an example
    specs = ""
    specs_match = re.search(r'Specifications(.*?)(Earnest Money Deposit|EMD)', text, re.I | re.S)
    if specs_match:
        specs = specs_match.group(1).strip()
        # Optional: clean specs text here
    return specs if specs else "Not Found"

def extract_emd(text):
    # Look for EMD amount patterns like 'EMD: Rs XXXX' or 'Earnest Money Deposit: Rs XXXX'
    match = re.search(r'(EMD|Earnest Money Deposit).*?Rs\.?\s*([\d,]+)', text, re.I)
    if match:
        return "Rs " + match.group(2).replace(",", "")
    return "Not Found"

def extract_bidder_requirements(text):
    # Extract section called 'Bidder Requirements' or similar keywords
    match = re.search(r'(Bidder Requirements|Eligibility|Qualification Criteria)(.*?)(\n\n|\Z)', text, re.I | re.S)
    if match:
        return match.group(2).strip()
    return "Not Found"

st.title("Tender Document Extractor")

uploaded_file = st.file_uploader("Upload tender PDF or Word file", type=["pdf", "docx"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()

    st.subheader("Extracted Information")
    st.markdown("**Product:**")
    st.write(extract_product(text))

    st.markdown("**Product Specifications:**")
    st.write(extract_product_specifications(text))

    st.markdown("**EMD Amount:**")
    st.write(extract_emd(text))

    st.markdown("**Bidder Requirements:**")
    st.write(extract_bidder_requirements(text))
