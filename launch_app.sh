#! bin/bash
printf "Hello watchlist is starting\n\n"

printf "Fetching your watchlist\n\n"
py "download_movie_data.py" &&

printf "Getting the movie data\n\n" &&
py "format_movie_data.py" &&

printf "And now shiny\n\n" &&
"/c/Program Files/R/R-4.2.2/bin/RScript.exe" start_shiny.R
