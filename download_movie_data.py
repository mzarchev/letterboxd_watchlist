from tmdb import MovieTMDB
from download_lb_watchlist import download_lb_watchlist
import pandas as pd

redownload = input("Start data download from beginning? [y/n]:")
if redownload == y:
    df_lb_watchlist = download_lb_watchlist("mzarchev")
    df_lb_watchlist.to_csv("data/watchlist.csv")

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

    df_movies.to_csv("data/df_movie_info.csv")

else: 
    df_lb_watchlist = pd.read_csv("data/watchlist.csv")
    df_movies = pd.read_csv("data/df_movie_info.csv")