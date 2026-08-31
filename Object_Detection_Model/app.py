import streamlit as st
import sys
import numpy as np
import cv2 as cv
from ultralytics import YOLO                # to use obj detection model
from streamlit.web.cli import main
from streamlit.web import cli as stcli
from PIL import Image
import tempfile                             # for video preprocessing

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAGE LAYOUT
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
st.set_page_config('objDetection', layout='wide')


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CREDIT SECTION
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

st.markdown(
    """
    <div style='display: flex; justify-content: flex-end; align-items: center; margin-bottom: 5px;'>
        <b style='margin-right: 15px; font-size: 16px;'>Credits : </b>
        <a href='https://github.com/pradhans369' target='_blank'>
            <img src='https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white' style='margin-right: 10px;'>
        </a>
        <a href='https://www.linkedin.com/in/pradhans369/' target='_blank'>
            <img src='https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white'>
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# HEADINGS
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

st.title("Project Vision | Object Detection")
st.write("Detecting Over More Than 100 Classes")
st.markdown("---")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MODEL
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@st.cache_resource
def load_model():
    return YOLO("yolo26n.pt")

model = load_model()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN BUTTON SECTION
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

btn_sec1, btn_sec2 = st.columns([1,1])

with btn_sec1:
    button = st.selectbox('Select Input Source', options=['Image', 'Recorded Video', 'Live webcam'], index=None)

st.divider()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 'IMAGE' BUTTON
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if button == 'Image':
    with btn_sec2:
        img_btn = st.selectbox('Select Image Input', options=['Open Camera', 'Upload image'], index=None)


    img_format = ['.jpg','.jpeg','.png','.gif','.webp']
    btn_sec1, btn_sec2 = st.columns([1, 1])

    if img_btn == 'Open Camera':
        with btn_sec1:
            img_clicked = st.camera_input("Take live picture")                              # used for clicking image

        if img_clicked is not None:
            img = Image.open(img_clicked)                                                   # converting image buffer to opencv format

                # Converts Raw Bytes to a PIL Image: Uses Python's Pillow library (PIL.Image) to read and decode the raw byte stream from 'img_clicked' into a workable PIL Image object.
                # Prepares for Processing: Once it is a PIL image, you can easily convert it to a NumPy array (np.array(img)), pass it into computer vision models (like YOLO), or perform transformations (resizing, filtering, etc.).

            img_array = np.array(img)           # converting the img into a numpy array

            # sending the numpy array into the model
            result = model(img_array)

            with btn_sec2:
                st.subheader("Detected Objects in the Image")
                st.image(result[0].plot(), caption='detected objects')
        else:
            with btn_sec2:
                st.info("Snap a photo on the left to see detections here")

    elif img_btn == 'Upload image':
        with btn_sec1:
            st.write("Select image from files")
            imgs_uploaded = st.file_uploader('Select image / images', type=img_format, accept_multiple_files=True)         # accepting multiple image files

            if imgs_uploaded:
                with btn_sec2:
                    st.subheader("Detected Objects in the Image")

                for img in imgs_uploaded:

                    img = Image.open(img)
                    img_array = np.array(img)

                    result = model(img_array)

                    with btn_sec2:
                        st.image(result[0].plot())
            else:
                with btn_sec2:
                    st.info("Select a photo from the files to see detections here")


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 'RECORDED VIDEO' BUTTON
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


elif button == 'Recorded Video':
    vid_format = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    btn_sec1, btn_sec2 = st.columns([1, 1])


    with btn_sec1:
        rec_vid = st.file_uploader('Upload Video (one video only)', type=vid_format)
        

    with btn_sec2:
        if rec_vid is not None:
            # saving the uploaded video bytes to a file on a disk with mp4 format
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(rec_vid.read())
            tfile.close()                   # closing the file so 'OpenCV' can read it

            col1, col2 = st.columns([1,1])
            with col1:
                generate = st.button('Generate')

            if generate:
                cap = cv.VideoCapture(tfile.name)

                width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
                total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT)) or 100
                fps = int(cap.get(cv.CAP_PROP_FPS)) or 30

                out_tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                fourcc = cv.VideoWriter_fourcc(*'mp4v')
                out = cv.VideoWriter(out_tfile.name, fourcc, fps, (width, height))

                # making a progressbar for the download button 
                progress_bar = st.progress(0, text='Processing the video to download')
                vid_play = st.empty()
                current_frame = 0
                
                while cap.isOpened():
                    ret, frames = cap.read()
                    if not ret:
                        print('ERROR')
                        break

                    results = model(frames)
                    out.write(results[0].plot())

                    rgb_vid = cv.cvtColor(results[0].plot(), cv.COLOR_BGR2RGB)
                    vid_play.image(rgb_vid, channels='RGB')

                    # updating progressbar by each frame processed
                    current_frame += 1
                    progress = min(current_frame / total_frames, 1.0)
                    progress_bar.progress(
                        progress,
                        text=f"Processing download : frame {current_frame} of {total_frames} ({int(progress * 100)} %)"
                    )


                cap.release()
                out.release()
                st.toast('Video processing complete !!!')

                with col2:
                    # making a download button for the generated video
                    with open(out_tfile.name, 'rb') as f:
                        video_bytes = f.read()

                    st.download_button(
                        label='Download',
                        data=video_bytes,
                        file_name="yolo_detected_video.mp4",
                        mime="video/mp4"
                    )
        else:
            st.info('Upload a video file to see object detection')



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 'LIVE WEB CAM' BUTTON
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

elif button == 'Live webcam':
    
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    cam_feed = st.empty()

    while True:
        ret, frames = cap.read()
        if not ret:
            st.subheader("⚠️ Camera Error")
            st.write("""
The following error is generally caused by denied camera access.

If camera permission is not granted, please allow camera access in your browser or Windows Privacy Settings.
""")
            break

        # frames = cv.flip(frames, 1)
        results = model(frames)
        vid_rgb = cv.cvtColor(results[0].plot(), cv.COLOR_BGR2RGB)
        cam_feed.image(vid_rgb, use_container_width=True)

    cap.release()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    if st.runtime.exists():
        pass
    else:
        sys.argv = ['streamlit', 'run', sys.argv[0]]
        sys.exit(stcli.main())

