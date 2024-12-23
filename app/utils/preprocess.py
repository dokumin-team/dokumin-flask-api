import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def preprocess_image(image_file):
    img = cv2.imread(image_file)
    img = cv2.resize(img, (256, 256))
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)
    return img