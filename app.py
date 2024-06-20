from flask import Flask, render_template, request, jsonify, flash
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

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

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

@app.route('/')
def home():
    return render_template('home.html', services=SERVICES, slogan='quote')

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
