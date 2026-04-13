import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Paths
project_dir = r"d:\THE CODE\PROJECTS\Email_Spam_Classifier"
app_dir = os.path.join(project_dir, "app")

print("Loading data...")
# Load the cleaned dataframe
with open(os.path.join(project_dir, 'df.pkl'), 'rb') as file:
    df = pickle.load(file)

print("Fitting TF-IDF Vectorizer...")
# Train TfidfVectorizer
tfidf = TfidfVectorizer(max_features=3000)
X = tfidf.fit_transform(df['TRANSFORMED_WORDS']).toarray()
y = df['TARGET'].values

print("Fitting MultinomialNB model...")
# Train MultinomialNB
mnb = MultinomialNB()
mnb.fit(X, y)

print("Dumping fitted models...")
# Overwrite the empty models in the app folder with the properly fitted ones
with open(os.path.join(app_dir, 'tfidf.pkl'), 'wb') as file:
    pickle.dump(tfidf, file)

with open(os.path.join(app_dir, 'MultinomialNB.pkl'), 'wb') as file:
    pickle.dump(mnb, file)

print("SUCCESS: Fitted models saved accurately to app folder.")
