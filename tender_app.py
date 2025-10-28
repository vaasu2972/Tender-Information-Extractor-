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

def extract_field(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1).strip()
    return "Not Found"

def extract_table(text):
    fields = {
        "Organization name": [r'Organisation Name\s*:?[\s\n]+([^\n]+)', r'Organization Name\s*:?[\s\n]+([^\n]+)', r'MinistryState Name\s*:?[\s\n]+([^\n]+)', r'Office Name\s*:?[\s\n]+([^\n]+)'],
        "Tender No": [r'Tender No\s*:?[\s\n]+([^\n]+)', r'Bid Number\s*:?[\s\n]+([^\n]+)', r'Bid No.\s*:?[\s\n]+([^\n]+)'],
        "Tender Id": [r'Tender Id\s*:?[\s\n]+([^\n]+)', r'Bid ID\s*:?[\s\n]+([^\n]+)'],
        "Due Date": [r'Due Date\s*:?[\s\n]+([^\n]+)', r'Bid End DateTime\s*:?[\s\n]+([^\n]+)'],
        "Tender Type (Open / Limited)": [r'Tender Type\s*:?[\s\n]+([^\n]+)'],
        "BID TYPE": [r'BID TYPE\s*:?[\s\n]+([^\n]+)', r'Bid Type\s*:?[\s\n]+([^\n]+)'],
        "Item Name With Qty": [r'Item Name With Qty\s*:?[\s\n]+([^\n]+)', r'Item Category\s*:?[\s\n]+([^\n]+)', r'Name of Item\s*:?[\s\n]+([^\n]+)', r'(?i)Total Quantity\s*:?[\s\n]+([^\n]+)'],
        "EMD (Earnest Money Deposit)": [r'EMD\s*:?[\s\n]+([^\n]+)', r'Earnest Money Deposit\s*:?[\s\n]+([^\n]+)'],
        "Tender Fee": [r'Tender Fee\s*:?[\s\n]+([^\n]+)', r'Bid Participation Fee\s*:?[\s\n]+([^\n]+)'],
        "PQR (Qualify Requirement) / Experience Criteria": [r'(?:PQR\s*\(Qualify Requirement\)|Experience Criteria|Pre Qualification Requirement|Eligibility Criteria)[\s\n:]*([\s\S]{0,500}?)\n(?:[A-Z][^a-z]|$)'],
        "Sample required / Sample Delivery Location": [r'Sample required.*?([Yy]es|[Nn]o)', r'Sample Delivery Location\s*:?[\s\n]+([^\n]+)'],
        "Material Delivery Location": [r'Material Delivery Location\s*:?[\s\n]+([^\n]+)', r'Delivery Location\s*:?[\s\n]+([^\n]+)', r'Consignee(.*?)(?=Total Quantity)', r'Place of Delivery\s*:?[\s\n]+([^\n]+)'],
        "Delivery Schedule (in parts or in full)": [r'Delivery Schedule\s*:?[\s\n]+([^\n]+)', r'Delivery Days\s*:?[\s\n]+([^\n]+)', r'Delivery in (full|parts)'],
        "Validity of price": [r'Validity of price\s*:?[\s\n]+([^\n]+)', r'Price Validity\s*:?[\s\n]+([^\n]+)', r'Validity\s*:?[\s\n]+([^\n]+)'],
        "Mode of submission (Online/Offline)": [r'Mode of Submission\s*:?[\s\n]+([^\n]+)', r'Submission Type\s*:?[\s\n]+([^\n]+)'],
        "Reverse Auction status": [r'Reverse Auction status\s*:?[\s\n]+([^\n]+)', r'Bid to RA enabled\s*:?[\s\n]+([^\n]+)'],
        "Important documents attached": [r'(Documents Required[\s\S]+)', r'(Additional Doc[\s\S]+)']
    }

    results = {}
    for field, patterns in fields.items():
        results[field] = extract_field(text, patterns)
    return results

def markdown_table(data_dict):
    headers = "| **Parameter** | **Details** |\n|:---|:---|\n"
    rows = ""
    for key, value in data_dict.items():
        if key != "Important documents attached":
            cell = value.replace('\n', ' ').strip() if value else "Not Found"
            rows += f"| {key} | {cell} |\n"
    return headers + rows

st.title("Tender Information Extractor (Table Format)")

uploaded_file = st.file_uploader("Upload tender PDF or Word file", type=["pdf", "docx"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()

    # Extract fields and display as markdown table
    data = extract_table(text)
    st.markdown("#### Tender Parameter Table (Copy-Paste Friendly)")
    st.markdown(markdown_table(data))

    # Show important documents separately if found
    important_docs = data.get("Important documents attached", "")
    if important_docs and important_docs != "Not Found":
        st.markdown("#### Important Documents / Attachments")
        st.write(important_docs)
