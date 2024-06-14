from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Hygraph configuration
HYGRAPH_ENDPOINT = os.getenv('HYGRAPH_ENDPOINT')
HYGRAPH_TOKEN = os.getenv('HYGRAPH_TOKEN')

def fetch_data_from_hygraph(query):
    headers = {
        'Authorization': f'Bearer {HYGRAPH_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.post(HYGRAPH_ENDPOINT, headers=headers, json={'query': query})
    response.raise_for_status()
    data = response.json()
    return data['data']

def fetch_all_data_from_hygraph():
    query = """
    query MyQuery {
      articles {
        id
        articleTitle: article_title
        contentMain: content_main
        author
        published
        tags
        image {
          url
        }
        createdAt
        createdBy
        updatedAt
        updatedBy
      }
      automatedTemplates {
        id
        title
        description
        author
        published
        tags
        image {
          url
        }
        createdAt
        createdBy
        updatedAt
        updatedBy
      }
      portfolioIdeas {
        id
        title
        description
        author
        publishedDate: published_date
        tags
        image {
          url
        }
        createdAt
        createdBy
        updatedAt
        updatedBy
      }
    }
    """
    return fetch_data_from_hygraph(query)

@app.route('/')
def home():
    try:
        data = fetch_all_data_from_hygraph()
        articles = data['articles']
        templates = data['automatedTemplates']
        portfolio_ideas = data['portfolioIdeas']
    except requests.HTTPError as e:
        return jsonify({'error': str(e)}), 500

    return render_template('home.html', articles=articles, templates=templates, portfolio_ideas=portfolio_ideas, slogan='quote')


@app.route('/publish', methods=['POST'])
def publish():
data = request.json
title = data.get('title')
tags = data.get('tags')
content = data.get('content')
if not title or not tags or not content:
return jsonify({"error": "Missing data"}), 400

    
try:
        result = publish_article_to_hygraph(title, tags, content)
return jsonify({"message": "Article received successfully", "result": result}), 200
except requests.HTTPError as e:
return jsonify({'error': str(e)}), 500

@app.route("/api/articles")
def list_articles():
    try:
        data = fetch_all_data_from_hygraph()
        articles = data['articles']
    except requests.HTTPError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(articles)

@app.route("/api/templates")
def list_templates():
    try:
        data = fetch_all_data_from_hygraph()
        templates = data['automatedTemplates']
    except requests.HTTPError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(templates)

@app.route("/api/portfolio-ideas")
def list_portfolio_ideas():
    try:
        data = fetch_all_data_from_hygraph()
        portfolio_ideas = data['portfolioIdeas']
    except requests.HTTPError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(portfolio_ideas)

@app.route("/articles/<int:article_id>")
def article(article_id):
    try:
        data = fetch_all_data_from_hygraph()
        articles = data['articles']
    except requests.HTTPError as e:
        return jsonify({'error': str(e)}), 500

    article = next((item for item in articles if item['id'] == article_id), None)
    if article:
        return render_template('article.html', article=article)
    else:
        return "Article not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)