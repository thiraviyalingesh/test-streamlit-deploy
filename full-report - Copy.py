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
        logging.FileHandler("dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    /* Main background and text colors */
    .main {
        background-color: #1E1E1E;
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #990000;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #c20000;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Headings */
    h1, h2, h3 {
        color: white;
    }
    
    /* Metrics container */
    .metric-container {
        text-align: center; 
        background-color: #2C2C2C; 
        padding: 20px; 
        border-radius: 15px; 
        margin-top: 10px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border-left: 5px solid #3498db;
        height: 100%;
    }
    
    /* Success metrics container */
    .success-metric-container {
        text-align: center; 
        background-color: #2C2C2C; 
        padding: 20px; 
        border-radius: 15px; 
        margin-top: 10px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border-left: 5px solid #27ae60;
        height: 100%;
    }
    
    /* Metric title */
    .metric-title {
        color: #3498db;
        font-weight: bold;
        font-size: 1.8rem;
        margin-bottom: 15px;
    }
    
    /* Success metric title */
    .success-metric-title {
        color: #27ae60;
        font-weight: bold;
        font-size: 1.8rem;
        margin-bottom: 15px;
    }
    
    /* Big number display */
    .big-number {
        color: #3498db; 
        font-size: 60px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Success big number display */
    .success-big-number {
        color: #27ae60; 
        font-size: 60px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Chart container */
    .chart-container {
        background-color: #2C2C2C;
        padding: 25px;
        border-radius: 15px;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border-left: 5px solid #3498db;
    }
    
    /* Chart title */
    .chart-title {
        color: #3498db;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 20px;
        color: #aaa;
        font-size: 0.9rem;
        margin-top: 30px;
        border-top: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Get MongoDB connection details from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

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
    try:
        logger.info("Fetching engagement time series data")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        # Calculate last 7 days date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6)
        
        # Create aggregation pipeline
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
        
        # Convert to DataFrame
        df = pd.DataFrame(result)
        if not df.empty:
            df = df.rename(columns={"_id": "date"})
            df['date'] = pd.to_datetime(df['date'])
            
            # Fill missing dates with zeros
            date_range = pd.date_range(start=start_date.date(), end=end_date.date())
            all_dates = pd.DataFrame({'date': date_range})
            df = pd.merge(all_dates, df, on='date', how='left').fillna(0)
            
            return df.sort_values('date')
        
        return pd.DataFrame(columns=['date', 'engagements'])
        
    except Exception as e:
        logger.error(f"MongoDB Connection Error: {str(e)}")
        st.error(f"MongoDB Connection Error: {str(e)}")
        return pd.DataFrame()

def get_celebrity_engagement_data():
    """
    Fetches and aggregates engagement counts by celebrity tweet.
    Returns top 5 celebrities with highest engagement counts.
    
    Returns:
        pandas.DataFrame: DataFrame containing celebrity usernames and their engagement counts
        Columns: ['username', 'engagements']
    
    Raises:
        Returns empty DataFrame with appropriate error message on failure
    """
    try:
        logger.info("Fetching celebrity engagement data")
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DATABASE]
        collection = db["twitter_actions"]
        
        pipeline = [
            {"$group": {
                "_id": "$username",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        result = list(collection.aggregate(pipeline))
        client.close()
        
        df = pd.DataFrame(result)
        if not df.empty:
            df = df.rename(columns={"_id": "username", "count": "engagements"})
            df['username'] = df['username'].apply(lambda x: x.replace('@', '') if isinstance(x, str) and x.startswith('@') else x)
            logger.info(f"Found {len(df)} celebrity records")
            return df
        
        logger.warning("No celebrity engagement data found")
        st.error("No celebrity engagement data available")
        return pd.DataFrame(columns=['username', 'engagements'])
        
    except Exception as e:
        logger.error(f"Error fetching celebrity data: {str(e)}")
        st.error("Failed to fetch celebrity engagement data")
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
    """
    Main function to run the Streamlit dashboard.
    Displays:
    - Key metrics (Total Engagements, Successful Engagements, Success Ratio)
    - Time series engagement data
    - Top celebrity and user engagement data
    """
    logger.info("Starting dashboard application")
    
    # Page header
    st.markdown("<h1 style='text-align: center;'>Tweet Engagements Dashboard</h1>", unsafe_allow_html=True)
    
    # Refresh button and timestamp
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
    
    # Display metrics in same line
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-title">Total Engagements</div>
                <div class="big-number">{total_engagements}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-title">Successful Engagements</div>
                <div class="big-number">{successful_engagements}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        # Success ratio donut chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Success Ratio</div>', unsafe_allow_html=True)
        
        labels = ['Successful', 'Failed']
        values = [success_ratio, 100 - success_ratio]
        colors = ['#74c69d', '#e9ecef']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.7,
            textinfo='none',
            marker=dict(colors=colors)
        )])
        
        fig.add_annotation(
            text=f"{success_ratio:.1f}%",
            font=dict(size=20, family='Arial', color='white'),
            showarrow=False
        )
        
        fig.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            width=200,
            height=200
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Time series chart
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Daily Engagement Trends (Last 7 Days)</div>', unsafe_allow_html=True)
    
    if not time_series_data.empty:
        fig = go.Figure()
        
        # Add line with markers and text labels
        fig.add_trace(go.Scatter(
            x=time_series_data['date'],
            y=time_series_data['engagements'],
            mode='lines+markers+text',
            name='Engagements',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8),
            text=time_series_data['engagements'].astype(int),
            textposition='top center',
            textfont=dict(size=12, color='white')
        ))
        
        fig.update_layout(
            xaxis_title=None,
            yaxis_title="Number of Engagements",
            template='plotly_dark',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No time series data available")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Side-by-side bar charts
    col1, col2 = st.columns(2)
    
    # Celebrity engagement chart
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Top Celebrity Engagements</div>', unsafe_allow_html=True)
        
        if not celebrity_data.empty:
            # Sort data in descending order
            celebrity_data = celebrity_data.sort_values('engagements', ascending=False).head(5)
            
            fig = px.bar(
                celebrity_data,
                y='username',
                x='engagements',
                orientation='h',
                color_discrete_sequence=['#3498db']
            )
            
            fig.update_traces(
                texttemplate='%{x}',
                textposition='outside',
                textfont=dict(size=14, color='white')
            )
            
            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                yaxis={'categoryorder':'total ascending'},  # This will show bars in descending order
                template='plotly_dark',
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No celebrity engagement data available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # User engagement chart
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Top User Engagements</div>', unsafe_allow_html=True)
        
        if not user_data.empty:
            # Sort data in descending order
            user_data = user_data.sort_values('engagements', ascending=False).head(5)
            
            fig = px.bar(
                user_data,
                y='name',
                x='engagements',
                orientation='h',
                color_discrete_sequence=['#3498db']
            )
            
            fig.update_traces(
                texttemplate='%{x}',
                textposition='outside',
                textfont=dict(size=14, color='white')
            )
            
            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                yaxis={'categoryorder':'total ascending'},  # This will show bars in descending order
                template='plotly_dark',
                height=300,
                margin=dict(l=20, r=20, t=10, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No user engagement data available")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()





