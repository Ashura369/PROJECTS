import streamlit as st
import tensorflow as tf
import numpy as np
import cv2

# 1. Page Config
st.set_page_config(page_title="Live ISL Reader", layout="wide")
st.title("🤟 Real-Time Indian Sign Language Reader")
st.write("Continuous live webcam stream with real-time sign predictions!")

# 2. Load Keras Model
@st.cache_resource
def load_model():
    model_path = "Sign_language_model.keras"
    return tf.keras.models.load_model(model_path)

model = load_model()

# 3. Class Labels (0-9, A-Z -> 36 Classes)
class_names = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z' 
]

# 4. Stream Control & Camera Settings
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 1])
with col_ctrl1:
    run_stream = st.checkbox("▶ Start Real-Time Live Webcam Stream", value=False)
with col_ctrl2:
    mirror_flip = st.checkbox("🪞 Mirror Flip Video Feed", value=True)
with col_ctrl3:
    box_size = st.slider("🎯 Target Box Size:", min_value=150, max_value=400, value=250, step=10)

# Placeholders for Streamlit UI
col1, col2 = st.columns([2, 1])
with col1:
    FRAME_WINDOW = st.image([])
with col2:
    st.markdown("### 📊 Live Prediction Status")
    prediction_text = st.empty()
    confidence_bar = st.progress(0.0)
    confidence_text = st.empty()
    st.markdown("---")
    st.markdown("### 🔝 Top 3 Predictions")
    top3_window = st.empty()
    st.markdown("---")
    st.markdown("### 🔍 Model Input View (180x180)")
    HAND_CROP_WINDOW = st.image([])

# 5. Live Webcam Loop
if run_stream:
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("❌ Unable to access webcam 0. Please make sure no other app is using your camera.")
    else:
        while run_stream:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to grab camera frame.")
                break
                
            # Optional Horizontal Mirror Flip
            if mirror_flip:
                frame = cv2.flip(frame, 1)
                
            h, w, _ = frame.shape
            
            # Define Tight ROI Box in Center of Frame
            half_box = box_size // 2
            cy, cx = h // 2, w // 2
            y1, y2 = max(0, cy - half_box), min(h, cy + half_box)
            x1, x2 = max(0, cx - half_box), min(w, cx + half_box)
            
            # Crop & Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cropped_hand = rgb_frame[y1:y2, x1:x2]
            
            if cropped_hand.size != 0:
                # Resize cropped hand to match model input shape (180, 180)
                resized_hand = cv2.resize(cropped_hand, (180, 180))
                
                # MobileNetV2 Preprocessing: scale pixels from [0, 255] to [-1, 1]
                processed_hand = tf.keras.applications.mobilenet_v2.preprocess_input(resized_hand.astype(np.float32))
                img_batch = np.expand_dims(processed_hand, axis=0)
                
                # Make Real-Time Prediction
                predictions = model.predict(img_batch, verbose=0)[0]
                
                # Top 1 Prediction
                predicted_idx = int(np.argmax(predictions))
                predicted_label = class_names[predicted_idx] if predicted_idx < len(class_names) else f"Class_{predicted_idx}"
                confidence = float(predictions[predicted_idx] * 100)
                
                # Top 3 Predictions
                top3_indices = np.argsort(predictions)[-3:][::-1]
                top3_str = ""
                for idx in top3_indices:
                    label_name = class_names[idx] if idx < len(class_names) else f"Class_{idx}"
                    top3_str += f"* **Sign {label_name}**: {predictions[idx]*100:.1f}%\n"
                
                # Draw green target box & prediction label on live frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                label_display = f"Sign: {predicted_label} ({confidence:.1f}%)"
                cv2.putText(frame, label_display, (x1, max(35, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                
                # Update UI Side Panel
                prediction_text.markdown(f"## Predicted Sign: **{predicted_label}**")
                confidence_bar.progress(min(1.0, float(confidence / 100)))
                confidence_text.write(f"Confidence Level: **{confidence:.2f}%**")
                top3_window.markdown(top3_str)
                HAND_CROP_WINDOW.image(resized_hand, caption="Resized Hand Input", use_container_width=True)
            
            # Convert BGR to RGB for Streamlit display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_rgb, use_container_width=True)
            
        cap.release()

# Enable VS Code "Run Code" (▶) Button Launcher
import sys
from streamlit.web.cli import main

if __name__ == '__main__':
    if not st.runtime.exists():
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(main())