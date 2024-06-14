from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

SERVICES = [
    {
        'id': 1,
        'title': 'Articles',
        'content': 'This is the content of the article'
    },
    {
        'id': 2,
        'title': 'Automation templates',
        'content': 'This is the content of the templates'
    },
    {
        'id': 3,
        'title': 'Portfolio ideas',
        'content': 'This is the content of the ideas'
    },
]

@app.route('/')
def home():
    return render_template('home.html', services=SERVICES, slogan='quote')

@app.route('/owner')
def owner():
    return render_template('owner.html')

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json
    title = data['title']
    tags = data['tags']
    content = data['content']
    return jsonify({"message": "Article received successfully"}), 200

@app.route("/api/services")
def list_services():
    return jsonify(SERVICES)

@app.route("/articles/<int:article_id>")
def article(article_id):
    article = next((item for item in SERVICES if item['id'] == article_id), None)
    if article:
        return render_template('article.html', article=article)
    else:
        return "Article not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
