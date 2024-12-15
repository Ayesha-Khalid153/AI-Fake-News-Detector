import requests
import os
import spacy
import schedule
import time
import faiss
import pandas as pd
import numpy as np
from urllib.parse import urlparse
from textblob import TextBlob
from datetime import datetime

url = "https://newsdata.io/api/1/latest" # URL of the NewsData.io.
api_key = "pub_62108ce62f25c8321b4746e878acb35484998" # API key

publishers = ["ARY News", "Dawn News", "BBC", "geo.tv", "The Hindu", "Al Jazeera"]

nlp = spacy.load("en_core_web_md")

# FAISS index initialization
index = None
metadata = []

def initialize_faiss_index(d, nlist=100):
    global index
    quantizer = faiss.IndexFlatL2(d)
    index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)
    print("FAISS index initialized.")


# Initialize FAISS index with the vector dimension
initialize_faiss_index(nlp.vocab.vectors.shape[1])

# Defining POS tags for pronouns and helping verbs
pronouns_POS = {"PRP", "PRP$", "WP", "WP$"}
helping_Verb = {"is", "am", "are", "was", "were", "be", "been", "being", 
                "have", "has", "had", "do", "does", "did", "will", "shall", 
                "can", "could", "should", "would", "might", "must", "may",
                "the", "a", "an", "or", "for", "all", "at", "on", "to", "up",
                "in", "of", "and", "it", "this", "that", "our", "those"}

# Function to fetch articles for a publisher
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

# Function to fetch and process articles from all publishers
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


# Clean description by removing unnecessary words
def cleaning_description(description):
    doc = nlp(description)
    cleaned = [
        token.text for token in doc
        if token.pos_ not in pronouns_POS and token.text.lower() not in helping_Verb
    ]
    return " ".join(cleaned)

# Get vector representation for an article description
def get_vector(description):
    doc = nlp(description)
    # Get the average vector for the document (article description)
    vectors = [token.vector for token in doc if not token.is_stop and not token.is_punct]
    if vectors:
        vector = np.mean(vectors, axis=0).astype(np.float32)  # Average the vectors of the words
        print(f"Vector shape for '{description[:30]}...': {vector.shape}")  # Print vector shape for debugging
        print(f"Vector values: {vector[:10]}...")  # Print the first 10 values to inspect
        return vector
    else:
        vector = np.zeros((nlp.vocab.vectors.shape[1],)).astype(np.float32)  # Ensure correct dimension
        print(f"Vector shape for '{description[:30]}...': {vector.shape}")  # Print vector shape for debugging
        return vector
    
# Preprocess articles, clean descriptions, and generate vectors
def preprocess_articles(articles, publisher_name):
    processed_articles = []
    global metadata
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
        #ategory = article.get("category", "N/A") if article.get("category") else "N/A"
        #country = article.get("country", "N/A") if article.get("country") else "N/A"
        #domain = urlparse(article['link']).netloc
        #sentiment = TextBlob(description).sentiment.polarity
        
        # Check if the vector is not empty before adding it to FAISS index
        # Skip zero vectors
        if np.count_nonzero(description_vector) == 0:
            continue
        
        # Collect vector for batch addition
        vectors_to_add.append(description_vector)

        # Add metadata for each article
        metadata.append({
            'title': article['title'],
            'publisher': publisher_name,
            'description': cleaned_description,
            'sentiment': TextBlob(description).sentiment.polarity
        })

        processed_articles.append({
            'date': date,
            'domain': urlparse(article['link']).netloc,
            'category': article.get("category", "N/A"),
            'country': article.get("country", "N/A"),
            'publisher': publisher_name,
            'title': article.get("title", "N/A"),
            'description': cleaned_description,
            'link': article.get('link',"N/A"),
            'sentiment': TextBlob(description).sentiment.polarity,
        })
        # Add vectors to FAISS index in batch
    if vectors_to_add:
        vectors_to_add = np.array(vectors_to_add).astype(np.float32)  # Convert to NumPy array
        index.add(vectors_to_add)  # Add vectors to FAISS index
        print(f"Added {len(vectors_to_add)} vectors to FAISS index. Current index size: {index.ntotal}")

    return processed_articles

def storing_data(articles, file_name = "cleaneddata.csv"):
    df_new = pd.DataFrame(articles)
    if os.path.exists(file_name):
        df_existing = pd.read_csv(file_name)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(file_name, index=False)
    else:
        df_new.to_csv(file_name, index=False)

def initialize_faiss_with_training(articles):
    global index
    sample_vectors = []
    for article in articles:
        description = article.get("description", "")
        cleaned_description = cleaning_description(description)
        vector = get_vector(cleaned_description)
        if np.count_nonzero(vector) > 0:
            sample_vectors.append(vector)
    
    sample_vectors = np.array(sample_vectors)
    if len(sample_vectors) > 0:
        index.train(sample_vectors)
        print("FAISS index trained with real article vectors.")
    else:
        print("No valid vectors for training FAISS index.")

def train_faiss_index_with_vectors(vectors):
    vectors = np.array(vectors).astype(np.float32)
    if not index.is_trained:
        print(f"Training FAISS index with {len(vectors)} vectors...")
        index.train(vectors)
        print("FAISS index trained successfully.")
    else:
        print("FAISS index is already trained.")

def fetching_data():
    all_vectors = []
    all_articles = []
    for publisher in publishers:
        raw_articles = fetch_articles_for_publisher(publisher)
        for article in raw_articles:
            description = article.get("description", "")
            cleaned_description = cleaning_description(description)
            vector = get_vector(cleaned_description)
            if np.count_nonzero(vector) > 0:
                all_vectors.append(vector)  # Collect all vectors for training
        processed = preprocess_articles(raw_articles, publisher)
        all_articles.extend(processed)

    # Train FAISS index with collected vectors
    if all_vectors:
        train_faiss_index_with_vectors(all_vectors)

    # Save processed articles
    storing_data(all_articles)




def query_faiss(query_description):
    # Get the vector for the query description
    query_vector = get_vector(query_description)
    
    # Ensure the index has been populated
    if index is None or index.ntotal == 0:
        print("FAISS index is empty. Please ensure it is populated with vectors.")
        return

    # Search FAISS for similar articles
    if index is not None and metadata:
        distances, indices = index.search(np.array([query_vector]), k=5)  # Retrieve top 5 similar articles
        
        # Print the results
        print(f"Query: {query_description}\n")
        for dist, idx in zip(distances[0], indices[0]):
            article = metadata[idx]
            print(f"Title: {article['title']}")
            print(f"Publisher: {article['publisher']}")
            print(f"Description: {article['description'][:200]}...")  # Print a snippet of the description
            print(f"Sentiment: {article['sentiment']:.2f}")
            print(f"Distance: {dist:.2f}")
            print("="*80)
    else:
        print("FAISS index is either not initialized or empty.")



# Example to test the similarity query
query_description = "Global economy outlook for 2024"
print(f"Similar data: {query_faiss(query_description)}")




schedule.every(2).minutes.do(fetching_data)

while(True):
    
    schedule.run_pending()
    time.sleep(60)