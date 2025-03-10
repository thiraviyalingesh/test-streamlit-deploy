# Import necessary libraries
import streamlit as st
import pymongo
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rerun_chart_debugger.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get MongoDB connection details from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Apply custom styling
st.set_page_config(
    page_title="Rerun Comparison Chart",
    page_icon="📊",
    layout="wide"
)

# Hide the theme switcher and footer
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton, div[data-testid="stToolbar"] {display: none !important;}
        
        /* Main background and text colors */
        .main {
            background-color: #FFFFFF;
            color: black;
        }
        
        /* Chart container */
        .chart-container {
            background-color: #F0F0F0;
            padding: 25px;
            border-radius: 15px;
            margin-top: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            border-left: 5px solid #3498db;
        }
        
        /* Chart title */
        .chart-title {
            color: #3498db;
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

def get_rerun_comparison_data():
    """
    Fetches data for comparing Initial Run vs Rerun metrics.
    Initial Run: Count where 'result' contains 'success'
    Rerun: Count ALL successful actions (either in 'result' or 'rerun')
    """
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]

        # Initial run pipeline (only count 'result' successes)
        initial_pipeline = [
            {
                "$match": {
                    "result": {"$regex": "success", "$options": "i"}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$regexMatch": {"input": "$action", "regex": "like", "options": "i"}},
                            "likes",
                            {
                                "$cond": [
                                    {"$regexMatch": {"input": "$action", "regex": "repost|retweet", "options": "i"}},
                                    "retweets",
                                    "comments"
                                ]
                            }
                        ]
                    },
                    "count": {"$sum": 1}
                }
            }
        ]

        # Rerun pipeline (count both 'result' and 'rerun' successes)
        rerun_pipeline = [
            {
                "$match": {
                    "$or": [
                        {"result": {"$regex": "success", "$options": "i"}},
                        {"rerun": {"$regex": "success", "$options": "i"}}
                    ]
                }
            },
            {
                "$group": {
                    "_id": {
                        "$cond": [
                            {"$regexMatch": {"input": "$action", "regex": "like", "options": "i"}},
                            "likes",
                            {
                                "$cond": [
                                    {"$regexMatch": {"input": "$action", "regex": "repost|retweet", "options": "i"}},
                                    "retweets",
                                    "comments"
                                ]
                            }
                        ]
                    },
                    "count": {"$sum": 1}
                }
            }
        ]

        initial_results = {doc["_id"]: doc["count"] for doc in collection.aggregate(initial_pipeline)}
        rerun_results = {doc["_id"]: doc["count"] for doc in collection.aggregate(rerun_pipeline)}

        return {
            "initial": {
                "likes": initial_results.get("likes", 0),
                "retweets": initial_results.get("retweets", 0),
                "comments": initial_results.get("comments", 0)
            },
            "rerun": {
                "likes": rerun_results.get("likes", 0),
                "retweets": rerun_results.get("retweets", 0),
                "comments": rerun_results.get("comments", 0)
            }
        }

    except Exception as e:
        logger.error(f"Error fetching rerun comparison data: {str(e)}")
        return None
    finally:
        client.close()

def create_grouped_bar_chart(metrics):
    """
    Creates a grouped bar chart comparing initial run vs rerun metrics.
    Using a simplified configuration to avoid Plotly errors.
    
    Args:
        metrics (dict): Dictionary containing metrics for both initial run and rerun
        
    Returns:
        plotly.graph_objects.Figure: The grouped bar chart figure
    """
    # Define data
    categories = ['Initial Run', 'Rerun']
    
    # Extract data for each series
    likes_values = [metrics['initial']['likes'], metrics['rerun']['likes']]
    retweets_values = [metrics['initial']['retweets'], metrics['rerun']['retweets']]
    comments_values = [metrics['initial']['comments'], metrics['rerun']['comments']]
    
    # Create a simple figure
    fig = go.Figure()
    
    # Add bars for each metric
    fig.add_trace(go.Bar(
        x=categories,
        y=likes_values,
        name='Likes',
        marker_color='#ff3333'  # Red color to match image
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=retweets_values,
        name='Retweets',
        marker_color='#3498db'  # Blue color to match image
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=comments_values,
        name='Comments',
        marker_color='#74c69d'  # Green color to match image
    ))
    
    # Basic layout
    fig.update_layout(
        title="We have a Rerun Facility to increase our Success rate",
        barmode='group',
        height=600
    )
    
    return fig

def main():
    """Main function to create and display the rerun comparison chart."""
    st.markdown("<h1 style='text-align: center;'>Rerun Comparison Analysis</h1>", unsafe_allow_html=True)
    
    metrics = get_rerun_comparison_data()
    
    if metrics is None:
        st.error("Failed to fetch data. Please check the database connection.")
        return
        
    # Create chart container
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Initial Run vs Rerun Performance</div>', unsafe_allow_html=True)
    
    # Create and display the chart
    fig = create_grouped_bar_chart(metrics)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add analysis
    st.subheader("Analysis")
    
    # Calculate improvement percentages
    likes_improvement = ((metrics["rerun"]["likes"] - metrics["initial"]["likes"]) / metrics["initial"]["likes"] * 100) if metrics["initial"]["likes"] > 0 else 0
    retweets_improvement = ((metrics["rerun"]["retweets"] - metrics["initial"]["retweets"]) / metrics["initial"]["retweets"] * 100) if metrics["initial"]["retweets"] > 0 else 0
    comments_improvement = ((metrics["rerun"]["comments"] - metrics["initial"]["comments"]) / metrics["initial"]["comments"] * 100) if metrics["initial"]["comments"] > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Likes Improvement", 
            value=f"{metrics['rerun']['likes'] - metrics['initial']['likes']}",
            delta=f"{likes_improvement:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Retweets Improvement", 
            value=f"{metrics['rerun']['retweets'] - metrics['initial']['retweets']}",
            delta=f"{retweets_improvement:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Comments Improvement", 
            value=f"{metrics['rerun']['comments'] - metrics['initial']['comments']}",
            delta=f"{comments_improvement:.1f}%"
        )
    
    # Add timestamp for last update
    st.markdown(f"<div style='text-align: right; color: gray; font-size: 0.8em;'>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
