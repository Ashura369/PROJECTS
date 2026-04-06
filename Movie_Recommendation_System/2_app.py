# Here we will creating a website

# we will be using streamlit
import streamlit as st
import pandas as pd
import pickle
import requests
import gzip
import os

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# -------------------------------------------------------------------------------------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))

movies = pickle.load(open(os.path.join(script_dir, 'movies.pkl'), 'rb'))
movies_list = movies['TITLE'].values 

similarity = pickle.load(gzip.open(os.path.join(script_dir, 'similarity.pkl.gz'), 'rb'))
# -------------------------------------------------------------------------------------------------------------------------------------------------------

# the API used for getting the movie posters
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


# making a function
def recommend(movie):
    movie_index = movies[movies['TITLE'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[movie_index])), reverse=True, key=lambda x: x[1])
    
    recommended_movies = []
    recommended_movies_posters = []
    for i in distances[1:11]:
        # getting the actual TMDB ID from the dataframe
        movie_id = movies.iloc[i[0]]['ID']
        recommended_movies.append(movies.iloc[i[0]]['TITLE'])
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

# -------------------------------------------------------------------------------------------------------------------------------------------------------

# Displays a clickable LinkedIn link in the top right of the page

st.markdown(
    """
    <div style='display: flex; justify-content: flex-end; align-items: center;'>
        <b style='margin-right: 15px; font-size: 16px;'>Credits : </b>
        <a href='https://github.com/Ashura369' target='_blank'>
            <img src='https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white' style='margin-right: 10px;'>
        </a>
        <a href='https://www.linkedin.com/in/ashura369' target='_blank'>
            <img src='https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white'>
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)

# Displays the big heading title on the page
st.title('Movie Recommendation System')
# putting option for to take input, it forces the user to select for one option only

notification_option = st.selectbox(
    "How would you like to be sent notification for upcoming updates?", 
    ("Message", "E-Mail", "Whatsapp Message", "Streamlit Messages")
)

movie_option = st.selectbox("Select a movie", movies_list)
st.write("MOVIE SELECTED :", movie_option)           # used to write lines


# making a button
# gives movie names and movie posters
if st.button('RECOMMEND'):
    recommended_movie_names, recommended_movie_posters = recommend(movie_option)
    
    # First row of 5 movies
    cols_row1 = st.columns(5)
    for index, col in enumerate(cols_row1):
        with col:
            st.text(recommended_movie_names[index])
            st.image(recommended_movie_posters[index])
            
    st.write("") # some spacing 
    
    # Second row of 5 movies
    cols_row2 = st.columns(5)
    for index, col in enumerate(cols_row2):
        with col:
            st.text(recommended_movie_names[index + 5])
            st.image(recommended_movie_posters[index + 5])





