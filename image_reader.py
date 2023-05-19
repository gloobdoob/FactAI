import easyocr
import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
import os

class ImageReader:
    def __init__(self):

        self.reader = easyocr.Reader(['en', 'tl'], recog_network='english_g2', gpu=True)

    # Extracts text from the image using a library called easyocr
    def read_img(self, img):

        result = self.reader.readtext(img, detail = 1, paragraph=True)

        if type(img) == str:
            img = Image.open(img)
            img_arr = np.array(img)
        else:
            img_arr = img

        spacer = 100
        font = cv2.FONT_HERSHEY_SIMPLEX
        for detection in result:
            top_left = tuple(detection[0][0])
            bottom_right = tuple(detection[0][2])
            text = detection[1]
            img = cv2.rectangle(img_arr ,top_left,bottom_right,(0,255,0),3)
            img = cv2.putText(img_arr ,text,(20,spacer), font, 0.5,(0,255,0),2,cv2.LINE_AA)
            spacer+=15
        #plt.ion()
        # plt.imshow(img_arr)
        # plt.show()
        #plt.pause(0.001)
        # print('image shown')
        message = [row[1] for row in result]
        message = ' '.join(message)
        print('text extracted')
        return message




