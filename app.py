import sitecustomize
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

# Mail configuration
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

def fetch_data(query):
    response = requests.post(
        HYGRAPH_API_URL,
        json={'query': query},
        headers={'Authorization': f'Bearer {HYGRAPH_API_TOKEN}'}
    )
    return response.json()

class PostType(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    content = graphene.String()
    author = graphene.String()

class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)

    def resolve_all_posts(root, info):
        query = """
        {
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
        data = fetch_data(query)
        posts = data['data']['posts']
        return [PostType(
            id=post['id'],
            title=post['title'],
            content=post['content'],
            author=post['author']['name']
        ) for post in posts]

schema = graphene.Schema(query=Query)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/blog')
def blog():
    query = """
    {
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
    except requests.exceptions.RequestException as e:
        return render_template('blog.html', error="Error connecting to Hygraph API.")

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
        if 'data' in data and 'post' in data['data']:
            article = data['data']['post']
            return render_template('article.html', article=article)
    except requests.exceptions.RequestException as e:
        return render_template('article.html', error="Error connecting to Hygraph API.")

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable GraphiQL interface
    )
)

if __name__ == '__main__':
    app.run(debug=True)
