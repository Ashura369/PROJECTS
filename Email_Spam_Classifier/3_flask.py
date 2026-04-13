from flask import Flask, render_template, url_for, flash, redirect, session, request
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

# receiving the files
tfidf = pickle.load(open('tfidf.pkl','rb'))
model = pickle.load(open('MultinomialNB.pkl','rb'))

st = PorterStemmer()
stop_words = stopwords.words('english')

def transform(txt):
    txt = str(txt).strip().lower()
    txt = nltk.word_tokenize(txt)
    
    temp = []
    for word in txt:
        # Fixed 'i' to 'word'
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

@app.route("/home", methods=['GET','POST'])
def home():
    # Initializing variables to None to prevent UnboundLocalError
    username = email = number = None

    form = Registration()
    if form.validate_on_submit():
        username = form.name.data
        email = form.email.data
        number = form.number.data

        flash(f"Welcome {username}, [{email}] !", "success")

    # Fixed: Passing 'form=form' so the HTML can render the fields
    return render_template("page_1.html", form=form, name=username, email=email, number=number)

if __name__ == "__main__":
    app.run(debug=True)
