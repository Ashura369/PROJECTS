import streamlit as st
import tensorflow as tf
import numpy as np
import cv2                              # cv2 is OpenCV (Open Source Computer Vision), a popular Python library for processing images and real-time video streams, live video, photo, cropping, resizing, color conversion, etc

import sys
# a standard built-in Python module that lets your script interact directly with the Python interpreter and your Operating System.

from streamlit.web.cli import main
from streamlit.web import cli as stcli
# Those two lines import Streamlit's internal Command Line Interface (CLI) modules.
# They are imported so you can run your app by simply clicking the "Run Code" (▶) button in VS Code, without opening a terminal or typing streamlit run app.py manually.

# ------------------------------------------------------------------------------------------------------------------

st.set_page_config(page_title='liveISLReader', layout='wide')
st.title("Real-Time Indian Sign Language Reader")
st.write("Continuous live webcam stream with real-time sign predictions !!!")

# ------------------------------------------------------------------------------------------------------------------

# Loading the model
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("Sign_language_model.keras")
model = load_model()

# class labels
class_names = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z' 
]

# ------------------------------------------------------------------------------------------------------------------

# function for showing popup img
@st.dialog("Original Input Image", width='large')               # this makes the img pop up
def show_image_popup(image):
    st.image(image, use_container_width=True)

col1, col2 = st.columns([2,1])
with col1:
    img_taken = st.file_uploader("Upload a Hand Sign Image", type=['jpg','jpeg','png'])

    if img_taken is not None:
        bytes_data = img_taken.getvalue()           # The input img is story as raw list of numbers, it retreives the list of numbers and stores it into bytes data
        cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            # cv2.imdecode -- Converts the raw file stream into a 1-dimensional list of numbers in RAM
            # cv2.IMREAD_COLOR -- Tells OpenCV to extract full 3-channel color (Blue, Green, Red).


        # Coverting BGR to RGB 
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        # resizing the input img
        resized_img = cv2.resize(rgb_img, (180,180))

        # displaying the img
        st.image(resized_img, caption='Resized Image (180 x 180)')

        if st.button("Maximize"):
            show_image_popup(rgb_img)
        
with col2:
    st.markdown("### Prediction Resualts")
    prediction_text = st.empty()
    confidence_bar = st.progress(0.0)
    confidence_text = st.empty()
    st.markdown("---")

    st.markdown("#### Top 3 Predictions")
    top3_resualts = st.empty()
    st.markdown("---")


# Showing the output of the img (model prediction)
if img_taken is not None:
    processed_img = resized_img.astype(np.float32)
    img_batch = np.expand_dims(processed_img, axis=0)

    # making prediction
    predictions = model.predict(img_batch, verbose=0)[0]

    # Top 1 Prediction
    predicted_idx = int(np.argmax(predictions))
    predicted_label = class_names[predicted_idx]
    confidence = float(predictions[predicted_idx] * 100)

    # Top 3 Predictions
    top3_indices = np.argsort(predictions)[-3:][::-1]
    top3_str = ""

    for idx in top3_indices:
        top3_str += f"* **Sign {class_names[idx]}**: {predictions[idx]*100:.1f}%\n"

    # Displayiing resualts in col2
    prediction_text.markdown(f"Predicted Sign : {predicted_label}")
    confidence_bar.progress(min(1.0, float(confidence / 100)))
    confidence_text.write(f"Confidence Level : {confidence:.2f}%")
    top3_resualts.markdown(top3_str)





# ------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    if st.runtime.exists():
        pass
    else:
        sys.argv = ['streamlit', 'run', sys.argv[0]]                # This line prepares the command line argument list to look like ['streamlit', 'run', 'app.py']. (Note: sys.argb has a small typo — it should be sys.argv with a v).
        sys.exit(stcli.main())                                      # Launches Streamlit's engine (stcli.main()), opens your web browser to http://localhost:8501, and starts your web app automatically!

