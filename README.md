# Welcome!
This script uses some environment variables, so you'll need to do the following:
1. Create a new file in the code directory named `.env`
2. Add a new value `TARGET_YEAR` and set it equal to the year you want to see a summary of
3. Add a new value `LISTEN_THRESHOLD` and set it to the milliseconds value you want to consider "listened" (recommend 15000)
4. Add a new value `DATA_DIR_PATH` and set it equal to the directory (relative preferred) where the Spotify JSON files are stored
5. Add a new value `SPOTIFY_NAME` and set it to your username (or any name, it's just used for printing)
6. Add a new value `STORE_FILE` and set it to True or False (determines if a `.txt` file is written)
