from flask import Flask, render_template, url_for, flash, redirect, session, request
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

app = Flask(__name__)
# Secret key is REQUIRED for CSRF protection and flashing messages
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

# -----------------------------------------------------------------------------------------------------------------

# Use absolute paths relative to this script's location
basedir = os.path.abspath(os.path.dirname(__file__))

# receiving the files
tfidf = pickle.load(open(os.path.join(basedir, 'tfidf.pkl'), 'rb'))
model = pickle.load(open(os.path.join(basedir, 'MultinomialNB.pkl'), 'rb'))

st = PorterStemmer()
stop_words = stopwords.words('english')

def transform(txt):
    txt = str(txt).strip().lower()
    txt = nltk.word_tokenize(txt)
    
    temp = []
    for word in txt:
        if word.isalnum() and word not in stop_words:
            temp.append(word)
    
    text = temp[:]
    temp.clear()

    for word in text:
        temp.append(st.stem(word))
    
    return " ".join(temp)


# -----------------------------------------------------------------------------------------------------------------

# making a class for the registration form
class Registration(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(message="Please enter your name")])
    email = StringField("E-Mail", validators=[DataRequired(message="Please enter your email"), Email(message="Not a valid email")])
    number = StringField("Phone Number", validators=[DataRequired(message="Please enter your number"), Length(min=10, max=15)])
    submit = SubmitField("Register")

# -----------------------------------------------------------------------------------------------------------------

@app.route("/")
def index():
    # Redirect root to /home so users don't get a 404 error
    return redirect(url_for('home'))

# -----------------------------------------------------------------------------------------------------------------

@app.route("/home", methods=['GET','POST'])
def home():

    form = Registration()
    if form.validate_on_submit():
        username = form.name.data
        email = form.email.data
        number = form.number.data

        flash(f"Welcome {username}, [{email}] !", "success")
        return redirect(url_for('mails'))

    # Fixed: Passing 'form=form' so the HTML can render the fields
    return render_template("page_1.html", form=form)

# -----------------------------------------------------------------------------------------------------------------

@app.route("/mails", methods=['GET', 'POST'])
def mails():

    prediction = None
    if request.method == 'POST':
        # receiving input text from page_2
        text = request.form.get("email_content")

        if text:
            text_transformed = transform(text)
            text_vectorized = tfidf.transform([text_transformed])

            result = model.predict(text_vectorized)[0]
            
            # Debug logging
            print(f"DEBUG: Processing text: {text[:50]}...")
            print(f"DEBUG: Transformed: {text_transformed[:50]}...")
            print(f"DEBUG: Prediction Result: {result}")

            if result == 1:
                prediction = "SPAM"
                flash("Analysis complete: High probability of spam detected.", "danger")
            else:
                prediction = "NOT A SPAM"
                flash("Analysis complete: Content remains verified clear.", "success")

    return render_template("page_2.html", prediction=prediction)







# -----------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)
