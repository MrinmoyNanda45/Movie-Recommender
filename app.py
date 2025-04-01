import streamlit as st
import pandas as pd
import pickle
import requests
import os

api_key = os.getenv("TMDB_API_KEY")  # Fixed: Use the environment variable name as a string
if not api_key:
    st.error("TMDB API key not found. Please set TMDB_API_KEY.")
    st.stop()

# Load data with error handling
try:
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame.from_dict(movies_dict, orient='index')
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Data files not found.")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Recommendation function with error handling
def recommend(movie):
    try:
        movie_index = movies[movies['original_title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        return [movies.iloc[i[0]] for i in movies_list]
    except IndexError:
        st.error(f"Movie '{movie}' not found in the dataset.")
        return []

# Cached poster and details fetching
@st.cache_data
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    try:
        data = requests.get(url).json()
        poster_path = data.get('poster_path', '')
        poster_url = f"https://image.tmdb.org/t/p/w185{poster_path}" if poster_path else "https://via.placeholder.com/185x278?text=No+Poster"
        year = data.get('release_date', '')[:4] if data.get('release_date') else "N/A"
        rating = data.get('vote_average', 'N/A')
        return {"poster_url": poster_url, "year": year, "rating": rating}
    except Exception as e:
        st.warning(f"Failed to fetch details for movie ID {movie_id}")
        return {"poster_url": "https://via.placeholder.com/185x278?text=Error", "year": "N/A", "rating": "N/A"}

# Display function
def display_recommendations(recommendations):
    if not recommendations:
        st.warning("No recommendations to show.")
        return
    st.subheader("Top Picks:")
    cols = st.columns(5)
    for i, movie in enumerate(recommendations):
        with cols[i]:
            details = fetch_movie_details(movie['id'])
            st.image(details['poster_url'], width=120)
            st.write(f"**{movie['original_title']}**")
            st.write(f"Year: {details['year']}")
            st.write(f"Rating: {details['rating']}/10")

# Styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    .stImage {
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Main UI
st.title('Movies Recommender System')
st.markdown("Find your next favorite movie! 🍿")
selected_movie_name = st.selectbox("Pick a movie to get recommendations", movies['original_title'].values)

if st.button('Recommend'):
    with st.spinner('Fetching your recommendations...'):
        recommendations = recommend(selected_movie_name)
        display_recommendations(recommendations)