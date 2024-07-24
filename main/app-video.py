import tempfile
import cv2
import mediapipe as mp
import streamlit as st
import numpy as np
from PIL import Image

#demo video 
DEMO_VIDEO = 'video.mp4'
BG_IMAGE = 'background/Nachusa_Grasslands_Spring_2016.jpg'
BG_VIDEO = 'grass_land.mp4'
BG_COLOR = (200, 200, 200)

mp_selfie_segmentation = mp.solutions.selfie_segmentation

def main():

    #title
    st.title('Selfie Segmentation App')
    st.markdown(' ## Output')
    stframe = st.empty()

    #sidebar title and subheader
    st.sidebar.title('Segmentation App')
    st.sidebar.subheader('Parameters')

    #creating a button for webcam
    use_webcam = st.sidebar.button('Use Webcam')
    
    #model selection 
    model_display = ("MP SelfieSegmenter (square)", "MP SelfieSegmenter (landscape)")
    model_options = list(range(len(model_display)))
    model_selection = st.sidebar.selectbox('Model Selection',options=model_options,format_func=lambda x: model_display[x])

    #background type
    background_type = st.sidebar.selectbox('Background Type',options=['Image','Video','Original'])

    #blur background
    blur_background = st.sidebar.selectbox('Blur Background',options=['No','Low','High'])

    #save result
    save_result = st.sidebar.selectbox('Save Result',options=['No','Yes'])
   
    #file uploader
    video_file_buffer = st.sidebar.file_uploader("Upload Video", type=['mp4','mov','avi','asf','m4v'])
    tfflie = tempfile.NamedTemporaryFile(delete=False)

    if not video_file_buffer:
        if use_webcam:
            vid = cv2.VideoCapture(0)
        else:
            vid = cv2.VideoCapture(DEMO_VIDEO)
            tfflie.name = DEMO_VIDEO
    else:
        tfflie.write(video_file_buffer.read())
        vid = cv2.VideoCapture(tfflie.name)

    if background_type == 'Image':
        #background image
        img_file_buffer = st.sidebar.file_uploader("Upload Background Image", type=['jpg','jpeg','png'])

        if img_file_buffer is not None:
            image = np.array(Image.open(img_file_buffer))
        else:
            demo_image = BG_IMAGE
            image = np.array(Image.open(demo_image))

        st.sidebar.text('Background Image')
        st.sidebar.image(image)
    else:
        #background video
        vid_file_buffer = st.sidebar.file_uploader("Upload Background Video", type=['mp4','mov','avi','asf','m4v'])
        tfflie_bg = tempfile.NamedTemporaryFile(delete=False)

        if not vid_file_buffer:
            vid_bg = cv2.VideoCapture(BG_VIDEO)
            tfflie_bg.name = BG_VIDEO
        else:
            tfflie_bg.write(vid_file_buffer.read())
            vid_bg = cv2.VideoCapture(tfflie_bg.name)

        st.sidebar.text('Background Video')
        st.sidebar.video(tfflie_bg.name)

    #input video
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(vid.get(cv2.CAP_PROP_FPS))
    codec = cv2.VideoWriter_fourcc('V','P','0','9')
    out = cv2.VideoWriter('output.webm', codec, fps, (width, height))
    st.sidebar.text('Input Video')
    st.sidebar.video(tfflie.name)

    #segmentation
    with mp_selfie_segmentation.SelfieSegmentation(model_selection=model_selection) as selfie_segmentation:
        if background_type == 'Image':
            bg_image = image
            bg_image = cv2.resize(bg_image, (width, height))

            if blur_background == 'Low':
                bg_image = cv2.stackBlur(bg_image, (21, 21), 0)
            elif blur_background == 'High':
                bg_image = cv2.stackBlur(bg_image, (51, 51), 0)

            while vid.isOpened():

                ret, frame = vid.read()

                if not ret:
                    break

                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = selfie_segmentation.process(frame)
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.3

                if bg_image is None:
                    bg_image = np.zeros(image.shape, dtype=np.uint8)
                    bg_image[:] = BG_COLOR

                output_image = np.where(condition, frame, bg_image)
                stframe.image(output_image,use_column_width=True)

                # Save the output video
                if save_result == 'Yes':
                    out.write(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))

            vid.release()
            out.release()
            cv2.destroyAllWindows()

        elif background_type == 'Video':
            while vid.isOpened():

                ret, frame = vid.read()
                ret_bg, bg_frame = vid_bg.read()

                if not ret:
                    break
                if not ret_bg:
                    vid_bg.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret_bg, bg_frame = vid_bg.read()

                bg_frame = cv2.resize(bg_frame, (width, height))

                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                bg_frame.flags.writeable = True
                bg_frame = cv2.cvtColor(bg_frame, cv2.COLOR_BGR2RGB)

                if blur_background == 'Low':
                    bg_frame = cv2.stackBlur(bg_frame, (21, 21), 0)
                elif blur_background == 'High':
                    bg_frame = cv2.stackBlur(bg_frame, (51, 51), 0)

                results = selfie_segmentation.process(frame)
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.3

                if bg_frame is None:
                    bg_frame = np.zeros(image.shape, dtype=np.uint8)
                    bg_frame[:] = BG_COLOR

                output_image = np.where(condition, frame, bg_frame)
                stframe.image(output_image,use_column_width=True)

                # Save the output video
                if save_result == 'Yes':
                    out.write(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))

            vid.release()
            out.release()
            cv2.destroyAllWindows()

        else:
            while vid.isOpened():

                ret, frame = vid.read()

                if not ret:
                    break

                frame.flags.writeable = True
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                results = selfie_segmentation.process(frame)
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.3

                bg_image = frame

                if blur_background == 'Low':
                    bg_image = cv2.stackBlur(bg_image, (21, 21), 0)
                elif blur_background == 'High':
                    bg_image = cv2.stackBlur(bg_image, (51, 51), 0)

                output_image = np.where(condition, frame, bg_image)
                stframe.image(output_image,use_column_width=True)

                # Save the output video
                if save_result == 'Yes':
                    out.write(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))

            vid.release()
            out.release()
            cv2.destroyAllWindows()

    st.success('Video is Processed')
    st.stop()

if __name__ == '__main__':
    main()