51pp
====

A Search BT torrent website, use python tornado


3rd Part:
1. coreseek
2. postgresql

Install:
1. run sqlfiles/51ppdb.sql file, create db
2. run deamon utils/DHTSpider.py in backgroup, search and save bt file info to the db
3. run python main.py to open the website service.
4. run coreseek make index, and coreseek search service.
