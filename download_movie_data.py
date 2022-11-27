from tmdb import MovieTMDB
import pandas as pd

# Import letterboxd (lb) watchlist data
df_lb_watchlist = pd.read_csv("data/watchlist.csv")

# Delete df_movies if it exists from a previous loop run
if "df_movies" in globals(): del df_movies

# Loop to extract info of all movies from watchlist
for lb_movie, lb_year in zip(df_lb_watchlist.Name, df_lb_watchlist.Year):
        
    movie = MovieTMDB()
    movie.find_movie(query=lb_movie, year=lb_year)
    
    print("\n", movie.movie_info["title"], "by", movie.director, "\n")
    
    
    try: 
        df_movies = pd.concat([df_movies, movie.return_df()],
                              ignore_index=True)
    except NameError:
        df_movies = movie.return_df()
    
