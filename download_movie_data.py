from tmdb import MovieTMDB
from download_lb_watchlist import download_lb_watchlist
import pandas as pd

# Get watchlist data
df_lb_watchlist = download_lb_watchlist("mzarchev")

# Loop to extract info of all movies from watchlist
for lb_movie, lb_year in zip(df_lb_watchlist.Name, df_lb_watchlist.Year):
    
    movie = MovieTMDB()
    
    movie.find_movie(query=lb_movie, year=str(lb_year))
    
    try: # Catch if movie cannot be found
        try: # Catch if on first loop
            df_movies = pd.concat([df_movies, movie.return_df()],
                                ignore_index=True)
            print("\n Processed", movie.movie_info["title"], "by", movie.director, "\n")
        except NameError:
            df_movies = movie.return_df()
    except:
        pass
        

# Export
df_lb_watchlist.to_csv("data/watchlist.csv")
df_movies.to_parquet("data/df_movie_info.parquet")
