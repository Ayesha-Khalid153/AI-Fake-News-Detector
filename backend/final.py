import requests
import os
import schedule
import time
import pandas as pd
from urllib.parse import urlparse
from textblob import TextBlob

def retrieving_data():
    url = "https://newsdata.io/api/1/latest" # URL of the NewsData.io.
    api_key = "pub_62108dce5cd6981efd750ebc06be71d34dd46" # API key

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
            for article in data["results"]:
                # Extract fields, with default values if not present
                date = article.get("pubDate")
                description = article.get("description")
                category = ", ".join(article.get("category", [])) if isinstance(article.get("category"), list) else article.get("category", "")
                country = ", ".join(article.get("country", [])) if isinstance(article.get("country"), list) else article.get("country", "")
                title = article.get("title", "")
                link = article.get("link", "")
                # Append articles in array
                articles.append({
                    'date': date,
                    'description': description,
                    'category': category,
                    'country': country,
                    'title': title,
                    'link': link
                })
            return articles
        else:
            raise Exception("No results found in the response.")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")
        raise Exception(f"Failed to fetch data. HTTP Status Code: {response.status_code}")

def preprocess_articles(articles):
    processed_articles = []
    for article in articles:
        # Skip articles with missing critical data
        if not article.get("title"):
            article["title"] = "N/A"
        elif not article.get("link"):
            article["link"] = "N/A"
        
        date = article.get("pubDate")
        # Handle None for description
        description = article.get("description", "")
        description = (description) if description else "N/A"
        
        # Ensure category and country are processed correctly
        category = ", ".join([cat.strip().title() for cat in article.get("category", []) if isinstance(cat, str)]) if article.get("category") else "N/A"
        country = ", ".join([c.strip().upper() for c in article.get("country", []) if isinstance(c, str)]) if article.get("country") else "N/A"
        domain = urlparse(article['link']).netloc
        sentiment = TextBlob(description).sentiment.polarity
        
        processed_articles.append({
            'date': date,
            'domain': domain,
            'category': category,
            'country': country,
            'title': article.get("title", "N/A"),
            'description': description,
            'link': article['link'],
            'sentiment': sentiment
        })
    
    # Sort articles by date (most recent first)
    #processed_articles.sort(key=lambda x: x['date'] or "0000-01-01", reverse=True)
    return processed_articles

def storing_data(articles, file_name = "news_data.xlsx"):
    if os.path.exists(file_name):
        df_existing = pd.read_excel(file_name, engine='openpyxl')
        df_new = pd.DataFrame(articles)
        df_combine = pd.concat([df_existing, df_new], ignore_index=True)
        df_combine.to_excel(file_name, index= False, engine='openpyxl')
        print(f"Data has been appeneded to {file_name}.")
    else:
        df = pd.DataFrame(articles)
        df.to_excel(file_name, index = False, engine='openpyxl')
        print(f"Data has been saved to {file_name}.")

def fetching_data():
    try:
        raw_articles = retrieving_data()
        articles = preprocess_articles(raw_articles)
        storing_data(articles)
        for article in articles:
            print(f"Date: {article['date']}\nDescription: {article['description']}\nCategory: {article['category']}\nCountry: {article['country']}\nTitle: {article['title']}\nLink: {article['link']}\nDomain: {article['domain']}\nSentiment: {article['sentiment']:.2f}\n")
    except Exception as e:
        print(f"Error: {e}")

# Schedule the task to run every 30 minutes
schedule.every(2).minutes.do(fetching_data)

# Keep the code running
while(True):
    schedule.run_pending()
    time.sleep(60)



