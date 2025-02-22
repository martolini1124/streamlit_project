# LogiBot

LogiBot is an AI-powered logistics management system built with Streamlit and IBM's Granite LLM API. This application helps dispatchers and logistics managers handle delivery operations more efficiently through an interactive chat interface and dashboard.

## Features

### 1. AI Chatbot (LogiBot)
- Interactive chat interface powered by IBM Granite 3-8b-instruct model
- Specialized in logistics and dispatch operations
- Pre-set common queries for quick access
- Real-time response processing

### 2. Dashboard
- Overview of key logistics metrics
- Real-time tracking statistics
- Performance indicators for:
  - Total Shipments
  - In-Transit Items
  - Delivered Items
  - Pending Deliveries

### 3. Shipment Tracking
- Individual shipment tracking
- Interactive map visualization
- Real-time status updates
- Tracking number lookup system

### 4. Analytics
- Delivery performance metrics
- Monthly delivery trends
- Interactive charts and visualizations

## Technical Details

- **Frontend**: Streamlit
- **AI Model**: IBM Granite 3-8b-instruct
- **APIs**:
  - IBM Cloud IAM Authentication
  - Granite API for text generation
  - Geolocation services for tracking

## Setup Requirements

1. IBM Cloud API Key
2. Python 3.7+
3. Required Python packages:
   ```
   streamlit
   pandas
   requests
   ```

## Environment Variables

For production deployment, configure the following:
- `API_KEY`: IBM Cloud API Key

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

