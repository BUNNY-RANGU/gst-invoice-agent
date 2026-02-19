"""
GST Invoice Agent - Streamlit Frontend
Beautiful web interface for invoice management
Author: Bunny Rangu
Day: 7/30
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json


# Session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
# Page config
st.set_page_config(
    page_title="GST Invoice Agent",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2563eb;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# LOGIN PAGE              ← YOUR PASTED CODE STARTS HERE
# ========================

def show_login_page():
    st.markdown('<h1 class="main-header">🔐 GST Invoice Agent</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            login_btn = st.form_submit_button("🔑 Login", use_container_width=True)
            
            if login_btn:
                if not username or not password:
                    st.error("Please enter username and password!")
                else:
                    with st.spinner("Logging in..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/api/auth/login",
                                json={
                                    "username": username,
                                    "password": password
                                }
                            )
                            if response.status_code == 200:
                                data = response.json()
                                st.session_state.logged_in = True
                                st.session_state.token = data['access_token']
                                st.session_state.username = data['user']['username']
                                st.session_state.user_role = data['user']['role']
                                st.success(f"✅ {data['message']}")
                                st.rerun()
                            else:
                                st.error(f"❌ {response.json().get('detail', 'Login failed')}")
                        except Exception as e:
                            st.error(f"❌ API Offline! Start the API server first!")
    
    with tab2:
        st.subheader("Create new account")
        with st.form("register_form"):
            reg_username = st.text_input("Username*", placeholder="Choose username")
            reg_fullname = st.text_input("Full Name", placeholder="Your full name")
            reg_email = st.text_input("Email*", placeholder="your@email.com")
            reg_password = st.text_input("Password*", type="password", placeholder="Min 8 characters")
            reg_confirm = st.text_input("Confirm Password*", type="password", placeholder="Repeat password")
            register_btn = st.form_submit_button("📝 Register", use_container_width=True)
            
            if register_btn:
                if not reg_username or not reg_email or not reg_password:
                    st.error("Please fill all required fields!")
                elif reg_password != reg_confirm:
                    st.error("Passwords don't match!")
                elif len(reg_password) < 8:
                    st.error("Password must be at least 8 characters!")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/api/auth/register",
                                json={
                                    "username": reg_username,
                                    "email": reg_email,
                                    "password": reg_password,
                                    "full_name": reg_fullname
                                }
                            )
                            if response.status_code == 200:
                                st.success("✅ Account created! Please login.")
                            else:
                                st.error(f"❌ {response.json().get('detail', 'Registration failed')}")
                        except Exception as e:
                            st.error(f"❌ API Offline! Start the API server first!")

# Check if logged in
if not st.session_state.logged_in:
    show_login_page()
    st.stop()

# Sidebar Navigation
st.sidebar.title("🧾 GST Invoice Agent")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "➕ Create Invoice", "📋 View Invoices", "📥 Export Reports", "📈 Analytics", "ℹ️ About"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Quick Stats")

# Get health check
try:
    health = requests.get(f"{API_URL}/health").json()
    st.sidebar.success(f"✅ System Healthy")
    st.sidebar.info(f"📈 Total Invoices: {health.get('total_invoices', 0)}")
except:
    st.sidebar.error("❌ API Offline")


# ====================
# PAGE 1: DASHBOARD
# ====================
if page == "📊 Dashboard":
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)
    
    try:
        # Get statistics
        stats_response = requests.get(f"{API_URL}/api/stats")
        
        if stats_response.status_code == 200:
            data = stats_response.json()
            
            if data['success'] and 'stats' in data and data['stats']:
                stats = data['stats']
                
                # Display metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="📄 Total Invoices",
                        value=stats.get('total_invoices', 0)
                    )
                
                with col2:
                    st.metric(
                        label="💰 Total Revenue",
                        value=f"₹{stats.get('total_revenue', 0):,.2f}"
                    )
                
                with col3:
                    st.metric(
                        label="💸 GST Collected",
                        value=f"₹{stats.get('total_gst_collected', 0):,.2f}"
                    )
                
                with col4:
                    st.metric(
                        label="📦 Items Sold",
                        value=stats.get('total_items_sold', 0)
                    )
                
                st.markdown("---")
                
                # Top Customers
                if 'top_customers' in stats and stats['top_customers']:
                    st.subheader("🏆 Top Customers")
                    
                    top_customers_df = pd.DataFrame(stats['top_customers'])
                    
                    # Create bar chart
                    fig = px.bar(
                        top_customers_df,
                        x='name',
                        y='total_spent',
                        title='Customer Spending',
                        labels={'name': 'Customer', 'total_spent': 'Total Spent (₹)'},
                        color='total_spent',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display table
                    st.dataframe(
                        top_customers_df.style.format({'total_spent': '₹{:,.2f}'}),
                        use_container_width=True
                    )
                
                # Recent Invoices
                st.markdown("---")
                st.subheader("📋 Recent Invoices")
                
                invoices_response = requests.get(f"{API_URL}/api/invoices")
                if invoices_response.status_code == 200:
                    invoices_data = invoices_response.json()
                    if invoices_data['success'] and invoices_data['invoices']:
                        recent = invoices_data['invoices'][:5]
                        
                        for inv in recent:
                            with st.expander(f"🧾 {inv['invoice_number']} - {inv['customer']['name']} - ₹{inv['totals']['grand_total']:,.2f}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Date:** {inv['date']}")
                                    st.write(f"**Customer:** {inv['customer']['name']}")
                                    st.write(f"**Phone:** {inv['customer']['phone']}")
                                with col2:
                                    st.write(f"**Items:** {inv['totals']['total_items']}")
                                    st.write(f"**GST:** ₹{inv['totals']['total_gst']:,.2f}")
                                    st.write(f"**Total:** ₹{inv['totals']['grand_total']:,.2f}")
            else:
                st.info("📊 No invoices yet. Create your first invoice!")
        else:
            st.error("Failed to fetch statistics")
            
    except Exception as e:
        st.error(f"Error: {e}")


# ====================
# PAGE 2: CREATE INVOICE
# ====================
elif page == "➕ Create Invoice":
    st.markdown('<h1 class="main-header">➕ Create New Invoice</h1>', unsafe_allow_html=True)
    
    with st.form("invoice_form"):
        st.subheader("👤 Customer Details")
        
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Customer Name*", placeholder="Rajesh Kumar")
            customer_phone = st.text_input("Phone Number*", placeholder="9876543210", max_chars=10)
        with col2:
            customer_email = st.text_input("Email", placeholder="rajesh@example.com")
            customer_address = st.text_area("Address", placeholder="Mumbai, Maharashtra", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            customer_gst = st.text_input("GST Number (Optional)", placeholder="27ABCDE1234F1Z5", max_chars=15)
        with col2:
            customer_state = st.text_input("State", value="Telangana")
        
        st.markdown("---")
        st.subheader("🛒 Invoice Items")
        
        # Number of items
        num_items = st.number_input("Number of Items", min_value=1, max_value=20, value=1)
        
        items = []
        for i in range(num_items):
            st.markdown(f"**Item {i+1}**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                item_name = st.text_input(f"Item Name*", key=f"name_{i}", placeholder="Laptop")
            with col2:
                item_price = st.number_input(f"Price (₹)*", key=f"price_{i}", min_value=0.0, value=1000.0, step=100.0)
            with col3:
                item_qty = st.number_input(f"Quantity*", key=f"qty_{i}", min_value=1, value=1)
            with col4:
                item_gst = st.selectbox(f"GST %*", key=f"gst_{i}", options=[0, 5, 12, 18, 28], index=3)
            
            item_desc = st.text_input(f"Description (Optional)", key=f"desc_{i}", placeholder="Product description")
            
            if item_name:
                items.append({
                    "name": item_name,
                    "description": item_desc,
                    "price": item_price,
                    "quantity": item_qty,
                    "gst_rate": item_gst
                })
            
            st.markdown("---")
        
        # Notes
        notes = st.text_area("Additional Notes", placeholder="Thank you for your business!")
        
        # Submit button
        submitted = st.form_submit_button("🚀 Create Invoice", use_container_width=True)
        
        if submitted:
            if not customer_name or not customer_phone:
                st.error("❌ Please fill in required customer details (Name and Phone)")
            elif len(items) == 0:
                st.error("❌ Please add at least one item")
            else:
                # Create invoice
                payload = {
                    "customer": {
                        "name": customer_name,
                        "phone": customer_phone,
                        "email": customer_email,
                        "address": customer_address,
                        "gst_number": customer_gst,
                        "state": customer_state
                    },
                    "items": items,
                    "notes": notes
                }
                
                with st.spinner("Creating invoice..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/api/invoice/create-with-pdf",
                            json=payload
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                            
                            # Display invoice details
                            invoice = result['invoice']
                            st.balloons()
                            
                            st.markdown("### 📋 Invoice Created!")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.info(f"**Invoice #:** {invoice['invoice_number']}")
                            with col2:
                                st.info(f"**Total:** ₹{invoice['totals']['grand_total']:,.2f}")
                            with col3:
                                st.info(f"**GST:** ₹{invoice['totals']['total_gst']:,.2f}")
                            
                            # Download PDF button
                            pdf_url = f"{API_URL}/api/invoice/{invoice['invoice_number']}/pdf"
                            st.markdown(f"[📥 Download PDF]({pdf_url})")
                        else:
                            st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")


# ====================
# PAGE 3: VIEW INVOICES
# ====================
elif page == "📋 View Invoices":
    st.markdown('<h1 class="main-header">📋 All Invoices</h1>', unsafe_allow_html=True)
    
    # Search box
    search_query = st.text_input("🔍 Search by Customer Name", placeholder="Type customer name...")
    
    try:
        # Get all invoices
        response = requests.get(f"{API_URL}/api/invoices")
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success'] and data['invoices']:
                invoices = data['invoices']
                
                # Filter by search query
                if search_query:
                    invoices = [
                        inv for inv in invoices 
                        if search_query.lower() in inv['customer']['name'].lower()
                    ]
                
                st.info(f"📊 Showing {len(invoices)} invoice(s)")
                
                # Display invoices
                for inv in invoices:
                    status_color = "🔴" if inv['payment_status'] == "Pending" else "🟡" if inv['payment_status'] == "Partial" else "🟢"
                    with st.expander(
                        f"🧾 {inv['invoice_number']} | {inv['customer']['name']} | ₹{inv['totals']['grand_total']:,.2f} | {status_color} {inv['payment_status']}"
                    ):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("### Customer Details")
                            st.write(f"**Name:** {inv['customer']['name']}")
                            st.write(f"**Phone:** {inv['customer']['phone']}")
                            if inv['customer']['email']:
                                st.write(f"**Email:** {inv['customer']['email']}")
                            if inv['customer']['gst_number']:
                                st.write(f"**GST:** {inv['customer']['gst_number']}")
                            
                            st.markdown("### Items")
                            items_df = pd.DataFrame(inv['items'])
                            st.dataframe(
                                items_df[['name', 'quantity', 'unit_price', 'gst_rate', 'total_amount']],
                                use_container_width=True
                            )
                        
                        with col2:
                            st.markdown("### Totals")
                            st.metric("Subtotal", f"₹{inv['totals']['subtotal']:,.2f}")
                            st.metric("CGST", f"₹{inv['totals']['total_cgst']:,.2f}")
                            st.metric("SGST", f"₹{inv['totals']['total_sgst']:,.2f}")
                            st.metric("Grand Total", f"₹{inv['totals']['grand_total']:,.2f}")
                            
                            # Download button
                            pdf_url = f"{API_URL}/api/invoice/{inv['invoice_number']}/pdf"
                            st.markdown(f"[📥 Download PDF]({pdf_url})")

                            st.markdown("---")
                            # Email invoice section
                            with st.expander("📧 Email This Invoice"):
                                with st.form(key=f"email_form_{inv['invoice_number']}"):
                                    recipient = st.text_input(
                                        "Recipient Email",
                                        value=inv['customer'].get('email', ''),
                                        key=f"email_to_{inv['invoice_number']}"
                                    )
                                    
                                    st.info("⚠️ Gmail requires App Password. Regular password won't work!")
                                    sender = st.text_input(
                                        "Your Gmail",
                                        placeholder="your@gmail.com",
                                        key=f"email_from_{inv['invoice_number']}"
                                    )
                                    sender_pass = st.text_input(
                                        "Gmail App Password",
                                        type="password",
                                        help="Not your Gmail password! Create App Password in Google Account settings.",
                                        key=f"email_pass_{inv['invoice_number']}"
                                    )
                                    
                                    send_email = st.form_submit_button("📧 Send Email")
                                    
                                    if send_email:
                                        if not recipient or not sender or not sender_pass:
                                            st.error("Please fill all fields")
                                        else:
                                            with st.spinner("Sending email..."):
                                                try:
                                                    response = requests.post(
                                                        f"{API_URL}/api/invoice/{inv['invoice_number']}/send-email",
                                                        params={
                                                            "recipient_email": recipient,
                                                            "sender_email": sender,
                                                            "sender_password": sender_pass
                                                        }
                                                    )
                                                    
                                                    if response.status_code == 200:
                                                        st.success(f"✅ Email sent to {recipient}!")
                                                    else:
                                                        st.error(f"❌ {response.json().get('detail', 'Failed to send')}")
                                                except Exception as e:
                                                    st.error(f"❌ Error: {e}")

                            # Payment Management Section
                            with st.expander("💰 Payment Management"):
                                try:
                                    # Get payment history
                                    pay_hist_resp = requests.get(f"{API_URL}/api/invoice/{inv['invoice_number']}/payments")
                                    if pay_hist_resp.status_code == 200:
                                        pay_data = pay_hist_resp.json()
                                        
                                        action_col1, action_col2, action_col3 = st.columns(3)
                                        action_col1.metric("Total Amount", f"₹{pay_data['total_amount']:,.2f}")
                                        action_col2.metric("Total Paid", f"₹{pay_data['total_paid']:,.2f}")
                                        action_col3.metric("Remaining", f"₹{pay_data['remaining']:,.2f}")
                                        
                                        st.markdown(f"**Payment Status:** `{pay_data['status']}`")
                                        
                                        # Record Payment Form
                                        st.markdown("---")
                                        st.subheader("➕ Record Payment")
                                        with st.form(key=f"payment_form_{inv['invoice_number']}"):
                                            pay_amt = st.number_input("Amount (₹)", min_value=1.0, max_value=pay_data['remaining'], value=float(pay_data['remaining']))
                                            pay_method = st.selectbox("Method", ["UPI", "Cash", "Bank Transfer", "Card", "Cheque"])
                                            pay_tid = st.text_input("Transaction ID / Ref", placeholder="Optional")
                                            pay_notes = st.text_input("Notes", placeholder="Optional")
                                            
                                            submit_pay = st.form_submit_button("💳 Record Payment")
                                            
                                            if submit_pay:
                                                with st.spinner("Recording payment..."):
                                                    payment_response = requests.post(
                                                        f"{API_URL}/api/invoice/{inv['invoice_number']}/payment",
                                                        params={
                                                            "amount": pay_amt,
                                                            "payment_method": pay_method,
                                                            "transaction_id": pay_tid,
                                                            "notes": pay_notes
                                                        }
                                                    )
                                                    if payment_response.status_code == 200:
                                                        st.success("✅ Payment recorded successfully!")
                                                        st.rerun()
                                                    else:
                                                        st.error(f"❌ Error: {payment_response.json().get('detail', 'Failed to record')}")
                                        
                                        # Payment History Table
                                        if pay_data['payments']:
                                            with st.expander("📜 Payment History"):
                                                hist_df = pd.DataFrame(pay_data['payments'])
                                                st.dataframe(hist_df[['date', 'amount', 'method', 'transaction_id']], use_container_width=True)
                                except Exception as e:
                                    st.error(f"Error loading payments: {e}")
            else:
                st.info("📋 No invoices found. Create your first invoice!")
        else:
            st.error("Failed to fetch invoices")
            
    except Exception as e:
        st.error(f"Error: {e}")

        

# ====================
# PAGE 4: EXPORT REPORTS  
# ====================
elif page == "📥 Export Reports":
    st.markdown('<h1 class="main-header">📥 Export Reports</h1>', unsafe_allow_html=True)
    
    st.info("💡 Download reports as Excel files for accounting and GST filing")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📋 All Invoices")
        st.write("Export complete invoice list")
        
        if st.button("📥 Download", key="export_invoices", use_container_width=True):
            with st.spinner("Generating..."):
                try:
                    response = requests.get(f"{API_URL}/api/export/invoices", stream=True)
                    if response.status_code == 200:
                        filename = f"invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        st.success(f"✅ Downloaded: {filename}")
                        with open(filename, 'rb') as f:
                            st.download_button("💾 Save File", f, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.error("Export failed")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        st.markdown("### 💰 GST Summary")
        st.write("Monthly GST report")
        selected_month = st.text_input("Month (YYYY-MM)", value=datetime.now().strftime("%Y-%m"), key="gst_month")
        
        if st.button("📥 Download", key="export_gst", use_container_width=True):
            with st.spinner("Generating..."):
                try:
                    response = requests.get(f"{API_URL}/api/export/gst-summary", params={"month": selected_month}, stream=True)
                    if response.status_code == 200:
                        filename = f"gst_summary_{selected_month.replace('-', '_')}.xlsx"
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        st.success("✅ GST summary generated!")
                        with open(filename, 'rb') as f:
                            st.download_button("💾 Save Report", f, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.error("Export failed")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col3:
        st.markdown("### 👥 Customer Report")
        st.write("Customer spending analysis")
        
        if st.button("📥 Download", key="export_customers", use_container_width=True):
            with st.spinner("Generating..."):
                try:
                    response = requests.get(f"{API_URL}/api/export/customer-report", stream=True)
                    if response.status_code == 200:
                        filename = f"customer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        st.success("✅ Customer report generated!")
                        with open(filename, 'rb') as f:
                            st.download_button("💾 Save Report", f, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.error("Export failed")
                except Exception as e:
                    st.error(f"Error: {e}")


# ====================
# PAGE 5: ANALYTICS
# ====================
elif page == "📈 Analytics":
    st.markdown('<h1 class="main-header">📈 Advanced Analytics</h1>', unsafe_allow_html=True)
    
    # Revenue Trends
    st.subheader("💰 Revenue Trends")
    period = st.selectbox("Period", ["daily", "weekly", "monthly"], index=2, key="trend_period")
    
    try:
        trends_response = requests.get(f"{API_URL}/api/analytics/revenue-trends", params={"period": period})
        
        if trends_response.status_code == 200:
            trends = trends_response.json()
            
            if trends['data']['dates']:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trends['data']['dates'],
                    y=trends['data']['revenue'],
                    mode='lines+markers',
                    name='Revenue',
                    line=dict(color='#2563eb', width=3),
                    fill='tozeroy'
                ))
                fig.add_trace(go.Scatter(
                    x=trends['data']['dates'],
                    y=trends['data']['gst'],
                    mode='lines+markers',
                    name='GST',
                    line=dict(color='#dc2626', width=2)
                ))
                fig.update_layout(title=f"Revenue & GST Trends ({period.capitalize()})", xaxis_title="Period", yaxis_title="Amount (₹)", hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data yet. Create invoices first!")
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Top Customers by CLV")
        try:
            clv_response = requests.get(f"{API_URL}/api/analytics/customer-clv")
            if clv_response.status_code == 200:
                clv_data = clv_response.json()
                if clv_data['customers']:
                    top_5 = clv_data['customers'][:5]
                    clv_df = pd.DataFrame(top_5)
                    fig = px.bar(clv_df, x='name', y='clv', title='Customer Lifetime Value', labels={'name': 'Customer', 'clv': 'CLV (₹)'}, color='clv', color_continuous_scale='Greens')
                    st.plotly_chart(fig, use_container_width=True)
                    display_df = clv_df[['name', 'total_spent', 'invoice_count', 'clv']].copy()
                    display_df.columns = ['Customer', 'Total Spent', 'Invoices', 'CLV']
                    st.dataframe(display_df.style.format({'Total Spent': '₹{:,.2f}', 'CLV': '₹{:,.2f}'}), use_container_width=True)
                else:
                    st.info("No data yet")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with col2:
        st.subheader("💸 GST Rate Breakdown")
        try:
            gst_response = requests.get(f"{API_URL}/api/analytics/gst-breakdown")
            if gst_response.status_code == 200:
                gst_data = gst_response.json()
                if gst_data['breakdown']:
                    gst_df = pd.DataFrame(gst_data['breakdown'])
                    fig = px.pie(gst_df, values='gst_collected', names='rate', title='GST by Rate', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                    display_gst = gst_df[['rate', 'revenue', 'gst_collected']].copy()
                    display_gst.columns = ['GST %', 'Revenue', 'GST Collected']
                    st.dataframe(display_gst.style.format({'Revenue': '₹{:,.2f}', 'GST Collected': '₹{:,.2f}'}), use_container_width=True)
                else:
                    st.info("No data yet")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    
    st.subheader("🏆 Top Products")
    try:
        products_response = requests.get(f"{API_URL}/api/analytics/top-products", params={"limit": 10})
        if products_response.status_code == 200:
            products_data = products_response.json()
            if products_data['products']:
                products_df = pd.DataFrame(products_data['products'])
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.bar(products_df.head(5), x='revenue', y='name', orientation='h', title='Top 5 by Revenue', labels={'name': 'Product', 'revenue': 'Revenue (₹)'}, color='revenue', color_continuous_scale='Blues')
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = px.bar(products_df.head(5), x='quantity_sold', y='name', orientation='h', title='Top 5 by Quantity', labels={'name': 'Product', 'quantity_sold': 'Units'}, color='quantity_sold', color_continuous_scale='Oranges')
                    st.plotly_chart(fig, use_container_width=True)
                
                display_df = products_df[['name', 'revenue', 'quantity_sold']].copy()
                display_df.columns = ['Product', 'Revenue', 'Quantity Sold']
                st.dataframe(display_df.style.format({'Revenue': '₹{:,.2f}'}), use_container_width=True)
            else:
                st.info("No data yet")
    except Exception as e:
        st.error(f"Error: {e}")


# ====================
# PAGE 6: ABOUT
# ====================
elif page == "ℹ️ About":
    st.markdown('<h1 class="main-header">ℹ️ About GST Invoice Agent</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ## 🚀 AI-Powered GST Invoice Automation
    
    Built by **Bunny Rangu** as part of a 30-day B.Tech project.
    
    ### ✨ Features
    - ✅ Automated GST calculation (CGST/SGST)
    - ✅ Professional PDF invoice generation
    - ✅ Customer management
    - ✅ Invoice history & search
    - ✅ Real-time statistics dashboard
    - ✅ REST API with auto-documentation
    - ✅ Database persistence
    
    ### 🛠️ Tech Stack
    - **Backend:** Python, FastAPI
    - **Database:** SQLAlchemy, SQLite
    - **Frontend:** Streamlit
    - **PDF:** xhtml2pdf
    - **API Docs:** Swagger/OpenAPI
    
    ### 📊 Progress
    **Day 7 of 30** - Frontend Complete! 🎉
    
    ### 🔗 Links
    - **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
    - **GitHub:** [https://github.com/BUNNY-RANGU/-ai-agent-taxxx](https://github.com/BUNNY-RANGU/-ai-agent-taxxx)
    
    ### 📬 Contact
    Building in public! Connect on LinkedIn.
    
    ---
    
    Made with ❤️ in Hyderabad, India
    """)
    
    st.balloons()


