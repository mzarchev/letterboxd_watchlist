#! bin/bash

py "download_movie_data.py" &&
py "format_movie_data.py" &&
Rscript.exe "start_shiny.R"