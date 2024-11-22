import streamlit as st
import requests
import pandas as pd

# Ahrefs API Key (replace with your actual API key)
AHREFS_API_KEY = "wwBw9eR3dnDNZz_1nk1gyBqa7HhRLJEKhRl7DIgm"

# Function to Fetch SERP Results
def get_serp_results(domain, api_key):
    url = "https://apiv2.ahrefs.com"
    params = {
        "token": api_key,
        "from": "positions_metrics",  # Adjust as needed
        "target": domain,  # Adjust based on your table's requirement
        "mode": "domain",  # Adjust mode based on target type
        "select": "position,url,title",
        "output": "json",
        "limit": 10
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        st.write("API Response (Debug):", data)
        if "positions_metrics" in data:
            results = [
                {
                    "Position": item.get("position", "N/A"),
                    "URL": item.get("url", "N/A"),
                    "Title": item.get("title", "N/A")
                }
                for item in data["positions_metrics"]
            ]
            return results
        else:
            st.error("The 'positions_metrics' key is missing in the API response.")
            return []
    else:
        st.error(f"Error fetching SERP results: {response.status_code}")
        st.write("Response Text (Debug):", response.text)  # Add debug response text
        return []

# Initialize selected URLs list
selected_urls = []

# Streamlit Sidebar for Keyword Input
st.sidebar.header("Keyword Input")
keyword = st.sidebar.text_input("Enter a keyword for SERP analysis")

if keyword:
    st.sidebar.write("Fetching SERP results...")
    serp_results = get_serp_results(keyword, AHREFS_API_KEY)

    # Display SERP Results with Checkboxes
    if serp_results:
        st.sidebar.write("Top 10 SERP Results:")
        for result in serp_results:
            # Display checkbox for each URL
            selected = st.sidebar.checkbox(
                f"({result['Position']}) {result['Title']}",
                key=result["URL"]
            )
            if selected:
                selected_urls.append(result["URL"])

# Display Selected URLs
if selected_urls:
    st.sidebar.subheader("Selected URLs:")
    for url in selected_urls:
        st.sidebar.write(url)
else:
    st.sidebar.write("No URLs selected yet.")