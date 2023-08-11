from flask import Flask, render_template, jsonify, request
from main import text_extractor, predict_headline

import numpy as np
import cv2
import csv

import time
import os

app = Flask(__name__)

def get_search_links(result):
    # Placeholder implementation
    search_links = None
    if 'UNRELIABLE' in result:
        ("UNRELIABLE FOUND!!!!!!!!!!!!!!!")
        search_links = ['https://www.example.com/false-news']

    elif 'RELIABLE' in result:
        print("RELIABLE FOUND!!!!!!!!!!!!!!!")
        search_links = ['https://www.example.com/true-news']

    else:
        print("NOPE GOT NOTHING")
        search_links = []
    return search_links

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/Report")
def report():
    return render_template('report.html')

@app.route("/About")
def about():
    return render_template('about.html')

@app.route("/Fake")
def fake():
    return render_template('fake.html')

@app.route("/predict", methods=['POST'])
def predict():
    if 'imagefile' in request.files and request.files['imagefile'].filename != '':
        imagefile = request.files['imagefile'].read()
        imgbytes = np.fromstring(imagefile, np.uint8)
        img = cv2.imdecode(imgbytes, cv2.IMREAD_COLOR)
        imageRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        headline, image_pred = text_extractor(imageRGB)
        rating, result, search_links = predict_headline(headline, image_pred)

        image_src = None
        if 'UNRELIABLE' in result:
            image_src = 'static/images/unreliable.png'

        elif 'RELIABLE' in result:
            image_src = 'static/images/reliable.png'

        # Modify the following code to retrieve the appropriate links based on the prediction
        # Replace the placeholder function `get_search_links()` with your implementation
        #search_links_p = get_search_links(result)
        #print(f'supposed link output: {search_links}')
        return jsonify({'result': result, 'search_links': search_links, 'image_url': image_src})
    else:
        headline = request.form.get('headline-input')
        if headline:
            rating, result, search_links = predict_headline(headline)

            # Modify the following code to retrieve the appropriate links based on the prediction
            # Replace the placeholder function `get_search_links()` with your implementation
           # search_links_p = get_search_links(result)
            image_src = None
            if 'UNRELIABLE' in result:
                image_src = 'static/images/unreliable.png'

            elif 'RELIABLE' in result:
                image_src = 'static/images/reliable.png'

            #print(f'supposed link output: {search_links_p}')
            return jsonify({'result': result, 'search_links': search_links, 'image_url': image_src})
        else:
            return jsonify({'error': 'Please enter a headline'})

        
@app.route("/submitreport", methods=['POST'])
def submit_report():
    news_title = request.form.get('news-title')
    news_content = request.form.get('news-content')
    contact_email = request.form.get('contact-email')

    if not news_title or not news_content or not contact_email:
        return "Error: Missing form data"

    # Save the data to a CSV file
    with open('reports.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([news_title, news_content, contact_email])

    # Display a dialog box using SweetAlert with custom CSS styles
    return """
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11.0.17/dist/sweetalert2.min.js"></script>
    <script>
    Swal.fire({
        title: 'Report Submitted',
        text: 'Your report has been submitted successfully.',
        icon: 'success',
    });
    </script>
    """


if __name__ == '__main__':
    app.run(debug=True)