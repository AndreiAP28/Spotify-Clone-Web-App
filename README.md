# Spotify Clone Web App

### Video Demo: [video link](https://youtu.be/egpaVRjTlCw)

## Project Description
This project is a web application designed to mimic the functionality and user experience of Spotify. Utilizing API requests, it fetches data from the Spotify API to replicate features like searching for songs, creating playlists, and browsing artists.

## Purpose of project
The primary aim of this project is to provide a platform for practicing and honing skills in handling data extracted from APIs. It serves as a playground for developers to learn and experiment with API integration, data manipulation, and data visualization.

Additionally, this project serves as a comprehensive exercise in web development, encompassing everything from frontend design to backend functionality. It offers an opportunity to delve into the creation of a fully-fledged web application, incorporating elements such as animations, transitions, and other interactive features to enhance the user experience.

## Project Structure (files):

- static
    - css
        1. style.css
    - js
        1. auto-logout.js
        2. play-btn.js
        3. playsong.js
        4. see-all-items.js
        5. show-objectprofile.js
        
- templates
    1. home.html
    2. index.html
    3. layout.html
    4. objectprofile.html
    5. see_all.html
    6. userprofile.html
- .env
- app.py
- README.md
- requirements.txt

## App's Features
- Vizualize your recently played songs/albums/playlists
- View artist profiles
- View user profile
- Explore your top artists/songs all time chart
- Play, pause, skip and control playback
- Explore recommendations based on listening history
- View playlist/album's content

## Technologies Used

- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask)
- API Integration: Spotify API
- UI/UX Enhancement: Various libraries and frameworks such as Bootstrap

## About Libraries

_**DOTENV**_: is a Python module that allows you to load environment variables from a .env file into os.environ. It simplifies managing environment variables for your Python projects, especially in development environments, by providing a convenient way to keep sensitive or environment-specific configuration separate from your codebase.

([Read more](https://pypi.org/project/python-dotenv/))

_**FLASK**_: is a lightweight web framework for Python. It provides tools, libraries, and technologies to help build web applications quickly and efficiently. Flask is known for its simplicity and flexibility, making it an excellent choice for developing small to medium-sized web applications, APIs, or prototypes.([Read more](https://pypi.org/project/Flask//))

_**FLASK-SESSION**_: is a Flask extension that adds support for server-side sessions to your Flask applications. It provides an easy way to store user session data on the server, which can be accessed and modified throughout the user's interaction with your application. Flask-Session supports different session backends, including Redis, Memcached, and filesystem storage, allowing you to choose the best option for your use case.([Read more](https://pypi.org/project/Flask-Session/))

## Importing & Installing the Libraries

Before running the application, make sure you have the required dependencies installed. You can install them using pip:

```bash
pip install flask
```

```bash
pip install python-dotenv
```

```bash
pip install Flask-Session
```

Right after that the libaries are ready for being imported and used:

```python
from flask import Flask, flash, redirect, render_template, request, url_for, session, jsonify
from dotenv import load_dotenv
from flask_session import Session
from datetime import datetime, timedelta
import os
import requests
import json
import random
```

## Usage

```bash
python app.py
```


## Social Media

- **EdX**: AndreiAP_28
- **GitHub**: AndreiAP28
