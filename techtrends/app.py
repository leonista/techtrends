import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from datetime import datetime
import sys

connect_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connect_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connect_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      log_m('Article with ID=="{id}" DOES NOT EXIST!'.format(id=post_id), 1)
      return render_template('404.html'), 404
    else:
      log_m('Article with Title="{title}" Successfully Retrieved!'.format(title=post['title']), 0)
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    log_m('About Page Retrieved!', 0)
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            log_m('New Article with TITLE="{title}", Created!'.format(title=title), 0)

            return redirect(url_for('index'))

    return render_template('create.html')

# Log controller
def log_m(msg, input):
    if input == 0:
        app.logger.info(
            '{time} | {message}'.format( time=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), message=msg))
        sys.stdout.write(
            '{time} | {message} \n'.format( time=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), message=msg))
        
    if input == 1:
        app.logger.error(
            '{time} | {message}'.format( time=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), message=msg))
        sys.stderr.write(
            '{time} | {message} \n'.format( time=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), message=msg))
        
        
        


# Define the /healthz endpoint 
@app.route('/healthz')
def healthz():
    connection = get_db_connection()
    connection.cursor()
    connection.execute("SELECT * FROM posts")
    connection.close()
    results = {"result": "Ok - healthy", "HTTP / 1": 200 }
    return results


# Define /metrics endpoint 
@app.route("/metrics")
def metrics():
    try:
        connection = get_db_connection()
        posts = connection.execute("SELECT * FROM posts").fetchall()
        connection.close()
        posts_count = len(posts)
        status_c = 200
        addition = {"post_count": posts_count, "db_connection_count": connect_count}
        results = {"responce": addition, "HTTP / 1": status_c}
        return results

    except Exception:       
        return {"result": "ERROR -"}, 500


# start the application on port 3111
if __name__ == "__main__":

    ## set log level 
    logging.basicConfig(level=logging.DEBUG)

    app.run(host='0.0.0.0', port='3111')
