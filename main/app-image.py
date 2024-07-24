import streamlit
import os
import urllib.request
from PIL import Image
from rembg import remove

# set full screen
streamlit.set_page_config(layout="wide")
streamlit.title("Image Background Removal and Replacement")
streamlit.write("Image Background Removal and Replacement")

# create directories
os.makedirs("original", exist_ok = True)
os.makedirs("background", exist_ok = True)
os.makedirs("masked", exist_ok = True)
os.makedirs("result", exist_ok = True)

# create checkbox
use_local_image = streamlit.checkbox("Use Local Image", value=False)
cols = streamlit.columns(2)

if use_local_image:
    subject_file = cols[0].file_uploader("Choose Subject Image", type=["jpg", 'png', 'jpeg'], key='subject')
    background_file = cols[1].file_uploader("Choose Background Image", type=["jpg", 'png', 'jpeg'], key='background')

    subject_name = subject_file.name
    subject_file = os.path.join('original', subject_name)
    
    background_name = background_file.name
    background_file = os.path.join('background', background_name)

else:
    subject_url = cols[0].text_input("Enter Subject Image URL", "https://upload.wikimedia.org/wikipedia/commons/6/68/Eurasian_wolf_2.jpg")
    background_url = cols[1].text_input("Enter Background Image URL", "https://upload.wikimedia.org/wikipedia/commons/a/a1/Nachusa_Grasslands_Spring_2016.jpg")

    subject_name = subject_url.split('/')[-1]
    background_name = background_url.split('/')[-1]

    urllib.request.urlretrieve(subject_url, "original/" + subject_name)
    urllib.request.urlretrieve(background_url, "background/" + background_name)

    subject_file = os.path.join('original', subject_name)
    background_file = os.path.join('background', background_name)

# Preview the image files
subject_img = Image.open(subject_file)
cols[0].image(subject_img, caption='Subject Image', use_column_width=True)
background_img = Image.open(background_file)
cols[1].image(background_img, caption='Background Image', use_column_width=True)

streamlit.title("Removing and Replacing Background from Subject Image")
cols = streamlit.columns(2)

# Remove and replace the background of the subject image
output_file = "masked/" + subject_name
with open(output_file, 'wb') as f:
  input = open("original/" + subject_name, 'rb').read()
  subject = remove(input)
  f.write(subject)

subject_img = Image.open(output_file)
background_img = Image.open(background_file)

background_img = background_img.resize(subject_img.size)

background_img.paste(subject_img, (0,0), subject_img)
background_img.save('result/result.jpeg', format='jpeg')

# Display the masked image
cols[0].image(output_file, caption="Subject Image without Background", use_column_width=True)

# Display the masked image with the new background
cols[1].image('result/result.jpeg', caption='Merged Image', use_column_width=True)