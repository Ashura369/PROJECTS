# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import re
import emoji
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from cleantext import clean

# Download NLTK data if not already present
@st.cache_resource
def setup_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')

setup_nltk()

stop_words = stopwords.words('english')
lmt = WordNetLemmatizer()

def transform(txt):
    txt = clean(txt, lowercase=True, punct=True)    
    txt = re.sub(r'(.)\1{2,}', r'\1', txt)              
    txt = re.sub(r'https?://\S+|www\.\S+', '', txt)    
    txt = re.sub(r'@\S+', '', txt)                     
    txt = emoji.demojize(txt)                           
    txt = word_tokenize(txt)
    temp = [lmt.lemmatize(word, pos='v') for word in txt if word not in stop_words and (word.isalpha() or (word.startswith(':') and word.endswith(':')))]
    return " ".join(temp)

# Page Configuration
st.set_page_config(
    page_title="Airline Sentiment Analysis Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .stCard {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eef2f7;
    }
    
    .badge-negative {
        background-color: #ffebe9;
        color: #cf222e;
        border: 1px solid #ff8182;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-size: 1.3rem;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(207, 34, 46, 0.15);
    }
    .badge-neutral {
        background-color: #ddf4ff;
        color: #0969da;
        border: 1px solid #54aeff;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-size: 1.3rem;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(9, 105, 218, 0.15);
    }
    .badge-positive {
        background-color: #dafbe1;
        color: #1a7f37;
        border: 1px solid #4ac26b;
        padding: 0.6rem 1.2rem;
        border-radius: 30px;
        font-size: 1.3rem;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(26, 127, 55, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# Load Trained Model Assets
@st.cache_resource
def load_assets():
    with open("sentiment_analysis_model.pkl", "rb") as f:
        assets = pickle.load(f)
    return assets

try:
    assets = load_assets()
    vectorizer = assets['vectorizer']
    processor = assets['processor']
    model = assets['model']
    model_loaded = True
except Exception as e:
    st.error(f"Error loading model asset `sentiment_analysis_model.pkl`: {e}")
    model_loaded = False

# Application Header
st.markdown("""
<div class="main-header">
    <h1>✈️ Airline Brand Sentiment Analyzer</h1>
    <p>Real-Time NLP & GPU Gradient Boosted Intelligence for Proactive Customer Care</p>
</div>
""", unsafe_allow_html=True)

if model_loaded:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("📝 Customer Feedback Input")
        
        # Sample presets
        st.caption("Click a sample preset or enter custom feedback:")
        preset_cols = st.columns(3)
        
        tweet_input = ""
        default_airline = "United"
        default_reason = "Customer Service Issue"
        
        if preset_cols[0].button("❌ Cancelled Flight", use_container_width=True):
            tweet_input = "My flight was cancelled at the last minute and no staff helped us rebook! Horrible experience. 😡"
            default_airline = "United"
            default_reason = "Cancelled Flight"
            
        if preset_cols[1].button("😐 Inquiry / Update", use_container_width=True):
            tweet_input = "Can someone confirm if the 4:30 PM flight from Chicago is on schedule?"
            default_airline = "Delta"
            default_reason = "Can't Tell"
            
        if preset_cols[2].button("💚 Excellent Service", use_container_width=True):
            tweet_input = "Huge thanks to the crew on flight 204! Amazing customer service and smooth flight. 💕"
            default_airline = "Virgin_America"
            default_reason = "Customer Service Issue"

        # Form Inputs
        with st.form("sentiment_form"):
            feedback_text = st.text_area(
                "Customer Tweet / Feedback Text",
                value=tweet_input,
                height=130,
                placeholder="Enter customer feedback or social media post here..."
            )
            
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                airline = st.selectbox(
                    "Airline Carrier",
                    ["United", "US_Airways", "American", "Southwest", "Delta", "Virgin_America"],
                    index=["United", "US_Airways", "American", "Southwest", "Delta", "Virgin_America"].index(default_airline)
                )
                day_name = st.selectbox(
                    "Day of Week",
                    ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                    index=1
                )
                timezone = st.selectbox(
                    "User Timezone",
                    ["Eastern_Time", "Central_Time", "Pacific_Time", "Mountain_Time", "Quito", "London"],
                    index=0
                )
                
            with f_col2:
                reason = st.selectbox(
                    "Complaint Reason",
                    ["Customer Service Issue", "Late Flight", "Cancelled Flight", "Lost Luggage", 
                     "Bad Flight", "Flight Booking Problems", "Flight Attendant Complaints", "longlines", "Damaged Luggage", "Can't Tell"],
                    index=["Customer Service Issue", "Late Flight", "Cancelled Flight", "Lost Luggage", 
                           "Bad Flight", "Flight Booking Problems", "Flight Attendant Complaints", "longlines", "Damaged Luggage", "Can't Tell"].index(default_reason)
                )
                hour = st.slider("Tweet Hour (0-23)", 0, 23, 14)
                reason_confidence = st.slider("Reason Confidence Score", 0.0, 1.0, 0.85, step=0.05)
                retweets = st.number_input("Retweet Count", min_value=0, max_value=1000, value=0)

            submit_btn = st.form_submit_button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

    with col_right:
        st.subheader("📊 Sentiment Analysis Results")
        
        if submit_btn or feedback_text.strip():
            if not feedback_text.strip():
                st.warning("Please enter some feedback text to analyze.")
            else:
                with st.spinner("Processing NLP transformations and running model inference..."):
                    # 1. Combine text columns exactly as done during training
                    combined_text_raw = f"{day_name} {timezone} {airline} {feedback_text} {reason}"
                    transformed_text = transform(combined_text_raw)
                    
                    # 2. Vectorize text with TF-IDF
                    tfidf_matrix = vectorizer.transform([transformed_text])
                    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=[f"tfidf_{name}" for name in vectorizer.get_feature_names_out()])
                    
                    # 3. Scale numerical features with ColumnTransformer
                    input_df = pd.DataFrame([{
                        'hour': hour,
                        'reason_confidence': reason_confidence,
                        'retweets': retweets
                    }])
                    scaled_num = processor.transform(input_df)
                    num_df = pd.DataFrame(scaled_num, columns=['hour', 'reason_confidence', 'retweets'])
                    
                    # 4. Concatenate numerical and text TF-IDF features
                    final_input = pd.concat([num_df, tfidf_df], axis=1)
                    
                    # 5. Predict using final model
                    pred_class = model.predict(final_input)[0]
                    
                    # Get probabilities if supported
                    try:
                        probs = model.predict_proba(final_input)[0]
                    except Exception:
                        probs = None
                    
                    label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}
                    pred_label = label_map.get(pred_class, str(pred_class))
                    
                    # Display Large Badge
                    st.markdown("### Predicted Sentiment:")
                    if pred_label == "Negative":
                        st.markdown(f'<div class="badge-negative">🔴 Negative Sentiment</div>', unsafe_allow_html=True)
                    elif pred_label == "Neutral":
                        st.markdown(f'<div class="badge-neutral">🔵 Neutral Sentiment</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="badge-positive">🟢 Positive Sentiment</div>', unsafe_allow_html=True)
                    
                    st.write("")
                    
                    # Display Probabilities
                    if probs is not None:
                        st.markdown("#### Class Confidence Probabilities:")
                        p_neg, p_neu, p_pos = probs[0], probs[1], probs[2]
                        
                        st.write(f"🔴 **Negative:** {p_neg*100:.1f}%")
                        st.progress(float(p_neg))
                        
                        st.write(f"🔵 **Neutral:** {p_neu*100:.1f}%")
                        st.progress(float(p_neu))
                        
                        st.write(f"🟢 **Positive:** {p_pos*100:.1f}%")
                        st.progress(float(p_pos))

                    # Inspection Expander
                    with st.expander("🛠️ Inspect NLP Preprocessing & Feature Pipeline"):
                        st.markdown("**Combined Raw Feature Input:**")
                        st.code(combined_text_raw)
                        st.markdown("**Cleaned & Demojized Tokens:**")
                        st.code(transformed_text)
                        st.markdown("**Final Model Input Feature Matrix Shape:**")
                        st.write(final_input.shape)
        else:
            st.info("Enter feedback on the left or select a preset, then click **Analyze Sentiment** to view predictions.")
