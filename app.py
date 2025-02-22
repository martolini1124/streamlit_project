import streamlit as st
import pandas as pd
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Logistics Agent", layout="wide")

# --- SIDEBAR NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Dashboard", "Shipment Tracking", "AI Chatbot", "Analytics"])

# --- DASHBOARD ---
if menu == "Dashboard":
    st.title("AI Logistics Agent Dashboard")
    st.write("Welcome to the AI-powered logistics tracking system.")
    
    # Sample data for overview
    metrics = {
        "Total Shipments": 500,
        "In Transit": 120,
        "Delivered": 350,
        "Pending": 30
    }
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Shipments", metrics["Total Shipments"])
    col2.metric("In Transit", metrics["In Transit"])
    col3.metric("Delivered", metrics["Delivered"])
    col4.metric("Pending", metrics["Pending"])

# --- SHIPMENT TRACKING ---
elif menu == "Shipment Tracking":
    st.title("Shipment Tracking")
    tracking_number = st.text_input("Enter Tracking Number:")
    if st.button("Track"):
        with st.spinner("Fetching shipment details..."):
            time.sleep(2)  # Simulate API call
            st.success(f"Shipment {tracking_number} is currently **In Transit**.")
    
    # Sample map (Replace with real tracking data)
    st.map(pd.DataFrame({"lat": [37.7749], "lon": [-122.4194]}))  # San Francisco Example

# --- AI CHATBOT ---
elif menu == "AI Chatbot":
    st.title("AI Chatbot")
    user_query = st.text_input("Ask about your shipment:")
    if st.button("Ask AI"):
        with st.spinner("Thinking..."):
            time.sleep(2)  # Simulate AI response time
            st.success("Your package will arrive in 2 days.")

# --- ANALYTICS ---
elif menu == "Analytics":
    st.title("Logistics Analytics")
    st.write("View shipment performance and efficiency metrics.")
    
    # Placeholder for analytics data
    df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
        "Deliveries": [200, 220, 250, 280, 300]
    })
    st.line_chart(df.set_index("Month"))

