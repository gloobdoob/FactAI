from flask import Flask, render_template, jsonify, request
from main import text_extractor, predict_headline

import numpy as np
import cv2
import csv

import time
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/Report")
def report():
    return render_template('report.html')

@app.route("/About")
def about():
    return render_template('about.html')

@app.route("/predict", methods=['POST'])
def predict():
    # check if image file is uploaded
    if 'imagefile' in request.files and request.files['imagefile'].filename != '':
        # gets image file name from request
        print('imagefile' in request.files)
        imagefile = request.files['imagefile'].read()
        # converts file object to bytes
        imgbytes = np.fromstring(imagefile, np.uint8)
        # converts bytes to image
        img = cv2.imdecode(imgbytes, cv2.IMREAD_COLOR)
        imageRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        headline, image_pred = text_extractor(imageRGB)
        result = predict_headline(headline, image_pred)
        return jsonify({'result': result})
    else:
        # check if input text is entered

        headline = request.form.get('headline-input')
        # check if both image and input text are empty
        if headline:
            result = predict_headline(headline)
            return jsonify({'result': result})

        else:
            return jsonify({'error': 'Please upload an image or enter text'})

    # perform processing on the input


    # outputs result in output_display div


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
    <style>
    function fireSweetAlert() {
                    Swal.fire({
                        title: 'Report Submitted',
                        text: 'Your report has been submitted successfully.',
                        icon: 'success',
                })
                }
    </script>
    """


if __name__ == '__main__':
    app.run(debug=False)
