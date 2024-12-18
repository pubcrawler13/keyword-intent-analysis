import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# Set the page configuration
st.set_page_config(
    page_title="Primary Keywords Search Intent Analysis Tool",
    layout="wide"
)

# Apply custom CSS for dropdown and file uploader widths
st.markdown(
    """
    <style>
    div[data-baseweb="select"] {
        width: 250px !important; /* Dropdown width */
    }
    div.stFileUploader {
        width: 750px !important; /* File uploader width */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Ahrefs API Token
API_TOKEN = "rKMvQKYP6NdrHqVAgZUoqNPvhy4XaGGM7Fpk5Crh"

# Function to fetch organic results for a keyword
def fetch_organic_results(keyword, country):
    url = "https://api.ahrefs.com/v3/serp-overview/serp-overview"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
    }
    params = {
        "keyword": keyword,
        "select": "url",
        "country": country
    }
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        positions = data.get("positions", [])
        # Extract valid URLs and limit to top 10
        urls = [entry.get("url") for entry in positions if entry.get("url")]
        return urls[:10]
    else:
        st.error(f"Error fetching results for keyword '{keyword}': {response.status_code}")
        return []

def process_uploaded_file(uploaded_file):
    """
    Processes the uploaded CSV file:
    - Skips all rows before the first row containing 'URL'.
    - Allows the user to select the column containing keywords.
    """
    df = pd.read_csv(uploaded_file)

    # Step 1: Skip rows before the first row containing 'URL'
    st.write("Detecting the first valid row after 'URL'...")
    for index, row in df.iterrows():
        if row.astype(str).str.contains("URL", case=False, na=False).any():
            df = df.iloc[index + 1:]  # Skip rows before this one
            st.write(f"Filtered DataFrame starting from row {index + 2}:")
            st.write(df.head())
            break

    # Step 2: Let the user select the keyword column
    keyword_column = st.selectbox("Select the column containing keywords:", df.columns)

    # Handle case where no column is selected
    if not keyword_column:
        st.error("No column selected. Unable to proceed.")
        return None

    # Extract keywords from the identified column
    keywords = df[keyword_column].dropna().tolist()
    st.write(f"Detected keywords in column '{keyword_column}'. Found {len(keywords)} keywords.")
    return keywords

def classify_url(url):
    transactional_keywords = [
        "buy", "shop", "order", "cart", "checkout", "sale", "discount", 
        "deal", "promo", "coupon", "offers", "pricing", "quote", "rent",
        "lease", "subscription", "membership", "bid", "auction", 
        "add to cart", "purchase", "store", "bundle", "package", 
        "clearance", "preorder", "wholesale", "free shipping", 
        "fast shipping", "same-day delivery", "click to buy", "limited offer",
        "compare prices", "best price", "hot deal", "new arrivals",
        "featured products", "exclusive offer", "low price guarantee"
    ]
    informational_keywords = [
        "how", "why", "what", "where", "when", "who", "which", "guide", 
        "tutorial", "review", "overview", "tips", "advice", "examples", 
        "comparison", "explained", "analysis", "resource", "article", 
        "wiki", "help", "faq", "step-by-step", "definition", "description",
        "history", "process", "technique", "method", "list", "strategy",
        "plan", "framework", "case study", "insights", "statistics", 
        "facts", "benefits", "reasons", "types", "kinds", "categories"
    ]
    transactional_domains = [
        "amazon.com", "ebay.com", "walmart.com", "bestbuy.com", "homedepot.com", "lowes.com",
        # (Additional domains omitted for brevity)
    ]
    informational_domains = [
        "wikipedia.org", "wikihow.com", "britannica.com", "quora.com", "reddit.com",
        # (Additional domains omitted for brevity)
    ]

    url_lower = url.lower()
    if any(domain in url_lower for domain in transactional_domains):
        return "Transactional", f"Matched transactional domain: {url_lower}"
    if any(domain in url_lower for domain in informational_domains):
        return "Informational", f"Matched informational domain: {url_lower}"
    if any(keyword in url_lower for keyword in transactional_keywords):
        return "Transactional", None
    if any(keyword in url_lower for keyword in informational_keywords):
        return "Informational", None
    return "Unknown", "No matches found."

def main():
    st.title("Optimization Roadmap - Primary Keywords Search Intent Analysis Tool")
    st.write("Fetch and classify top 10 organic results for each keyword.")

    # Country selection
    country = st.selectbox("Select your country:", [
    "us", "ae", "ar", "at", "au", "be", "br", "ca", "ch", "cn", "cz", 
    "de", "dk", "es", "fi", "fr", "gr", "hk", "hu", "id", "ie", "il", 
    "in", "it", "jp", "kr", "mx", "my", "nl", "no", "nz", "ph", "pl", 
    "pt", "ru", "sa", "se", "sg", "th", "tr", "tw", "uk", "vn", "za"
])

    input_type = st.radio("Choose input type:", ["Upload CSV", "Enter URL"])
    keywords = None

    if input_type == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            keywords = process_uploaded_file(uploaded_file)
            if not keywords:
                st.stop()

    elif input_type == "Enter URL":
        url_input = st.text_input("Enter the URL:")
        if url_input and st.button("Fetch Keywords"):
            try:
                response = requests.get(url_input)
                response.raise_for_status()
                content = response.text
                keywords = extract_keywords_from_html(content)
                st.write("Keywords extracted from the URL:")
                st.write(keywords)
            except Exception as e:
                st.error(f"Error fetching content from the URL: {e}")
                return

    if keywords and st.button("Analyze Keywords"):
        st.write("Processing keywords...")
        results = []

        def classify_and_append(keyword, url, results):
            search_intent, explanation = classify_url(url)
            results.append({"Keyword": keyword, "URL": url, "Type": search_intent, "Explanation": explanation})
        
        with ThreadPoolExecutor() as executor:
            for keyword in keywords:
                st.write(f"Fetching results for keyword: {keyword}")
                urls = fetch_organic_results(keyword.strip(), country)
                if not urls:
                    st.warning(f"No results found for keyword '{keyword}'.")
                    continue
                for url in urls:
                    executor.submit(classify_and_append, keyword.strip(), url, results)

        if not results:
            st.error("No results were processed. Please check API responses.")
            return

        # Convert results to DataFrame
        results_df = pd.DataFrame(results)

        # Display results in a concise format
        st.subheader("Top 10 Organic Results with Search Intent and Explanations")
        st.write(results_df)

        # Generate per-keyword intent distribution charts
        st.subheader("Search Intent Distribution by Keyword")
        for keyword in results_df["Keyword"].unique():
            subset = results_df[results_df["Keyword"] == keyword]
            summary = subset["Type"].value_counts(normalize=True) * 100
            st.write(f"Search Intent for '{keyword}':")
            st.bar_chart(summary)

        # Generate overall intent distribution chart
        st.subheader("Overall Search Intent Distribution")
        overall_summary = results_df["Type"].value_counts(normalize=True) * 100
        st.bar_chart(overall_summary)

        # Option to download results
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="organic_results_with_intent_and_explanations.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
