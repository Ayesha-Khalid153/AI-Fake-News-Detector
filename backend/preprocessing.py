import requests
import os
import spacy
import schedule
import time
import pandas as pd
import numpy as np
from urllib.parse import urlparse
from textblob import TextBlob
from datetime import datetime

url = "https://newsdata.io/api/1/latest" # URL of the NewsData.io.
api_key = "pub_59941e48406bdabca2c52e358475abcc0892c" # API key

publishers = ["ARY News", "Dawn News", "BBC", "geo.tv", "The Hindu", "Al Jazeera"]

def fetch_articles_for_publisher(publisher):
    params = {
        'apikey': api_key,
        'language': 'en',
        'domain': publisher.lower().replace(" ", ""),  # Adjust for domain format
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Failed to fetch articles for {publisher}: {response.status_code}")
        return []

def retrieving_data(publishers):
    params = {
        "apikey": api_key,
        "language": "en"  # Language filter
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:  # Check for successful HTTP response
        data = response.json()  # Parse JSON
        
        # Ensure the expected data exists
        if "results" in data and data["results"]:
            articles = []
            for publisher in publishers:
                print(f"Fetching articles for {publisher}...")
                publisher_articles = fetch_articles_for_publisher(publisher)
                articles.extend(publisher_articles)
            return articles
        else:
            raise Exception("No results found in the response.")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")
        raise Exception(f"Failed to fetch data. HTTP Status Code: {response.status_code}")

nlp = spacy.load("en_core_web_md")


# Defining POS tags for pronouns and helping verbs
pronouns_POS = {"PRP", "PRP$", "WP", "WP$"}
helping_Verb = {"is", "am", "are", "was", "were", "be", "been", "being", 
                "have", "has", "had", "do", "does", "did", "will", "shall", 
                "can", "could", "should", "would", "might", "must", "may",
                "the", "a", "an", "or", "for", "all", "at", "on", "to", "up",
                "in", "of", "and", "it", "this", "that", "our", "those"}

def cleaning_description(description):
    doc = nlp(description)
    cleaned = [
        token.text for token in doc
        if token.pos_ not in pronouns_POS and token.text.lower() not in helping_Verb
    ]
    return " ".join(cleaned)

def get_vector(description):
    doc = nlp(description)
    # Get the average vector for the document (article description)
    # We exclude stop words and punctuation from the calculation
    vectors = [token.vector for token in doc if not token.is_stop and not token.is_punct]
    if vectors:
        return np.mean(vectors, axis=0)  # Average the vectors of the words
    else:
        return np.zeros((nlp.vector_size,)) 

def preprocess_articles(articles, publisher_name):
    processed_articles = []
    for article in articles:
        # Skip articles with missing critical data
        if not article.get("title"):
            article["title"] = "N/A"
        elif not article.get("link"):
            article["link"] = "N/A"

# Print the current date
        date = (datetime.now().date())
        # Handle None for description
        description = article.get("description", "N/A")
        description = (description) if description else "N/A"
        cleaned_description = cleaning_description(description)
        # Get the vector representation of the article description
        description_vector = get_vector(cleaned_description)
        # Ensure category and country are processed correctly
        category = article.get("category", "N/A") if article.get("category") else "N/A"
        country = article.get("country", "N/A") if article.get("country") else "N/A"
        domain = urlparse(article['link']).netloc
        sentiment = TextBlob(description).sentiment.polarity
        processed_articles.append({
            'date': date,
            'domain': domain,
            'category': category,
            'country': country,
            'publisher': publisher_name,
            'title': article.get("title", "N/A"),
            'description': cleaned_description,
            'link': article.get('link',"N/A"),
            'sentiment': sentiment,
            'description_vector': description_vector  # Add the vector to the article data
        })

    return processed_articles

def storing_data(articles, file_name = "cleaneddata.csv"):
    df_new = pd.DataFrame(articles)
    if os.path.exists(file_name):
        df_existing = pd.read_csv(file_name)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(file_name, index=False)
    else:
        df_new.to_csv(file_name, index=False)


def fetching_data():
    try:
        # Loop over publishers and fetch articles for each publisher
        all_articles = []
        for publisher in publishers:
            print(f"Fetching articles for {publisher}...")
            raw_articles = fetch_articles_for_publisher(publisher)
            articles = preprocess_articles(raw_articles, publisher)  # Include publisher name
            all_articles.extend(articles)

        # Store the processed articles
        storing_data(all_articles)  # Save processed articles to CSV

        # Print the stored articles (debugging or display purpose)
        for article in all_articles:
            print(f"Date: {article['date']}\nDomain: {article['domain']}\nCategory: {article['category']}\nCountry: {article['country']}\nPublisher: {article['publisher']}\nTitle: {article['title']}\nDescription: {article['description']}\nLink: {article['link']}\nSentiment: {article['sentiment']:.2f}\n")
    except Exception as e:
        print(f"Error: {e}")

schedule.every(2).minutes.do(fetching_data)

while(True):
    schedule.run_pending()
    time.sleep(60)