import os
import shutil
import numpy as np
import mediapipe as mp
from PIL import Image
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path='selfie_segmenter.tflite')
options = vision.ImageSegmenterOptions(base_options=base_options, output_category_mask=True)

def create_folders_if_not_exist():
    folders = ['mask_mediapipe', 'mask_rembg', 'original_image', 'subject']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

def process_multiple_images_mediapipe(source_path):
    create_folders_if_not_exist()
    for image_file in os.listdir(source_path):
        image_file_path = os.path.join(source_path, image_file)

        # original_image_path = os.path.join('original_image', image_file)
        # shutil.copy2(image_file_path, original_image_path)

        with vision.ImageSegmenter.create_from_options(options) as segmenter:
            image = mp.Image.create_from_file(image_file_path)

            segmentation_result = segmenter.segment(image)
            category_mask = segmentation_result.category_mask

            image_data = image.numpy_view()
            fg_image = np.zeros(image_data.shape, dtype=np.uint8)
            fg_image[:] = (255, 255, 255)
            bg_image = np.zeros(image_data.shape, dtype=np.uint8)
            bg_image[:] = (0, 0, 0)

            condition = np.stack((category_mask.numpy_view(),) * 3, axis=-1) > 0.3
            output_image = np.where(condition, bg_image, fg_image)

            image = Image.fromarray(output_image)
            image.save("mask_mediapipe/" + image_file)

process_multiple_images_mediapipe("D:\ProjectsAndCodes\GK-RemoveBG-API\original_image")