# # Payment Status Section
# elif page == "💳 Payment Status":
#     st.header("💳 Payment Status")
    
    # Input invoice number
    invoice_num = st.text_input("Enter Invoice Number", placeholder="INV-2025-XXXX")
    
    if invoice_num:
        try:
            # Get payment history
            payment_response = requests.get(f"{API_BASE_URL}/api/invoice/{invoice_num}/payments")
            
            if payment_response.status_code == 200:
                payment_data = payment_response.json()
                
                # Display payment summary
                st.subheader(f"Payment Details for {invoice_num}")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Amount", f"₹{payment_data['total_amount']:,.2f}")
                with col2:
                    st.metric("Total Paid", f"₹{payment_data['total_paid']:,.2f}")
                with col3:
                    st.metric("Remaining", f"₹{payment_data['remaining']:,.2f}")
                with col4:
                    status_color = "green" if payment_data['status'] == "Paid" else "orange"
                    st.metric("Status", payment_data['status'])
                
                st.divider()
                
                # Record Payment Form
                st.subheader("Record Payment")
                
                with st.form(key="payment_form"):
                    payment_amount = st.number_input("Payment Amount", min_value=0.0, step=100.0)
                    payment_method = st.selectbox("Payment Method", ["UPI", "Cash", "Card", "Bank Transfer", "Cheque"])
                    transaction_id = st.text_input("Transaction ID (Optional)")
                    payment_notes = st.text_area("Payment Notes (Optional)")
                    
                    submit_payment = st.form_submit_button("Record Payment")
                    
                    if submit_payment:
                        if payment_amount <= 0:
                            st.error("Please enter a valid payment amount")
                        else:
                            try:
                                payment_result = requests.post(
                                    f"{API_BASE_URL}/api/invoice/{invoice_num}/payment",
                                    params={
                                        "amount": payment_amount,
                                        "payment_method": payment_method,
                                        "transaction_id": transaction_id,
                                        "notes": payment_notes
                                    }
                                )
                                
                                if payment_result.status_code == 200:
                                    st.success(f"✅ Payment of ₹{payment_amount:,.2f} recorded successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error: {payment_result.json().get('detail', 'Failed')}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                
                st.divider()
                
                # Payment History
                st.subheader("Payment History")
                
                if payment_data['payments']:
                    for pay in payment_data['payments']:
                        with st.expander(f"Payment #{pay['id']} - ₹{pay['amount']:,.2f}"):
                            st.write(f"**Date:** {pay['date']} {pay['time']}")
                            st.write(f"**Method:** {pay['method']}")
                            if pay['transaction_id']:
                                st.write(f"**Transaction ID:** {pay['transaction_id']}")
                            if pay['notes']:
                                st.write(f"**Notes:** {pay['notes']}")
                else:
                    st.info("No payments recorded yet")
                    
            else:
                st.error(f"Invoice {invoice_num} not found")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("Enter an invoice number above to view payment status")


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>GST Invoice Agent v1.0 | Built by Bunny Rangu | Day 7/30 Complete ✅</p>
    </div>
    """,
    unsafe_allow_html=True
)