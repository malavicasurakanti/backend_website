from flask import Flask, render_template, request, jsonify, flash
from flask_mail import Mail, Message
import graphene
from graphene import ObjectType, String, Schema, Int, List
from flask_graphql import GraphQLView
import requests
import os
from dotenv import load_dotenv

load_dotenv() 
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)
# Hygraph Endpoint and API Token
HYGRAPH_API_URL = os.getenv('HYGRAPH_API')
HYGRAPH_API_TOKEN = os.getenv('HYGRAPH_AUTH_TOKEN')


from flask import Flask, render_template, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

HYGRAPH_API_URL = os.getenv('HYGRAPH_API')
HYGRAPH_API_TOKEN = os.getenv('HYGRAPH_AUTH_TOKEN')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/blog')
def blog():
    query = """
    query {
        posts {
            id
            title
            content
            author {
                name
            }
        }
    }
    """
    try:
        response = requests.post(HYGRAPH_API_URL, json={'query': query}, headers={'Authorization': f'Bearer {HYGRAPH_API_TOKEN}'})
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        if 'data' in data:
            return render_template('blog.html', posts=data['data']['posts'])
        else:
            print("Error: Unexpected response structure:", data)
            return render_template('blog.html', error="Error fetching blog posts data.")
    except requests.exceptions.RequestException as e:
        print("Error connecting to Hygraph API:", e)
        return render_template('blog.html', error="Error connecting to Hygraph API. Please check your network connection and API settings.")

@app.route('/article/<int:article_id>')
def article(article_id):
    query = """
    query($id: ID!) {
        post(where: { id: $id }) {
            title
            content
            author {
                name
            }
        }
    }
    """
    variables = {'id': article_id}
    try:
        response = requests.post(HYGRAPH_API_URL, json={'query': query, 'variables': variables}, headers={'Authorization': f'Bearer {HYGRAPH_API_TOKEN}'})
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        print("Response from Hygraph:", data)  # Print the response for debugging
        if 'data' in data and 'post' in data['data']:
            article = data['data']['post']
            return render_template('article.html', article=article)
        else:
            print("Error: Unexpected response structure:", data)
            return render_template('article.html', error="Article not found or API response error.")
    except requests.exceptions.RequestException as e:
        print("Error connecting to Hygraph API:", e)
        return render_template('article.html', error="Error connecting to Hygraph API. Please check your network connection and API settings.")

if __name__ == '__main__':
    if not HYGRAPH_API_URL or not HYGRAPH_API_TOKEN:
        print("Error: HYGRAPH_API and HYGRAPH_AUTH_TOKEN environment variables are not set.")
    else:
        print(f"HYGRAPH_API: {HYGRAPH_API_URL}")
        print(f"HYGRAPH_AUTH_TOKEN: {HYGRAPH_API_TOKEN}")
    app.run(debug=True)


