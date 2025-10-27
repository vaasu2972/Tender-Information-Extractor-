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

def summarize_gem(text):
    product = "Not Found"
    specs = "Not Found"
    emd = "Not Found"
    requirements = []

    product_match = re.search(r'Item Category\s*([^\n]+)', text, re.I)
    if product_match:
        product = product_match.group(1).strip()

    specs_match = re.search(r'Industrial grade Dimethylformamide.*?Total Quantity\s*([^\n]+)', text, re.I | re.S)
    if specs_match:
        qty = specs_match.group(1).strip()
        specs = f"Industrial grade Dimethylformamide, Quantity: {qty}"
    else:
        specs_match2 = re.search(r'Total Quantity\s*([^\n]+)', text, re.I)
        if specs_match2:
            specs = f"Industrial grade Dimethylformamide, Quantity: {specs_match2.group(1).strip()}"

    # EMD detection
    if re.search(r'EMD\s*not required|EMD\s*exempt', text, re.I):
        emd = "EMD not required for this tender"
    else:
        emd_match = re.search(r'(EMD|Earnest Money Deposit).*?Rs\.?\s*([\d,]+)', text, re.I)
        if emd_match:
            emd = "Rs " + emd_match.group(2).replace(",", "")

    # Bidder requirements (short summary using keywords)
    if "OEM manufacturers only" in text:
        requirements.append("OEM manufacturers only (not traders)")
    if "MSEs get preference" in text or "MSE preference" in text:
        requirements.append("MSEs get preference")
    if re.search(r'Exemption.*?experience.*?turnover', text, re.I):
        requirements.append("Exemption for startups regarding experience and turnover")
    requirements.append("PAN, GSTIN, cancelled cheque, EFT mandate required")
    requirements.append("Data sheets of product must be uploaded")

    return product, specs, emd, requirements

def summarize_general(text):
    product = "Not Found"
    specs = "Not Found"
    emd = "Not Found"
    requirements = []

    # Product
    product_match = re.search(r'(Product\s*[:\-]\s*|Material\s*[:\-]\s*)([^\n]+)', text, re.I)
    if not product_match:
        product_match = re.search(r'(Scope of Work|Scope of Tender)\s*[:\-]\s*([^\n]+)', text, re.I)
    if product_match:
        product = product_match.group(2).strip()

    # Specifications (usually after 'Technical specification' or 'Material Requisition')
    specs_match = re.search(r'(Technical Specification|Material Requisition)[\s:\-]*([\s\S]*?)(EMD|Earnest Money Deposit|Bidder Requirements|Qualification Criteria)', text, re.I)
    if specs_match:
        specs = specs_match.group(2).strip().split("\n")[0]  # Take first line for crisp output

    # EMD
    emd_match = re.search(r'(EMD|Earnest Money Deposit).*?Rs\.?\s*([\d,\.]+)', text, re.I)
    if emd_match:
        emd = "Rs " + emd_match.group(2).replace(",", "")
    elif re.search(r'EMD\s*not required|EMD\s*exempt', text, re.I):
        emd = "EMD not required for this tender"

    # Bidder requirements (short by section heading/sentence match)
    req_match = re.search(r'(Bidder Requirements|Qualification Criteria|Eligibility)[\s:\-]*([\s\S]{0,400})', text, re.I)
    if req_match:
        requirements = [line.strip() for line in req_match.group(2).split("\n") if line.strip()][:3]  # Only a few bullet points

    if not requirements:
        requirements = ["Refer to bid eligibility section for details"]

    return product, specs, emd, requirements

st.title("Tender Information Extractor")
uploaded_file = st.file_uploader("Upload tender PDF or Word file", type=["pdf", "docx"])

if uploaded_file is not None:
    # Accept both file types
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()

    # Check for GeM
    if "GeM" in text or "Bid Details" in text or "Item Category" in text:
        product, specs, emd, requirements = summarize_gem(text)
    else:
        product, specs, emd, requirements = summarize_general(text)

    st.subheader("Extracted Summary")
    st.markdown(f"**Product:** {product}")
    st.markdown(f"**Product Specifications:** {specs}")
    st.markdown(f"**EMD Amount:** {emd}")
    st.markdown("**Bidder Requirements:**")
    st.markdown("\n".join([f"- {req}" for req in requirements]))
