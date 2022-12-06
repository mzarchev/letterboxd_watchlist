#! /bin/bash

# Concat together all .py files
cat download_lb_watchlist.py <(echo) snake_case.py <(echo) tmdb.py <(echo) \
 download_movie_data.py <(echo) format_movie_data.py > all_py_together.py

 grep -vE "(cat|rat)" sourcefile > destinationfile

 sed -i '/from download/d' all_py_together.py
 sed -i '/from tmdb/d' all_py_together.py
 sed -i '/from snake_case/d' all_py_together.py
