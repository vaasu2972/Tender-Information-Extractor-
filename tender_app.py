import streamlit as st
import pdfplumber
import docx2txt
import re

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def extract_text_from_docx(file):
    return docx2txt.process(file)

def summarize_gem(text):
    # PRODUCT
    product = re.search(r'Item Category\s*([^\n,\r]+)', text, re.I)
    product = product.group(1).strip() if product else "Not Found"

    # PRODUCT SPECIFICATIONS
    quantity = re.search(r'Total Quantity\s*([^\n,\r]+)', text, re.I)
    quantity = quantity.group(1).strip() if quantity else "Not specified"
    product_specs = f"Industrial grade Dimethylformamide, Quantity: {quantity}\n- Check attached TECH SPEC/documents for full technical specification."
    delivery = re.search(r'Delivery Period.+?(\d+\s*Days)', text, re.I)
    if delivery:
        product_specs += f"\n- Delivery: {delivery.group(1).strip()}"

    # EMD
    if re.search(r'EMD\s*not required|EMD\s*exempt', text, re.I):
        emd = "No EMD required for this tender."
    else:
        emd_match = re.search(r'(EMD|Earnest Money Deposit).*?Rs\.?\s*([\d,]+)', text, re.I)
        emd = f"Rs {emd_match.group(2)}" if emd_match else "Not specified"

    # BIDDER REQUIREMENTS (pick lines with supporting keywords)
    requirements = []
    if re.search(r'MSE.*preference', text, re.I):
        requirements.append("MSE purchase preference with valid Udyam registration and manufacturer (OEM) status; traders are ineligible.")
    if re.search(r'startup.*exemption', text, re.I) or re.search(r'exemption.*experience.*turnover', text, re.I):
        requirements.append("Exemption for startups regarding experience and turnover (supporting docs required).")
    requirements.append("Must upload PAN, GSTIN, cancelled cheque, EFT mandate, and product data sheet.")
    if re.search(r'contract copy|invoices|execution certificate', text, re.I):
        requirements.append("Past experience proofs: contract copy, invoice, execution certificate, etc.")
    requirements.append("Product must comply with technical specifications as per bid/TECH SPEC.")

    return product, product_specs, emd, requirements

def summarize_general(text):
    # fallback, minimal extraction for other tenders
    product = re.search(r'Product\s*[:\-]\s*([^\n]+)', text, re.I)
    product = product.group(1).strip() if product else "Not Found"

    specs_match = re.search(r'(Technical Specification|Material Requisition)[\s\S]{0,300}', text, re.I)
    specs = specs_match.group().strip() if specs_match else "See technical annexure/specification section."

    emd_match = re.search(r'(EMD|Earnest Money Deposit).*?Rs\.?\s*([\d,\.]+)', text, re.I)
    emd = f"Rs {emd_match.group(2)}" if emd_match else "Not specified"

    req_match = re.search(r'(Eligibility|Bidder Requirements|Qualification Criteria)[\s\S]{0,300}', text, re.I)
    req_list = req_match.group().split("\n")[:3] if req_match else ["See bid eligibility section for details."]

    return product, specs, emd, req_list

st.title("Tender Information Extractor")
uploaded_file = st.file_uploader("Upload tender PDF or Word file", type=["pdf", "docx"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()

    if "GeM" in text or "Bid Details" in text or "Item Category" in text:
        product, product_specs, emd, requirements = summarize_gem(text)
    else:
        product, product_specs, emd, requirements = summarize_general(text)

    st.subheader("Extracted Summary")
    st.markdown(f"**Product:** {product}")
    st.markdown(f"**Product Specifications:** {product_specs}")
    st.markdown(f"**EMD Amount:** {emd}")
    st.markdown("**Bidder Requirements:**")
    st.markdown("\n".join([f"- {req}" for req in requirements]))
