import nltk
nltk.download('vader_lexicon')

import streamlit as st
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# Sentiment Analysis Function
def analyze_sentiment(text):
    sid = SentimentIntensityAnalyzer()
    return sid.polarity_scores(text)

# Web Scraping Function
def scrape_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    return " ".join([p.get_text() for p in paragraphs])

# Similarity Function
def compute_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(vectors)[0, 1]

# Streamlit App
st.title("Sentiment & Content Comparison Tool")

# User Input
st.sidebar.header("Inputs")
competitor_url = st.sidebar.text_input("Competitor URL")
client_text = st.sidebar.text_area("Client Content")

if st.sidebar.button("Analyze"):
    if competitor_url and client_text:
        # Scrape Competitor Content
        competitor_text = scrape_content(competitor_url)

        # Sentiment Analysis
        competitor_sentiment = analyze_sentiment(competitor_text)
        client_sentiment = analyze_sentiment(client_text)

        # Similarity Analysis
        similarity = compute_similarity(competitor_text, client_text)

        # Display Results
        st.subheader("Sentiment Analysis")
        st.write("Competitor Sentiment:", competitor_sentiment)
        st.write("Client Sentiment:", client_sentiment)

        st.subheader("Content Similarity")
        st.write(f"Similarity Score: {similarity:.2f}")

        # Visualization
        st.subheader("Visualization")
        sentiments = ["Competitor", "Client"]
        scores = [competitor_sentiment['compound'], client_sentiment['compound']]
        plt.bar(sentiments, scores)
        plt.title("Sentiment Comparison")
        plt.ylabel("Sentiment Score")
        st.pyplot(plt)

        # Recommendations
        st.subheader("Recommendations")
        if similarity < 0.5:
            st.write("Consider aligning your content tone or topic with the competitor's.")
        else:
            st.write("Your content is well-matched with the competitor's!")
    else:
        st.error("Please provide both the competitor URL and client content.")
