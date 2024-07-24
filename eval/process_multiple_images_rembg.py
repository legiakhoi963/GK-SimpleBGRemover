import os
import shutil
from rembg import remove
from PIL import Image

def create_folders_if_not_exist():
    folders = ['mask_mediapipe', 'mask_rembg', 'original_image', 'subject']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

def process_multiple_images_rembg(source_path):
    create_folders_if_not_exist()
    for image_file in os.listdir(source_path):
        image_file_path = os.path.join(source_path, image_file)

        # original_image_path = os.path.join('original_image', image_file)
        # shutil.copy2(image_file_path, original_image_path)

        subject_path = os.path.join('subject', image_file)
        with open(subject_path, 'wb') as f:
            input = open(image_file_path, 'rb').read()
            subject = remove(input)
            f.write(subject)

        image = Image.open(subject_path)
        width, height = image.size

        for x in range(width):
            for y in range(height):
                r, g, b, a = image.getpixel((x, y))
                image.putpixel((x, y), (255, 255, 255, a))

        new_image = Image.new('RGBA', image.size, (0, 0, 0, 255))
        new_image.paste(image, (0, 0), image)
        new_image.save("mask_rembg/" + image_file)

process_multiple_images_rembg("D:\ProjectsAndCodes\GK-RemoveBG-API\original_image")