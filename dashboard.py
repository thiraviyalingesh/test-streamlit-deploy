# Import necessary libraries
import streamlit as st
import pymongo
import os
from dotenv import load_dotenv
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration with dark theme
st.set_page_config(
    page_title="Tweet Engagements Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.experimental_memo.clear()

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

# Function to connect to MongoDB and get engagement data
def get_engagement_data():
    # Connect to MongoDB
    client = pymongo.MongoClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    
    # Use the correct collection name
    collection = db["twitter_actions"]
    
    # Count total engagements (likes)
    total_count = collection.count_documents({"action": "like"})
    
    # Get time series data for chart
    pipeline = [
        {
            "$match": {
                "action": "like"
            }
        },
        {
            "$group": {
                "_id": "$date_only",  # Group by date_only field
                "count": {"$sum": 1}  # Count engagements per day
            }
        },
        {
            "$sort": {"_id": 1}  # Sort by date
        }
    ]
    
    result = list(collection.aggregate(pipeline))
    
    # Close connection
    client.close()
    
    # Create DataFrame for time series
    time_df = pd.DataFrame(result)
    if not time_df.empty:
        time_df = time_df.rename(columns={"_id": "date", "count": "engagements"})
        # Convert date strings to datetime objects for better plotting
        time_df["date"] = pd.to_datetime(time_df["date"])
    
    return total_count, time_df

# Title
st.markdown("<h1 style='text-align: center;'>Tweet Engagements Dashboard</h1>", unsafe_allow_html=True)

# Add auto-refresh button
if st.button("Refresh Data"):
    st.rerun()

# Display last updated time
st.write(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Get data
total_engagements, time_data = get_engagement_data()

# Display total engagements in a large format
st.markdown(
    f"""
    <div style='text-align: center; background-color: #2C2C2C; padding: 40px; border-radius: 10px; margin-top: 20px; margin-bottom: 20px;'>
        <h2 style='color: #3498db;'>Total Tweets Engaged</h2>
        <h1 style='color: #3498db; font-size: 100px;'>{total_engagements}</h1>
    </div>
    """, 
    unsafe_allow_html=True
)

# Create and display time series chart
if not time_data.empty:
    # Create Plotly time series chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_data['date'],
        y=time_data['engagements'],
        mode='lines+markers',
        name='Engagements',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8)
    ))
    
    # Add area under the line
    fig.add_trace(go.Scatter(
        x=time_data['date'],
        y=time_data['engagements'],
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)',
        line=dict(width=0),
        showlegend=False
    ))
    
    # Customize layout
    fig.update_layout(
        title="Engagements Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Engagements",
        template="plotly_dark",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No time series data available to display chart.")