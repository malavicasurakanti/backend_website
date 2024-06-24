from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import graphene
from graphene import ObjectType, String, Schema, Int, List
from flask_graphql import GraphQLView
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Configure email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Hygraph Endpoint and API Token
HYGRAPH_API_URL = os.getenv('HYGRAPH_API')
HYGRAPH_API_TOKEN = os.getenv('HYGRAPH_AUTH_TOKEN')

# Debugging statements
print(f"HYGRAPH_API_URL: {HYGRAPH_API_URL}")
print(f"HYGRAPH_API_TOKEN: {HYGRAPH_API_TOKEN}")

# Verify that the environment variables are loaded correctly
assert HYGRAPH_API_URL is not None, "HYGRAPH_API_URL environment variable not set"
assert HYGRAPH_API_TOKEN is not None, "HYGRAPH_API_TOKEN environment variable not set"

# Define GraphQL Schema for Articles, Templates, and Project Ideas
class ArticleType(ObjectType):
    id = Int()
    title = String()
    content = String()
    imageUrl = String()

class TemplateType(ObjectType):
    id = Int()
    title = String()
    content = String()
    imageUrl = String()

class ProjectIdeaType(ObjectType):
    id = Int()
    title = String()
    content = String()
    imageUrl = String()

class Query(ObjectType):
    articles = List(ArticleType)
    templates = List(TemplateType)
    project_ideas = List(ProjectIdeaType)

    def resolve_articles(root, info):
        headers = {
            'Authorization': f'Bearer {HYGRAPH_API_TOKEN}'
        }
        query = """
        {
          articles{
            id
            title
            content
            imageUrl
          }
        }
        """
        response = requests.post(HYGRAPH_API_URL, json={'query': query}, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
        data = response.json()
        if 'errors' in data:
            print(f"GraphQL errors: {data['errors']}")
        else:
            
            articles= data.get('data', {}).get('article', [])
            return [ArticleType(id=article['id'], title=article['title'], content=article['content'], imageUrl=article['imageUrl']) for article in articles]

def resolve_templates(root, info):
        headers = {
            'Authorization': f'Bearer {HYGRAPH_API_TOKEN}'
        }
        query = """
        {
          templates {
            id
            title
            content
            imageUrl
          }
        }
        """
        response = requests.post(HYGRAPH_API_URL, json={'query': query}, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
        data = response.json()
        if 'errors' in data:
            print(f"GraphQL errors: {data['errors']}")
        else:
            templates = data.get('data', {}).get('templates', [])
            return [TemplateType(id=template['id'], title=template['title'], content=template['content'], imageUrl=template['imageUrl']) for template in templates]

def resolve_project_ideas(root, info):
        headers = {
            'Authorization': f'Bearer {HYGRAPH_API_TOKEN}'
        }
        query = """
        {
          projectIdea {
            id
            title
            content
            imageUrl
          }
        }
        """
        response = requests.post(HYGRAPH_API_URL, json={'query': query}, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")
        data = response.json()
        if 'errors' in data:
            print(f"GraphQL errors: {data['errors']}")
        else:
            project_ideas = data.get('data', {}).get('projectIdeas', [])
            return [ProjectIdeaType(id=idea['id'], title=idea['title'], content=idea['content'], imageUrl=idea['imageUrl']) for idea in project_ideas]

schema = Schema(query=Query)

@app.route('/')
def home():
    headers = {
        'Authorization': f'Bearer {HYGRAPH_API_TOKEN}'
    }
    query = """
    {
      articles {
        id
        title
        content
        imageUrl
      }
      templates {
        id
        title
        content
        imageUrl
      }
      projectIdeas {
        id
        title
        content
        imageUrl
      }
    }
    """
    response = requests.post(HYGRAPH_API_URL, json={'query': query}, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")
    data = response.json()
    if 'errors' in data:
        print(f"GraphQL errors: {data['errors']}")
        flash("Error fetching data from Hygraph", 'danger')
        return render_template('home.html', articles=[], templates=[], project_ideas=[], services=[])

    articles = data.get('data', {}).get('articles', [])
    templates = data.get('data', {}).get('templates', [])
    project_ideas = data.get('data', {}).get('projectIdeas', [])

    # Combine all services into one list
    services = [
        {'id': article['id'], 'title': article['title'], 'imageUrl': article['imageUrl'], 'type': 'article'} for article in articles
    ] + [
        {'id': template['id'], 'title': template['title'], 'imageUrl': template['imageUrl'], 'type': 'template'} for template in templates
    ] + [
        {'id': project_idea['id'], 'title': project_idea['title'], 'imageUrl': project_idea['imageUrl'], 'type': 'projectIdea'} for project_idea in project_ideas
    ]

    # Debugging: print the data structures
    print("Articles: ", articles)
    print("Templates: ", templates)
    print("Project Ideas: ", project_ideas)
    print("Services: ", services)

    return render_template('home.html', articles=articles, templates=templates, project_ideas=project_ideas, services=services)



@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    msg = Message('New Subscription', recipients=['malavica.surakanti@gmail.com'])
    msg.body = f'New subscription from: {email}'
    try:
        mail.send(msg)
        flash('Thank you for subscribing!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('home'))

@app.route("/service/<string:service_type>/<int:service_id>")
def service(service_type, service_id):
    headers = {
        'Authorization': f'Bearer {HYGRAPH_API_TOKEN}'
    }
    query = f"""
    {{
      {service_type}(where: {{id: {service_id}}}) {{
        id
        title
        content
        imageUrl
      }}
    }}
    """
    response = requests.post(HYGRAPH_API_URL, json={'query': query}, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")
    data = response.json()
    if 'errors' in data:
        print(f"GraphQL errors: {data['errors']}")
        return "Service not found", 404
    service = data.get('data', {}).get(service_type, None)
    if service:
        return render_template('service.html', service=service)
    else:
        return "Service not found", 404

# Add GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable the GraphiQL interface
    )
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
