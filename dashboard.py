# Import necessary libraries
import streamlit as st
import pymongo
import os
from dotenv import load_dotenv
import time

# Page configuration with dark theme
st.set_page_config(
    page_title="Tweet Engagements Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #1E1E1E;
        color: white;
    }
    .stButton>button {
        background-color: #990000;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    h1, h2, h3 {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Get MongoDB connection details from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Function to connect to MongoDB and get total engagement count
def get_total_engagements():
    # Connect to MongoDB
    client = pymongo.MongoClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    
    # Use the correct collection name from your screenshots
    collection = db["twitter_actions"]
    
    # Count total engagements (likes)
    total_count = collection.count_documents({"action": "like"})
    
    # Close connection
    client.close()
    
    return total_count

# Title
st.markdown("<h1 style='text-align: center;'>Tweet Engagements Dashboard</h1>", unsafe_allow_html=True)

# Add auto-refresh button
if st.button("Refresh Data"):
    st.rerun()

# Display last updated time
st.write(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Get data
total_engagements = get_total_engagements()

# Display total engagements in a large format
st.markdown(
    f"""
    <div style='text-align: center; background-color: #2C2C2C; padding: 40px; border-radius: 10px; margin-top: 50px;'>
        <h2 style='color: #3498db;'>Total Tweets Engaged</h2>
        <h1 style='color: #3498db; font-size: 100px;'>{total_engagements}</h1>
    </div>
    """, 
    unsafe_allow_html=True
)