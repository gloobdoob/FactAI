import torch.nn.functional as F
from torchvision import transforms as T
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import torch
from torch import nn


class ImagePredictor:
    def __init__(self, img_size=224):
        self.IMAGENET_MEAN = 0.485, 0.456, 0.406
        self.IMAGENET_STD = 0.229, 0.224, 0.225
        self.IMG_SIZE = img_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = torch.hub.load('ultralytics/yolov5', 'custom', 'classifiers/image_classifier/static/best.pt', force_reload=True)

    def classify_transforms(self):
        return T.Compose([T.ToTensor(), T.Resize(self.IMG_SIZE), T.CenterCrop(self.IMG_SIZE),
                          T.Normalize(self.IMAGENET_MEAN, self.IMAGENET_STD)])

    def preprocess_img(self, img):
        filter = ImageEnhance.Color(img)
        new_image = filter.enhance(1.2)
        filter = ImageEnhance.Contrast(new_image)
        new_image = filter.enhance(2)
        filter = ImageEnhance.Sharpness(new_image)
        new_image = filter.enhance(2)
        return new_image

    def predict_img(self, img):
        img = Image.fromarray(img).convert('RGB')
        img = self.preprocess_img(img)
        transformations = self.classify_transforms()
        convert_tensor = transformations(img)
        convert_tensor = convert_tensor.unsqueeze(0)
        convert_tensor = convert_tensor.to(self.device)

        results = self.model(convert_tensor)

        pred = F.softmax(results, dim=1)
        #top5i = None

        # for i, prob in enumerate(pred):
        #     top5i = prob.argsort(0, descending=True)[:5].tolist()
        #    # text = '\n'.join(f'{prob[j]:.2f} {self.model.names[j]}' for j in top5i)

        return {'fake': pred[0][0].item(), 'real': pred[0][1].item()}


