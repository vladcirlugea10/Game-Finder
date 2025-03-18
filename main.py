import streamlit as st
from data_fetcher import fetch_game_data
from inference import recommend_games

def main():
    st.title("Game Finder Expert System")
    st.write("Discover your next favorite game based on your preferences!")

    # sidebar for user preferences
    st.sidebar.header("Tell us your preferences")
    genre = st.sidebar.selectbox("Select Genre", ["Action", "Adventure", "Turn-based strategy (TBS)", "Role-playing (RPG)", "Simulation", "Tactical"])
    platform = st.sidebar.selectbox("Select Platform", ["PC (Microsoft Windows)", "PlayStation", "Xbox", "Nintendo Switch"])
    price_max = st.sidebar.slider("Maximum Price ($)", 0, 100, 30)
    
    # checkbox to toggle rated only games
    show_rated_only = st.sidebar.checkbox("Show only rated games", value=False)
    sort_order = st.sidebar.selectbox("Sort by Price", ["Ascending", "Descending"])
    
    # refresh data
    refresh_data = st.sidebar.button("Refresh Game Data")
    games_data = fetch_game_data(force_update=refresh_data)
    
    # put preferences in a dictionary
    user_preferences = {
        "genre": genre.lower(),
        "platform": platform,
        "price_max": price_max
    }
    
    recommended_games = recommend_games(games_data, user_preferences)
    
    # remove games with no rating
    if show_rated_only:
        recommended_games = [game for game in recommended_games if game.get("rating", 0) > 0]

    if sort_order == "Ascending":
        recommended_games = sorted(recommended_games, key=lambda game: game.get("price", 0))
    else:
        recommended_games = sorted(recommended_games, key=lambda game: game.get("price", 0), reverse=True)
    
    st.header("Recommended Games")
    if recommended_games:
        num_columns = 3
        cols = st.columns(num_columns)
        for idx, game in enumerate(recommended_games):
            col = cols[idx % num_columns]
            with col:
                with st.container(border=True):
                    st.subheader(game.get("name", "Unknown Game"))
                    if game.get("image_url"):
                        st.image(game["image_url"], width=150)
                    rating = game.get("rating", 0)
                    if rating > 0:
                        st.write(f"Rating: {rating} ⭐")
                    else:
                        st.write("Rating: No Rating")
                    st.write(f"Price: ${game.get('price', 'N/A')}")
    else:
        st.write("No games match your criteria. Please adjust your preferences.")

if __name__ == "__main__":
    main()
