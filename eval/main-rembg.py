import cv2
import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from rembg import remove
from PIL import Image

app = FastAPI()

def create_folders_if_not_exist():
    folders = ['frame', 'original_image', 'original_video', 'result', 'subject']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

@app.post("/process_image")
async def process_image(image_file: UploadFile = File(...)):
    create_folders_if_not_exist()

    original_image_path = os.path.join('original_image', image_file.filename)
    with open(original_image_path, "wb") as f:
        f.write(image_file.file.read())

    subject_path = os.path.join('subject', image_file.filename)
    with open(subject_path, 'wb') as f:
        input = open(original_image_path, 'rb').read()
        subject = remove(input)
        f.write(subject)

    subject_img = Image.open(subject_path)
    background_img = Image.open("white.jpg")
    background_img = background_img.resize(subject_img.size)
    background_img.paste(subject_img, (0,0), subject_img)
    background_img.save("result/" + image_file.filename, format='jpeg')

    return JSONResponse(content={"message": f"Image processed", "filename": image_file.filename})
    
@app.post("/process_frame_from_video")
async def process_frame_from_video(video_file: UploadFile = File(...)):
    create_folders_if_not_exist()
    try:
        original_video_path = os.path.join('original_video', video_file.filename)
        with open(original_video_path, "wb") as f:
            f.write(video_file.file.read())

        capture = cv2.VideoCapture(original_video_path)
        frame_count = 0

        while True:
            success, frame = capture.read()
            if not success:
                break
            frame_count += 1
            frame_path = os.path.join('frame', video_file.filename + f"_frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, frame)

            subject_path = os.path.join('subject', video_file.filename + f"_frame_{frame_count}.jpg")
            with open(subject_path, 'wb') as f:
                input = open(frame_path, 'rb').read()
                subject = remove(input)
                f.write(subject)

            subject_img = Image.open(subject_path)
            background_img = Image.open("white.jpg")
            background_img = background_img.resize(subject_img.size)
            background_img.paste(subject_img, (0,0), subject_img)
            background_img.save("result/" + video_file.filename + f"_frame_{frame_count}.jpg", format='jpeg')
        capture.release()
 
        return JSONResponse(content={"message": f"Frames processed", "filename": video_file.filename, "frame_count": frame_count})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)