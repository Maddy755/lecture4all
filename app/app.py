#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@app.py
"""

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    Response,
    send_from_directory
)

import requests
import os
import json
from datetime import timedelta


app = Flask(__name__, template_folder='templates')

app.secret_key = 'secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)


# ============================================================
# Home / Index
# ============================================================

@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/index')
def index():
    return render_template('index.html')


# ============================================================
# Database / Search
# ============================================================

def post_to_db(query):
    db_env_url = 'http://db-env:7001/app/process_query'

    response = requests.post(
        db_env_url,
        json={'query': query}
    )

    return response


def handle_query(query):

    if not query:
        return {'error': 'No query provided'}, 400

    response = post_to_db(query)

    if response.status_code != 200:

        error_info = {
            'error': response.status_code,
            'status_code': response.status_code,
            'response_content': response.content.decode('utf-8')
        }

        return error_info, 500

    response = response.json()

    json_data = json.loads(response)

    return json_data, 200


# ============================================================
# Shorts
# ============================================================

@app.route('/shorts')
def shorts():

    query = request.args.get('query')

    json_data, status_code = handle_query(query)

    if status_code != 200:
        return render_template(
            'error.html',
            error_info=json_data
        ), status_code

    return render_template(
        'shorts.html',
        query=query,
        video_results=json_data['videos'],
        result_count=len(json_data['videos'])
    )


# ============================================================
# Search Results
# ============================================================

@app.route('/searchresults', methods=['GET'])
def searchresults():

    query = request.args.get('query')

    json_data, status_code = handle_query(query)

    if status_code != 200:
        return render_template(
            'error.html',
            error_info=json_data
        ), status_code

    return render_template(
        'searchresults.html',
        query=query,
        video_results=json_data['videos'],
        result_count=len(json_data['videos'])
    )


# ============================================================
# Video Page
# ============================================================

@app.route('/video')
def video():

    video_id = request.args.get('video_id')

    return render_template(
        'video.html',
        video_id=video_id
    )


# ============================================================
# LOCAL VIDEO FILE SERVING
# ============================================================

@app.route('/video-file/<path:filename>')
def video_file(filename):

    return send_from_directory(
        '/transcription/videos',
        filename
    )


# ============================================================
# Help
# ============================================================

@app.route('/help')
def help():

    return render_template('help.html')


# ============================================================
# About
# ============================================================

@app.route('/about')
def about():

    return render_template('about.html')


# ============================================================
# Convert SRT to VTT
# ============================================================

@app.route('/api/convert_srt_to_vtt')
def convert_srt_to_vtt():

    srt_path = request.args.get('srt_path')

    try:

        with open(
            srt_path,
            'r',
            encoding='utf-8'
        ) as f:

            srt_content = f.read()

        # Convert SRT timestamps to VTT format
        vtt_content = (
            "WEBVTT\n\n"
            + srt_content.replace(',', '.')
        )

        return Response(
            vtt_content,
            mimetype='text/vtt'
        )

    except Exception as e:

        return jsonify({
            'error': str(e)
        }), 500


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )