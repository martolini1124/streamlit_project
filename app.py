import streamlit as st
import pandas as pd
import time
import requests

# --- CONFIGURATION ---
# IBM Cloud API Key (update with env variables in production)
API_KEY = 'rb8KNVLDwDgeji47IgvqpC518efFkfFCCpFj4o80lyFK'

# URLs
IAM_TOKEN_URL = 'https://iam.cloud.ibm.com/identity/token'
GRANITE_API_URL = 'https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29'

# --- INITIAL STATE ---
# Initialize chat history in session_state so it persists across pages
if "messages" not in st.session_state:
    st.session_state.messages = []

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
            "stop_sequences": [
                "<<END>>",
                "[STOP]",
                "###",
                "\\n\\n",
                "[END]"
            ],
            "repetition_penalty": 1
        },
        "model_id": "ibm/granite-3-8b-instruct",
        "project_id": "b280bfb6-acee-4cdd-906b-f4e3552ec9b5",
        "moderations": {
            "hap": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True}
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True}
                }
            },
            "pii": {
                "input": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True}
                },
                "output": {
                    "enabled": True,
                    "threshold": 0.5,
                    "mask": {"remove_entity_value": True}
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


def clean_response_text(text):
    """Remove stopping sequences and clean up the response text."""
    stop_sequences = ["[END]", "<<END>>", "[STOP]", "###"]
    cleaned_text = text
    for seq in stop_sequences:
        cleaned_text = cleaned_text.replace(seq, "").strip()
    return cleaned_text


def process_message(prompt, system_prompt):
    """Handle message processing and API calls."""
    if not prompt:
        return

    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get AI response
    with st.spinner("Processing request..."):
        iam_token = get_iam_token(API_KEY)
        if not iam_token:
            st.error("Failed to generate IAM token. Please try again later.")
            return

        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        result = trigger_granite_api(iam_token, full_prompt)

        if not result:
            st.error("Failed to get response from Granite API. Please try again.")
            return

        try:
            response_text = result['results'][0]['generated_text']
            # Clean the response text before adding to messages
            cleaned_response = clean_response_text(response_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": cleaned_response})
        except (KeyError, IndexError):
            st.error("Error parsing API response. Please see details in the logs.")
            st.json(result)

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

    # Sidebar: System prompt and clear chat button
    with st.sidebar:
        system_prompt = st.text_area(
            "System Prompt (AI Assistant's Role)",
            value=("""📦 System Prompt for a Logistical Agent (Dispatcher Support)
1. Identity & Role:
You are LogiBot, a logistical support agent designed to assist dispatchers in managing deliveries. Your primary role is to provide quick, accurate, and context-aware answers regarding delivery operations.

2. Goals:

Help dispatchers with real-time delivery status.
Provide ETAs based on location and traffic conditions (if data is available).
Suggest optimal routes for deliveries.
Handle common logistical issues (e.g., delays, reroutes, lost packages).
Support driver and customer communication guidelines.
3. Communication Style:

Be concise, professional, and action-oriented.
Prioritize clarity over technical jargon.
Use bullet points or numbered lists when explaining multi-step solutions.
4. Information You Can Access:

Delivery schedules
Current driver locations
Package tracking data
Routing maps and traffic data (if integrated)
Customer delivery details
5. Handling Incomplete Data:
If certain data is unavailable (e.g., real-time GPS location), suggest alternative actions like contacting the driver or checking with the warehouse.

6. Common Use Cases:

Order Status: "Where is order #12345?"
ETA Requests: "When will Driver John arrive at Customer X?"
Routing Help: "What’s the fastest route to 456 Main St. considering traffic?"
Issue Handling: "The customer wasn’t home, what should the driver do?"
Driver Support: "Can you notify Driver Sarah about the schedule change?"
7. Constraints:

Always prioritize delivery timelines and customer satisfaction.
Never share sensitive customer data without authorization.
Avoid giving speculative answers; always state when data is unavailable.
8. Tone in Special Situations:

Delays or Issues: Empathetic yet solution-oriented.
Critical Delivery Failures: Urgent and clear, offering next steps.
Routine Queries: Quick and efficient.

Stopping Sequence Instruction:
Always conclude your response with the stopping token [END] to signal completion.                   
                   """),
            height=300
        )
        if st.button("Clear Chat History"):
            st.session_state.messages = []

    # Add preset prompt buttons with better spacing and styling
    st.subheader("Common Questions:", divider='gray')

    # Use st.columns with adjusted ratios for tighter spacing
    # Equal ratios for centered columns
    col1, col2, col3 = st.columns([1, 1, 1])

    # Use st.expander for a cleaner look
    with st.expander("Click to see common questions"):
        # Simplified button handling with more descriptive labels
        preset_prompts = {
            "Where is delivery #7890?": col1.button("Track Delivery #7890 🚚", use_container_width=True),
            "The delivery is delayed": col2.button("Report Delay ⚠️", use_container_width=True),
            "Customer wasn't home, what to do?": col3.button("Customer Not Home 🏠", use_container_width=True)
        }

    # Handle preset prompts
    for prompt_text, clicked in preset_prompts.items():
        if clicked:
            process_message(prompt_text, system_prompt)

    # Handle chat input
    if prompt := st.chat_input("What would you like to know?"):
        process_message(prompt, system_prompt)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Sidebar: API status display
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
    "Navigation", ["AI Chatbot", "Dashboard", "Shipment Tracking", "Analytics"]
)

if menu == "AI Chatbot":
    show_ai_chatbot()
elif menu == "Dashboard":
    show_dashboard()
elif menu == "Shipment Tracking":
    show_shipment_tracking()
elif menu == "Analytics":
    show_analytics()
