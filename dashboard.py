# Import necessary libraries
import streamlit as st
import pymongo
import pandas as pd
import plotly.graph_objects as go
import time

# Page configuration with dark theme
st.set_page_config(
    page_title="Tweet Engagements Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add modern CSS styling
st.markdown("""
<style>
    /* Modern color palette and base styles */
    :root {
        --primary: #6C5CE7;
        --secondary: #A594F9;
        --accent: #3498db;
        --background: #111827;
        --card-bg: #1F2937;
        --success: #10B981;
        --warning: #F59E0B;
        --text: #F3F4F6;
    }

    .main {
        background-color: var(--background);
        color: var(--text);
    }

    /* Modern card styling */
    .metric-container {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.2s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
    }

    .metric-title {
        color: #94A3B8;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.025em;
        margin-bottom: 0.5rem;
    }

    .big-number {
        color: var(--text);
        font-size: 2.25rem;
        font-weight: 700;
        line-height: 1;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Modern button styling */
    .stButton>button {
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }

    /* Chart container styling */
    .chart-container {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .chart-title {
        color: #94A3B8;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        letter-spacing: 0.025em;
    }

    /* Header styling */
    h1 {
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.025em;
        text-align: center;
        margin: 2rem 0;
    }

    /* Streamlit elements override */
    .stPlotlyChart {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Get MongoDB connection details from Streamlit secrets
# This is different from using dotenv in local development
try:
    # MongoDB connection details - from Streamlit secrets
    MONGODB_URI = st.secrets["MONGODB_URI"]
    MONGODB_DATABASE = st.secrets["MONGODB_DATABASE"]
except Exception as e:
    st.error(f"Error accessing secrets: {e}")
    st.warning("Make sure you've configured secrets in Streamlit Cloud")
    # Provide fallbacks to allow the app to load even with errors
    MONGODB_URI = None
    MONGODB_DATABASE = None

# Function to connect to MongoDB and get engagement data
def get_engagement_data():
    if not MONGODB_URI or not MONGODB_DATABASE:
        return 0, pd.DataFrame()  # Return empty data if credentials not available
        
    try:
        # Connect to MongoDB with timeout settings
        client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Verify connection
        client.admin.command('ping')  # Will raise error if connection fails
        
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
        
    except Exception as e:
        st.error(f"MongoDB Connection Error: {str(e)}")
        return 0, pd.DataFrame()  # Return empty data on error

# Title
st.markdown("<h1 style='text-align: center;'>Tweet Engagements Dashboard</h1>", unsafe_allow_html=True)

# Add auto-refresh button
if st.button("Refresh Data"):
    st.rerun()

# Display last updated time
st.write(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Show connection status
if not MONGODB_URI or not MONGODB_DATABASE:
    st.warning("MongoDB credentials not configured. Please set up secrets in Streamlit Cloud.")

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
    # Update chart configurations
    def create_modern_chart_layout(title="", height=300):
        return dict(
            template="plotly_dark",
            height=height,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F3F4F6'),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                gridwidth=0.5,
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                gridwidth=0.5,
                zeroline=False
            )
        )

    # Update time series chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_data['date'],
        y=time_data['engagements'],
        mode='lines+markers',
        name='Engagements',
        line=dict(
            color='#6C5CE7',
            width=4,
            shape='spline',
            smoothing=1.3
        ),
        marker=dict(
            size=8,
            color='#A594F9',
            symbol='circle',
            line=dict(
                color='#6C5CE7',
                width=2
            )
        ),
        fill='tozeroy',
        fillcolor='rgba(108,92,231,0.1)'
    ))

    fig.update_layout(
        **create_modern_chart_layout("Daily Engagements", 400)
    )

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No time series data available to display chart.")

# Update bar charts
def create_modern_bar_chart(data, title):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data['Metric'],
        y=data['Count'],
        marker_color=['#6C5CE7', '#A594F9', '#3498db'],
        marker_line_color='rgba(255,255,255,0.2)',
        marker_line_width=1,
        opacity=0.9
    ))
    
    fig.update_layout(
        **create_modern_chart_layout(title),
        bargap=0.4
    )
    return fig
