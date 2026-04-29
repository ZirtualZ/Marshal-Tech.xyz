import os
import requests
from datetime import datetime
from flask import Flask, render_template, request, Response, send_from_directory
from werkzeug.utils import secure_filename
from api.stats import stats_api

# --- Config ---
app = Flask(__name__)

# File Serving Route(im not using it anymore.)
@app.route('/files/<path:filename>')
def serve_custom_files(filename):
    return send_from_directory(FILES_DIRECTORY, filename

# Page Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/discord-server')
def discord():
    return render_template('discord.html')

@app.route('/files')
def files():
    file_list = os.listdir(FILES_DIRECTORY)
    return render_template('files.html', files=file_list)
  

@app.route('/labs')
def labs():
    return render_template('labs.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logs')
def logs():
    files = os.listdir(FILES_DIRECTORY)
    return render_template('logs.html', files=files)

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/bot')
def bot():
    return render_template('bot.html')

@app.route('/vnc')
def vnc():
    return render_template('vnc.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/comments')
def comments():
    return render_template('comments.html')

app.register_blueprint(stats_api)
# had something on 8080 so 8081 is what i have left lmao
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
