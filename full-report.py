# Import necessary libraries
import streamlit as st
import pymongo
import os
from dotenv import load_dotenv
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debugger.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration with dark theme
st.set_page_config(
    page_title="Tweet Engagements Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Dark theme styling with smaller KPI cards and cream browser background
st.markdown("""
<style>
    .main, .main .block-container, body, [data-testid="stAppViewContainer"] {
        background-color: #f5f3e8 !important;
    }
    
    /* Fix for stApp wrapper */
    .stApp {
        background-color: #f5f3e8 !important;
    }
    
    /* Dark themed containers on cream background */
    .metric-container {
        text-align: center; 
        background-color: #1e1e1e; 
        padding: 12px; 
        border-radius: 8px; 
        margin: 6px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border-left: 3px solid #3498db;
        height: auto;
        color: #f0f0f0;
    }
    
    /* Success metrics container */
    .success-metric-container {
        text-align: center; 
        background-color: #1e1e1e; 
        padding: 12px; 
        border-radius: 8px; 
        margin: 6px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        border-left: 3px solid #27ae60;
        height: auto;
        color: #f0f0f0;
    }
    
    /* Metric title */
    .metric-title {
        color: #3498db;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 6px;
    }
    
    /* Success metric title */
    .success-metric-title {
        color: #27ae60;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 6px;
    }
    
    /* Small big number display */
    .big-number {
        color: #3498db; 
        font-size: 32px;
        font-weight: 700;
        margin: 4px 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    
    /* Success big number display */
    .success-big-number {
        color: #27ae60; 
        font-size: 32px;
        font-weight: 700;
        margin: 4px 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    
    /* Chart container */
    .chart-container {
        padding: 15px;
        border-radius: 8px;
        background-color: #1e1e1e;
        margin: 12px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        color: #f0f0f0;
    }
    
    /* Chart borders */
    .engagement-chart {
        border-left: 3px solid #1DA1F2;
    }
    
    .success-chart {
        border-left: 3px solid #27ae60;
    }
    
    /* Chart title */
    .chart-title {
        color: #e0e0e0;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    
    /* Section headers */
    h1, h2, h3, h4 {
        font-weight: 600;
        color: #333333; /* Dark text on cream background */
        margin: 15px 0 10px 0;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1DA1F2;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 15px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #0c80cf;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    /* Last updated text */
    .last-updated {
        color: #555;
        font-size: 12px;
        font-style: italic;
        margin-left: 15px;
    }
    .refresh-button {
    background: linear-gradient(45deg, #2193b0, #6dd5ed);
    color: white;
    border: none;
    border-radius: 30px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    display: inline-block;
    text-align: center;
    text-decoration: none;
    position: relative;
    overflow: hidden;
    z-index: 10;
    }

    .refresh-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 20px rgba(0,0,0,0.3);
    }

    .refresh-button::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, #6dd5ed, #2193b0);
        opacity: 0;
        z-index: -1;
        transition: opacity 0.3s ease;
    }

    .refresh-button:hover::after {
        opacity: 1;
    }

    /* Animated text styles */
    .text7 {
    color: white;
    font-weight: bold;
    font-size: 26px;
    box-sizing: content-box;
    -webkit-box-sizing: content-box;
    height: 40px;
    display: flex;
    margin-top: 10px;
    justify-content: center;
    }
    .text7 .words {
    overflow: hidden;
    position: relative;
    top: 50%;
    }
    .text7 span {
    display: block;
    padding-left: 6px;
    padding-top: 5px;
    color: #956afa;
    animation: text7-animation 4s infinite;
    }
    @keyframes text7-animation {
    10% {
        -webkit-transform: translateY(-102%);
        transform: translateY(-102%);
    }
    25% {
        -webkit-transform: translateY(-100%);
        transform: translateY(-100%);
    }
    35% {
        -webkit-transform: translateY(-202%);
        transform: translateY(-202%);
    }
    50% {
        -webkit-transform: translateY(-200%);
        transform: translateY(-200%);
    }
    60% {
        -webkit-transform: translateY(-302%);
        transform: translateY(-302%);
    }
    75% {
        -webkit-transform: translateY(-300%);
        transform: translateY(-300%);
    }
    85% {
        -webkit-transform: translateY(-402%);
        transform: translateY(-402%);
    }
    100% {
        -webkit-transform: translateY(-400%);
        transform: translateY(-400%);
    }
    }
    
    .text7 {
  color: black;
  font-weight: bold;
  font-size: 26px;
  box-sizing: content-box;
  -webkit-box-sizing: content-box;
  height: 40px;
  display: flex;
}
.text7 .words {
  overflow: hidden;
  position: relative;
  top: 50%;
}
.text7 span {
  display: block;
  padding-left: 6px;
  padding-top: 5px;
  color: #956afa;
  animation: text7-animation 4s infinite;
}
@keyframes text7-animation {
  10% {
    -webkit-transform: translateY(-102%);
    transform: translateY(-102%);
  }
  25% {
    -webkit-transform: translateY(-100%);
    transform: translateY(-100%);
  }
  35% {
    -webkit-transform: translateY(-202%);
    transform: translateY(-202%);
  }
  50% {
    -webkit-transform: translateY(-200%);
    transform: translateY(-200%);
  }
  60% {
    -webkit-transform: translateY(-302%);
    transform: translateY(-302%);
  }
  75% {
    -webkit-transform: translateY(-300%);
    transform: translateY(-300%);
  }
  85% {
    -webkit-transform: translateY(-402%);
    transform: translateY(-402%);
  }
  100% {
    -webkit-transform: translateY(-400%);
    transform: translateY(-400%);
  }
}

/* Elegant rich cards with smooth hover */
.elegant-card {
    background: linear-gradient(135deg, #6c3c00, #e6b25d);
    border-radius: 15px;
    padding: 25px;
    color: white;
    transition: all 0.4s ease;
    box-shadow: 0 10px 20px rgba(108, 60, 0, 0.2);
    border: none;
    position: relative;
    overflow: hidden;
    height: 100%;
}

.elegant-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(230, 178, 93, 0.3), rgba(108, 60, 0, 0.1));
    opacity: 0;
    transition: opacity 0.4s ease;
    z-index: 1;
    border-radius: 15px;
}

.elegant-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 30px rgba(108, 60, 0, 0.3);
}

.elegant-card:hover::before {
    opacity: 1;
}

.elegant-card .card-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 12px;
    position: relative;
    z-index: 2;
    letter-spacing: 0.5px;
}

.elegant-card .card-value {
    font-size: 48px;
    font-weight: 700;
    margin: 15px 0;
    position: relative;
    z-index: 2;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.elegant-card.primary {
    background: linear-gradient(135deg, #6c3c00, #e6b25d);
}

.elegant-card.secondary {
    background: linear-gradient(135deg, #004e6c, #5dbfe6);
}
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Get MongoDB connection details from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Twitter color palette
TWITTER_COLORS = {
    'blue': '#1DA1F2',
    'black': '#14171A',
    'dark_gray': '#657786',
    'light_gray': '#AAB8C2',
    'extra_light_gray': '#E1E8ED',
    'extra_extra_light_gray': '#F5F8FA',
    'white': '#FFFFFF'
}

def get_total_engagements():
    """
    Function to fetch the total number of tweet engagements.
    Each unique _id represents a distinct engagement.
    
    Returns:
        int: Total count of unique engagements
    """
    try:
        logger.info("Fetching total engagements")
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        
        # Use the twitter_actions collection
        collection = db["twitter_actions"]
        
        # Count total unique engagements based on _id
        # Each document has a unique _id so this counts all documents
        total_count = collection.estimated_document_count()
        
        # Close connection
        client.close()
        
        logger.info(f"Found {total_count} total engagements")
        return total_count
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        st.error(f"MongoDB Connection Error: {str(e)}")
        return 0

def get_successful_engagements():
    """
    Function to fetch the total number of successful tweet engagements.
    Looks for a 'Success' or similar field in the documents and counts
    those that have a truthy value.
    
    Returns:
        int: Total count of successful engagements
    """
    try:
        logger.info("Fetching successful engagements")
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        
        # Use the twitter_actions collection
        collection = db["twitter_actions"]
        
        # Count documents that are either:
        # 1. Have "Success" in result field
        # 2. Have "Failed" in result but "Success" in rerun
        successful_count = collection.count_documents({
            "$or": [
                {"result": {"$regex": "Success", "$options": "i"}},  # Case insensitive Success in result
                {
                    "$and": [
                        {"result": {"$regex": "Failed", "$options": "i"}},  # Failed attempts
                        {"rerun": {"$regex": "Success", "$options": "i"}}   # But succeeded in rerun
                    ]
                }
            ]
        })
        
        client.close()
        return successful_count
        
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        st.error(f"MongoDB Connection Error: {str(e)}")
        return 0

def get_success_ratio():
    """
    Calculate the success ratio percentage.
    
    Returns:
        float: Percentage of successful engagements
    """
    try:
        logger.info("Calculating success ratio")
        # Get total and successful counts
        total = get_total_engagements()
        successful = get_successful_engagements()
        
        # Calculate percentage
        if total > 0:
            ratio = (successful / total) * 100
            logger.info(f"Success ratio: {ratio:.2f}%")
            return ratio
        else:
            logger.warning("No engagements found for success ratio calculation")
            return 0
    except Exception as e:
        logger.error(f"Error calculating success ratio: {str(e)}")
        return 0

def get_engagement_time_series():
    """
    Fetches engagement time series data for the last 7 days.
    """
    try:
        logger.info("Fetching engagement time series data")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        # Get current date in UTC
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Ensure we include the full current day
        end_date = end_date.replace(hour=23, minute=59, second=59)
        start_date = start_date.replace(hour=0, minute=0, second=0)
        
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$date"
                        }
                    },
                    "engagements": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        client.close()
        
        # Convert to DataFrame and handle missing dates
        df = pd.DataFrame(result)
        if not df.empty:
            df = df.rename(columns={"_id": "date", "engagements": "engagements"})
            df['date'] = pd.to_datetime(df['date'])
            
            # Create complete date range including today
            date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
            all_dates = pd.DataFrame({'date': date_range})
            
            # Merge with actual data and fill missing values
            df = pd.merge(all_dates, df, on='date', how='left').fillna(0)
            df['engagements'] = df['engagements'].astype(int)
            
            return df.sort_values('date')
            
        return pd.DataFrame(columns=['date', 'engagements'])
        
    except Exception as e:
        logger.error(f"Error in time series data: {str(e)}")
        return pd.DataFrame(columns=['date', 'engagements'])

def get_celebrity_engagement_data():
    """
    Fetches and aggregates engagement counts by celebrity tweet.
    """
    try:
        logger.info("Fetching celebrity engagement data")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        pipeline = [
            {
                "$match": {
                    "username": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$username",
                    "engagements": {"$sum": 1}
                }
            },
            {
                "$sort": {"engagements": -1}
            },
            {
                "$limit": 5
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        client.close()
        
        if result:
            df = pd.DataFrame(result)
            df = df.rename(columns={"_id": "username", "engagements": "engagements"})
            # Clean up usernames (remove @ if present)
            df['username'] = df['username'].apply(lambda x: x.replace('@', '') if isinstance(x, str) and x.startswith('@') else x)
            logger.info(f"Found {len(df)} celebrity records")
            return df
        
        logger.warning("No celebrity engagement data found")
        return pd.DataFrame(columns=['username', 'engagements'])
        
    except Exception as e:
        logger.error(f"Error fetching celebrity data: {str(e)}")
        return pd.DataFrame(columns=['username', 'engagements'])

def get_user_engagement_data():
    """
    Fetches and aggregates engagement counts by Twitter users.
    Returns top 5 users with highest engagement counts.
    
    Returns:
        pandas.DataFrame: DataFrame containing user names and their engagement counts
        Columns: ['name', 'engagements']
    
    Raises:
        Returns empty DataFrame with appropriate error message on failure
    """
    try:
        logger.info("Fetching user engagement data")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        pipeline = [
            {"$group": {
                "_id": "$name",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        result = list(collection.aggregate(pipeline))
        client.close()
        
        df = pd.DataFrame(result)
        if not df.empty:
            df = df.rename(columns={"_id": "name", "count": "engagements"})
            logger.info(f"Found {len(df)} user records")
            return df
        
        logger.warning("No user engagement data found")
        st.error("No user engagement data available")
        return pd.DataFrame(columns=['name', 'engagements'])
        
    except Exception as e:
        logger.error(f"Error fetching user data: {str(e)}")
        st.error("Failed to fetch user engagement data")
        return pd.DataFrame(columns=['name', 'engagements'])
        
def get_rerun_comparison_data():
    """
    Replicates Excel formula logic for comparing Initial Run vs Rerun metrics.
    Excel formulas reference Analysis Overall sheet cells:
    D7, D12 (Likes)
    D8, D13 (Reposts/Retweets)
    D9, D14 (Comments)
    """
    try:
        logger.info("Fetching rerun comparison data using Excel formula logic")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]

        # Pipeline for initial run (equivalent to D7, D8, D9)
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
                                    "retweets",  # Changed from "reposts" to "retweets"
                                    "comments"
                                ]
                            }
                        ]
                    },
                    "count": {"$sum": 1}
                }
            }
        ]

        # Pipeline for rerun (equivalent to D12, D13, D14)
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
                                    "retweets",  # Changed from "reposts" to "retweets"
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

        client.close()

        # Structure data like Excel series
        metrics = {
            "initial": {
                "likes": initial_results.get("likes", 0),
                "retweets": initial_results.get("retweets", 0),  # Changed from "reposts" to "retweets"
                "comments": initial_results.get("comments", 0)
            },
            "rerun": {
                "likes": rerun_results.get("likes", 0),
                "retweets": rerun_results.get("retweets", 0),  # Changed from "reposts" to "retweets"
                "comments": rerun_results.get("comments", 0)
            }
        }

        # If no data found, don't use hardcoded values
        if all(v == 0 for v in metrics["initial"].values()) and all(v == 0 for v in metrics["rerun"].values()):
            logger.warning("No rerun comparison data found")
            return metrics

        logger.info(f"Metrics found - Initial: {metrics['initial']}, Rerun: {metrics['rerun']}")
        return metrics

    except Exception as e:
        logger.error(f"Error fetching rerun comparison data: {str(e)}")
        return {
            "initial": {"likes": 0, "retweets": 0, "comments": 0},  # Changed from "reposts" to "retweets"
            "rerun": {"likes": 0, "retweets": 0, "comments": 0}  # Changed from "reposts" to "retweets"
        }

def main():
    """Main function to run the Streamlit dashboard."""
    logger.info("Starting dashboard application")
    
    # Page header
    # Page header with animated text
    st.markdown("""
        <h1 style='color: #333333; text-align: center; padding: 20px 0 10px 0; margin: 0;'>
            Tweet Engagements Dashboard
        </h1>
        
        <div class="text7" style="justify-content: center; margin-bottom: 20px;">
            <div>WE GENERATE</div>
            <div class="words">
                <span>LIKES</span>
                <span>RETWEETS</span>
                <span>COMMENTS</span>
                <span>ENGAGEMENT</span>
                <span>LIKES</span>
            </div>
            <div>FOR YOU!!</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Refresh button and timestamp in same line
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Refresh Data"):
            logger.info("Manual refresh triggered")
            st.rerun()
    with col2:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        st.write(f"Last updated: {current_time}")
    
    # Get all required data
    total_engagements = get_total_engagements()
    successful_engagements = get_successful_engagements()
    success_ratio = get_success_ratio()
    celebrity_data = get_celebrity_engagement_data()
    user_data = get_user_engagement_data()
    time_series_data = get_engagement_time_series()
    rerun_data = get_rerun_comparison_data()

    # Create a 2-column layout: Left for KPIs (1/3) and Right for pie chart (2/3)
    left_col, right_col = st.columns([1, 2])

    # Left column - Stacked KPI cards
    with left_col:
        # Total Engagements Card
        st.markdown(
            f"""
            <div class="elegant-card primary" style="padding: 0.6rem; height: 175px; margin-bottom: 10px;">
                <div class="card-title" style="font-size: 0.7rem;">Total Engagements</div>
                <div class="card-value" style="font-size: 1.2rem;">{total_engagements}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # Successful Engagements Card
        st.markdown(
            f"""
            <div class="elegant-card secondary" style="padding: 0.6rem; height: 175px;margin-bottom: 10px;">
                <div class="card-title" style="font-size: 0.7rem;">Successful Engagements</div>
                <div class="card-value" style="font-size: 1.2rem;">{successful_engagements}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Right column - Large pie chart
    with right_col:
        st.markdown(
        """
        <h3 style="text-align: center; color: #6c3c00; font-size: 40px; font-weight: bold;">
            Success Ratio
        </h3>
        """,
        unsafe_allow_html=True
    )
        
        # Success ratio donut chart
        fig_success = go.Figure(data=[go.Pie(
            labels=['Successful', 'Failed'],
            values=[success_ratio, 100 - success_ratio],
            hole=0.7,
            textinfo='none',
            marker=dict(
                colors=['#32c5d2', '#ffb822'],
                line=dict(color='white', width=2)
            )
        )])
        
        fig_success.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,  # Made pie chart bigger
            width=None,
            annotations=[dict(
                text=f"{success_ratio:.1f}%",
                x=0.5, y=0.5,
                font=dict(size=28, color='#6c3c00', family='Arial Black'),
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig_success, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Modern Initial vs Rerun Performance Section
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1a1a1a, #2d2d2d); padding: 20px; border-radius: 15px; margin: 20px 0;">
            <h2 style="text-align: center; color: #fff; font-size: 28px; margin-bottom: 30px;">
                <span style="background: linear-gradient(120deg, #3498db, #2ecc71); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Initial vs Rerun Performance
                </span>
            </h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    # Initial Run Chart (Modernized)
    with col1:
        initial_data = {
            'Metric': ['Likes', 'Retweets', 'Comments'],
            'Count': [
                rerun_data['initial']['likes'],
                rerun_data['initial']['retweets'],
                rerun_data['initial']['comments']
            ]
        }
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=initial_data['Metric'],
            y=initial_data['Count'],
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1'],
            marker_line_width=0,
            opacity=0.9
        ))
        
        # Add value labels on top of bars
        for i, value in enumerate(initial_data['Count']):
            fig.add_annotation(
                x=initial_data['Metric'][i],
                y=value,
                text=str(value),
                showarrow=False,
                yshift=10,
                font=dict(size=14, color='#ffffff')
            )
        
        fig.update_layout(
            title=dict(
                text='Initial Run Metrics',
                font=dict(size=20, color='#ffffff'),
                x=0.5,
                y=0.95
            ),
            height=400,
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                title=None,
                tickfont=dict(size=14, color='#ffffff')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                title=None,
                tickfont=dict(size=14, color='#ffffff')
            ),
            bargap=0.4
        )
        
        # Add hover effects
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>' +
                         'Count: %{y}<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.9)',
                font_size=14,
                font_color='#000000'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Rerun Chart (Modernized)
    with col2:
        rerun_data_combined = {
            'Metric': ['Likes', 'Retweets', 'Comments'],
            'Count': [
                rerun_data['rerun']['likes'],
                rerun_data['rerun']['retweets'],
                rerun_data['rerun']['comments']
            ]
        }
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=rerun_data_combined['Metric'],
            y=rerun_data_combined['Count'],
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1'],
            marker_line_width=0,
            opacity=0.9
        ))
        
        # Add value labels on top of bars
        for i, value in enumerate(rerun_data_combined['Count']):
            fig.add_annotation(
                x=rerun_data_combined['Metric'][i],
                y=value,
                text=str(value),
                showarrow=False,
                yshift=10,
                font=dict(size=14, color='#ffffff')
            )
        
        fig.update_layout(
            title=dict(
                text='Rerun Metrics',
                font=dict(size=20, color='#ffffff'),
                x=0.5,
                y=0.95
            ),
            height=400,
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                title=None,
                tickfont=dict(size=14, color='#ffffff')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                title=None,
                tickfont=dict(size=14, color='#ffffff')
            ),
            bargap=0.4
        )
        
        # Add hover effects
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>' +
                         'Count: %{y}<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.9)',
                font_size=14,
                font_color='#000000'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Add comparison metrics below charts
    st.markdown("""
        <div style="background: linear-gradient(135deg, #2d2d2d, #1a1a1a); padding: 20px; border-radius: 15px; margin: 20px 0;">
            <div style="display: flex; justify-content: space-around; text-align: center;">
    """, unsafe_allow_html=True)

    # Calculate percentage changes
    for metric in ['likes', 'retweets', 'comments']:
        initial = rerun_data['initial'][metric]
        rerun = rerun_data['rerun'][metric]
        if initial > 0:
            change = ((rerun - initial) / initial) * 100
            color = '#2ecc71' if change >= 0 else '#e74c3c'
            arrow = '↑' if change >= 0 else '↓'
            st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 0 10px;">
                    <h4 style="color: #ffffff; margin: 0;">{metric.title()}</h4>
                    <p style="color: {color}; font-size: 24px; margin: 10px 0;">
                        {arrow} {abs(change):.1f}%
                    </p>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # Time series chart with reduced height
    st.markdown('<div class="chart-container engagement-chart dark-chart">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Daily Engagement Trends (Last 7 Days)</div>', unsafe_allow_html=True)
    
    if not time_series_data.empty:
        fig_trends = go.Figure()
        fig_trends.add_trace(go.Scatter(
            x=time_series_data['date'],
            y=time_series_data['engagements'],
            mode='lines+markers+text',
            name='Engagements',
            line=dict(
                color='#1DA1F2',
                width=4,
                shape='spline',
                smoothing=1.3
            ),
            marker=dict(
                size=10,
                color='#1DA1F2'
            ),
            text=time_series_data['engagements'].astype(int),
            textposition='top center',
            textfont=dict(
                size=16,
                color='#FFFFFF',
                family='Arial Black'
            )
        ))
        
        fig_trends.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            plot_bgcolor='#1E1E1E',
            paper_bgcolor='#1E1E1E',
            xaxis=dict(
                showgrid=True,
                gridcolor='#333333',
                tickfont=dict(color='#FFFFFF'),
                title_font=dict(color='#FFFFFF')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#333333',
                tickfont=dict(color='#FFFFFF'),
                title_font=dict(color='#FFFFFF')
            )
        )
        
        st.plotly_chart(fig_trends, use_container_width=True)

    # Modified Celebrity and User engagement charts - Ensuring descending order
    col1, col2 = st.columns(2)
    
    # Celebrity engagement chart - Top 5 descending
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Top 5 Celebrity Engagements</div>', unsafe_allow_html=True)
        
        if not celebrity_data.empty:
            # Ensure top 5 descending order
            celebrity_data = celebrity_data.sort_values('engagements', ascending=False).head(5)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=celebrity_data['username'],
                x=celebrity_data['engagements'],
                orientation='h',
                marker_color='#3498db',
                text=celebrity_data['engagements'],
                textposition='outside'
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
                yaxis={'categoryorder':'total descending'}  # This ensures descending order
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # User engagement chart - Top 5 descending
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Top 5 User Engagements</div>', unsafe_allow_html=True)
        
        if not user_data.empty:
            # Ensure top 5 descending order
            user_data = user_data.sort_values('engagements', ascending=False).head(5)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=user_data['name'],
                x=user_data['engagements'],
                orientation='h',
                marker_color='#3498db',
                text=user_data['engagements'],
                textposition='outside'
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
                yaxis={'categoryorder':'total descending'}  # This ensures descending order
            )
            
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()

