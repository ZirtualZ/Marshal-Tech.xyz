import os
import requests
from datetime import datetime
from flask import Flask, render_template, request, Response, send_from_directory
from werkzeug.utils import secure_filename

# Import the stats_api blueprint from api.stats
from api.stats import stats_api

# --- Configuration ---
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 * 1024  # 20GB

# Path to the folder where you will manually place your files
FILES_DIRECTORY = os.path.join(app.root_path, 'files')

# Create the 'files' folder automatically if it doesn't exist
if not os.path.exists(FILES_DIRECTORY):
    os.makedirs(FILES_DIRECTORY)

# --- File Serving Route ---
@app.route('/files/<path:filename>')
def serve_custom_files(filename):
    return send_from_directory(FILES_DIRECTORY, filename)

# --- Page Routes ---
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
    # List all files in the configured FILES_DIRECTORY
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

# Register the stats_api blueprint for /api/stats
app.register_blueprint(stats_api)

if __name__ == '__main__':
    # Running on port 8081 as per your original code
    app.run(host='0.0.0.0', port=8081, debug=False)
