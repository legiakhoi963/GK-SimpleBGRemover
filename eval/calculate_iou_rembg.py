import numpy as np
import os
from PIL import Image

def load_image_as_numpy_array(image_path):
  image = Image.open(image_path)
  if image.mode == 'RGBA':
    image = image.convert('RGB')
  return np.array(image)

def calculate_iou(target, prediction):
  intersection = np.logical_and(target, prediction)
  union = np.logical_or(target, prediction)
  iou_score = np.sum(intersection) / np.sum(union)
  return iou_score

def calculate_average_iou(target_folder, prediction_folder):
  iou_scores = []
  for filename in os.listdir(target_folder):
    target_path = os.path.join(target_folder, filename)
    prediction_path = os.path.join(prediction_folder, filename)
    if os.path.exists(prediction_path):
      target = load_image_as_numpy_array(target_path)
      prediction = load_image_as_numpy_array(prediction_path)
      iou_score = calculate_iou(target, prediction)
      iou_scores.append(iou_score)
  
  if iou_scores:
    average_iou = np.mean(iou_scores)
    return average_iou
  else:
    return None

target_folder = 'D:\ProjectsAndCodes\GK-RemoveBG-API\mask_groundtruth'
prediction_folder = 'D:\ProjectsAndCodes\GK-RemoveBG-API\mask_rembg'
average_iou = calculate_average_iou(target_folder, prediction_folder)

if average_iou is not None:
  print("Average Rembg IoU score:", average_iou)
else:
  print("No matching files found in target and prediction folders.")