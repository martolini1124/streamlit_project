import streamlit as st
import pandas as pd
import time
import requests
import json

# --- CONFIGURATION ---
# IBM Cloud API Key (to be updated to use env variables in production)
API_KEY = 'rb8KNVLDwDgeji47IgvqpC518efFkfFCCpFj4o80lyFK'

# URLs
IAM_TOKEN_URL = 'https://iam.cloud.ibm.com/identity/token'
GRANITE_API_URL = 'https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29'

# --- HELPER FUNCTIONS ---


@st.cache_data(ttl=3500)
def get_iam_token(api_key):
    """Generate IAM Access Token using API Key (cached for 3500 seconds)."""
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey': api_key
    }
    try:
        response = requests.post(
            IAM_TOKEN_URL, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        access_token = response.json()['access_token']
        return access_token
    except Exception as e:
        st.error(f"❌ Failed to get IAM token: {str(e)}")
        return None


def trigger_granite_api(access_token, user_prompt):
    """Use the IAM token to call the Granite API."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    body = {
        "input": user_prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "min_new_tokens": 0,
            "repetition_penalty": 1
        },
        "model_id": "ibm/granite-3-8b-instruct",
        "project_id": "b280bfb6-acee-4cdd-906b-f4e3552ec9b5",
        "moderations": {
            "hap": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                }
            },
            "pii": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {
                        "remove_entity_value": True
                    }
                }
            }
        }
    }

    try:
        response = requests.post(
            GRANITE_API_URL, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Failed to trigger Granite API: {str(e)}")
        return None


# --- PAGE FUNCTIONS ---
def show_dashboard():
    st.title("AI Logistics Agent Dashboard")
    st.write("Welcome to the AI-powered logistics tracking system.")

    # Sample metrics for overview
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


def show_shipment_tracking():
    st.title("Shipment Tracking")
    tracking_number = st.text_input("Enter Tracking Number:")
    if st.button("Track"):
        with st.spinner("Fetching shipment details..."):
            time.sleep(2)  # Simulate API call delay
            st.success(
                f"Shipment {tracking_number} is currently **In Transit**.")

    # Example map display (replace with real tracking data)
    st.map(pd.DataFrame({"lat": [37.7749], "lon": [-122.4194]}))


def show_ai_chatbot():
    st.title("💬 IBM Granite Chat Assistant")
    st.write("🚀 Interact with IBM Granite LLM in a chat interface")

    # Initialize chat history if not already present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar: System prompt and chat clear button
    with st.sidebar:
        system_prompt = st.text_area(
            "System Prompt (AI Assistant's Role)",
            value=(
                "You are a highly efficient and knowledgeable logistical delivery support agent. "
                "Your role is to assist users with tracking shipments, scheduling deliveries, "
                "optimizing routes, and answering any logistical inquiries. Your responses should be "
                "clear, concise, and highly informative."
            ),
            height=150
        )
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.experimental_rerun()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            with st.spinner("Processing request..."):
                iam_token = get_iam_token(API_KEY)
                if not iam_token:
                    st.error(
                        "Failed to generate IAM token. Please try again later.")
                    return

                # Combine system context with user prompt
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
                result = trigger_granite_api(iam_token, full_prompt)
                if not result:
                    st.error(
                        "Failed to get response from Granite API. Please try again.")
                    return

            # Display assistant's response
            with st.chat_message("assistant"):
                try:
                    response_text = result['results'][0]['generated_text']
                    st.write(response_text)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response_text})
                except (KeyError, IndexError):
                    st.error("Error parsing API response")
                    st.json(result)  # Output raw response for debugging

        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

    # Sidebar: Display API status
    with st.sidebar:
        st.divider()
        st.caption("API Status")
        if st.session_state.messages:
            st.success("✅ System Online")
        else:
            st.info("💭 Waiting for first message")


def show_analytics():
    st.title("Logistics Analytics")
    st.write("View shipment performance and efficiency metrics.")

    # Placeholder analytics data
    df = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
        "Deliveries": [200, 220, 250, 280, 300]
    })
    st.line_chart(df.set_index("Month"))


# --- MAIN APP SETUP ---
st.set_page_config(page_title="AI Logistics Agent", layout="wide")

# Sidebar navigation
menu = st.sidebar.radio(
    "Navigation", ["Dashboard", "Shipment Tracking", "AI Chatbot", "Analytics"]
)

if menu == "Dashboard":
    show_dashboard()
elif menu == "Shipment Tracking":
    show_shipment_tracking()
elif menu == "AI Chatbot":
    show_ai_chatbot()
elif menu == "Analytics":
    show_analytics()
