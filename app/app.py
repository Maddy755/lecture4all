#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@app.py
"""

from flask import Flask, render_template, request, jsonify, session, Response
import requests
import os
import json
#import time
from datetime import timedelta

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

# # ─── Record start time for every incoming request ───────────────────────────────
# @app.before_request
# def start_timer():
#     g.request_start = time.perf_counter()
#     # optional: generate a request ID if you want to correlate logs downstream
#     g.request_id = f"{int(g.request_start * 1e6)}"

# # ─── After each request, log the total elapsed time ─────────────────────────────
# @app.after_request
# def log_request(response):
#     elapsed_ms = (time.perf_counter() - g.request_start) * 1000
#     app.logger.info(
#         f"[req={g.request_id}] {request.method} {request.path} "
#         f"status={response.status_code} elapsed_ms={elapsed_ms:.2f}"
#     )
#     # expose timing to clients if useful
#     response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.2f}"
#     return response

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/index')
def index():
    return render_template('index.html')
    

def post_to_db(query):
    db_env_url = 'http://db-env:7001/app/process_query'
    response = requests.post(db_env_url, json={'query': query})
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

@app.route('/shorts')
def shorts():
    query = request.args.get('query')
    json_data, status_code = handle_query(query)
    if status_code != 200:
        return render_template('error.html', error_info=json_data), status_code
    return render_template('shorts.html', query=query, video_results=json_data['videos'], result_count=len(json_data['videos']))

@app.route('/searchresults', methods=['GET'])
def searchresults():
    query = request.args.get('query')
    json_data, status_code = handle_query(query)
    if status_code != 200:
        return render_template('error.html', error_info=json_data), status_code
    return render_template('searchresults.html', query=query, video_results=json_data['videos'], result_count=len(json_data['videos']))

@app.route('/video')
def video():
    video_id = request.args.get('video_id')
    return render_template('video.html', video_id=video_id)

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/convert_srt_to_vtt')
def convert_srt_to_vtt():
    srt_path = request.args.get('srt_path')  # z. B. '/transcription/subtitles/19550_subtitles.srt'
    
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        # Konvertiere SRT zu VTT
        vtt_content = "WEBVTT\n\n" + srt_content.replace(',', '.')
        
        # Sende als VTT-Datei zurück
        return Response(
            vtt_content,
            mimetype='text/vtt',
            headers={'Content-Disposition': 'inline'}
        )
    except Exception as e:
        return str(e), 404

print('starting...')