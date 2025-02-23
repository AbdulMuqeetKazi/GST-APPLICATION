import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

# Initialize session state
if 'invoices' not in st.session_state:
    st.session_state.invoices = []

def calculate_gst(amount, rate):
    return (amount * rate) / 100

def calculate_total_tax(df):
    return df['cgst'].sum() + df['sgst'].sum() + df['igst'].sum()

def main():
    st.set_page_config(page_title="GST Simplify AI", layout="wide")
    
    st.title("GST Simplify AI")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Choose a function",
        ["Invoice Manager", "Tax Calculator", "Reports & Analytics", "Compliance Calendar"]
    )
    
    if page == "Invoice Manager":
        invoice_manager()
    elif page == "Tax Calculator":
        tax_calculator()
    elif page == "Reports & Analytics":
        reports_analytics()
    else:
        compliance_calendar()

def invoice_manager():
    st.header("Invoice Manager")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Invoice")
        invoice_no = st.text_input("Invoice Number")
        date = st.date_input("Invoice Date")
        party_name = st.text_input("Party Name")
        amount = st.number_input("Amount (pre-tax)", min_value=0.0)
        
        transaction_type = st.selectbox(
            "Transaction Type",
            ["Intra-state", "Inter-state"]
        )
        
        if transaction_type == "Intra-state":
            gst_rate = st.selectbox("GST Rate (%)", [5, 12, 18, 28])
            cgst = calculate_gst(amount, gst_rate/2)
            sgst = calculate_gst(amount, gst_rate/2)
            igst = 0
        else:
            gst_rate = st.selectbox("IGST Rate (%)", [5, 12, 18, 28])
            cgst = 0
            sgst = 0
            igst = calculate_gst(amount, gst_rate)
            
        if st.button("Add Invoice"):
            invoice = {
                "invoice_no": invoice_no,
                "date": str(date),
                "party_name": party_name,
                "amount": amount,
                "transaction_type": transaction_type,
                "gst_rate": gst_rate,
                "cgst": cgst,
                "sgst": sgst,
                "igst": igst,
                "total": amount + cgst + sgst + igst
            }
            st.session_state.invoices.append(invoice)
            st.success("Invoice added successfully!")
    
    with col2:
        st.subheader("Recent Invoices")
        if st.session_state.invoices:
            df = pd.DataFrame(st.session_state.invoices)
            st.dataframe(df)
        else:
            st.info("No invoices added yet")

def tax_calculator():
    st.header("GST Calculator")
    
    amount = st.number_input("Enter Amount (pre-tax)", min_value=0.0)
    gst_rate = st.slider("Select GST Rate (%)", 0, 28, step=1)
    
    if st.button("Calculate"):
        cgst = calculate_gst(amount, gst_rate/2)
        sgst = calculate_gst(amount, gst_rate/2)
        total = amount + cgst + sgst
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Base Amount", f"₹{amount:,.2f}")
        col2.metric("CGST", f"₹{cgst:,.2f}")
        col3.metric("SGST", f"₹{sgst:,.2f}")
        col4.metric("Total Amount", f"₹{total:,.2f}")

def reports_analytics():
    st.header("Reports & Analytics")
    
    if not st.session_state.invoices:
        st.info("No data available for analysis. Please add some invoices first.")
        return
    
    df = pd.DataFrame(st.session_state.invoices)
    df['date'] = pd.to_datetime(df['date'])
    
    # Monthly tax liability
    st.subheader("Monthly Tax Liability")
    monthly_tax = df.groupby(df['date'].dt.strftime('%Y-%m'))[['cgst', 'sgst', 'igst']].sum()
    fig = px.bar(monthly_tax, title="Monthly GST Breakdown")
    st.plotly_chart(fig)
    
    # Tax rate distribution
    st.subheader("Transaction Distribution by GST Rate")
    rate_dist = df['gst_rate'].value_counts()
    fig = px.pie(values=rate_dist.values, names=rate_dist.index, title="GST Rate Distribution")
    st.plotly_chart(fig)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions", len(df))
    col2.metric("Total Tax Collected", f"₹{calculate_total_tax(df):,.2f}")
    col3.metric("Average Transaction Value", f"₹{df['amount'].mean():,.2f}")

def compliance_calendar():
    st.header("Compliance Calendar")
    
    # Sample compliance deadlines
    deadlines = {
        "GSTR-1": "11th of next month",
        "GSTR-3B": "20th of next month",
        "GSTR-9": "31st December",
        "Annual Return": "31st December"
    }
    
    st.subheader("Important Deadlines")
    for return_type, deadline in deadlines.items():
        st.write(f"**{return_type}:** {deadline}")
    
    # Compliance checklist
    st.subheader("Monthly Compliance Checklist")
    tasks = [
        "Reconcile purchase and sales registers",
        "Check for missing invoices",
        "Verify ITC claims",
        "Review reverse charge applicability",
        "Check e-way bill compliance",
        "Verify tax payment details"
    ]
    
    for task in tasks:
        st.checkbox(task)

if __name__ == "__main__":
    main()
