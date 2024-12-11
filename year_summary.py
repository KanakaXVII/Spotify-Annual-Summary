#!/bin/python3

# Imports
import pandas as pd
import os
import sys
import json
from dotenv import load_dotenv

def main():
    '''Orchestrates Spotify summary job'''
    # Load dotenv
    load_dotenv()

    # Define parameters
    year = os.getenv('TARGET_YEAR')
    data_dir = os.getenv('DATA_DIR_PATH')
    threshold = int(os.getenv('LISTEN_THRESHOLD'))
    username = os.getenv('SPOTIFY_NAME')
    storeFile = os.getenv('STORE_FILE')

    # Load data
    data = load_data(year=year, dirName=data_dir)

    # Filter out songs that weren't listened to according to threshold
    played_songs = data[data['ms_played'] <= threshold]
    print(f'There are {played_songs.shape[0]} songs plalyed (at least {int(threshold / 1000)} seconds)')

    # Get play counts for songs
    value_counts = pd.DataFrame(columns=['song', 'artist', 'playCount'])

    # Iterate through played songs
    for record in played_songs.iterrows():
        if record[1]['master_metadata_track_name'] == None:
            continue
        
        # Check to see if a record has already been stored
        match_test = recordExists(df=value_counts, record=record)
        if match_test['match'] is True:
            value_counts.loc[match_test['index'], 'playCount'] += 1
        else:
            payload = {
                'song': record[1]['master_metadata_track_name'],
                'artist': record[1]['master_metadata_album_artist_name'],
                'playCount': 1
            }

            value_counts = pd.concat([value_counts, pd.DataFrame([payload])], ignore_index=True)
    
    # Sort the data by play count
    value_counts = value_counts.sort_values(by='playCount', ascending=False)

    # Calculate how many plays for each artist
    artist_counts = {}
    for item in value_counts.iterrows():
        if item[1]['artist'] in artist_counts.keys():
            artist_counts[item[1]['artist']] += item[1]['playCount']
        else:
            artist_counts[item[1]['artist']] = item[1]['playCount']
    
    # Sort the artist count dict
    artist_counts = dict(sorted(artist_counts.items(), key=lambda item: item[1], reverse=True))
    top10Artists = getTop10Artists(artist_counts)

    # Store metrics
    metrics = {
        'totalUniqueSongs': value_counts.shape[0],
        'totalUniqueArtists': len(list(value_counts['artist'].unique())),
        'totalPlays': value_counts['playCount'].sum(),
        'top10Songs': value_counts.head(10),
        'top10Artists': top10Artists,
        'totalTimeListened': (data['ms_played'].sum() / 1000) / 60
    }

    # Spit out summary
    summarize(username, year, metrics)

    # Write to file
    if storeFile is True:
        writeToFile(username, year, metrics)

def load_data(year: str, dirName: str) -> pd.DataFrame:
    '''Loads Spotify data from a local directory'''
    # Init storage
    data = pd.DataFrame()
    file_count = 0

    # Iterate through directory
    for filename in os.listdir(dirName):
        # Check if the filename includes the desired year
        if year in filename:
            # Build the full relative path
            filepath = os.path.join(dirName, filename)
            if os.path.isfile(filepath):
                # Increase counter
                file_count += 1

                # Read the file into a dataframe
                file_df = pd.read_json(filepath)
                print(f'Found {file_df.shape[0]} records in {filename}')

                # Add dataframe to master dataframe
                data = pd.concat([data, file_df], ignore_index=True)
        else:
            print(f'{filename} does not include data for {year}')
    
    # Filter out any non-year records
    data = data[data['ts'].str.contains(f'{year}')]

    # Print metrics
    print(f'Found {data.shape[0]} records in {file_count} different files')
    
    # Return data
    return data

def recordExists(df, record):
    '''Determines if a song record already exists in the mastere dataframe'''
    if record[1]['master_metadata_track_name'] in list(df['song']):
        # Get index values for the records
        inds = df.index[df['song'] == record[1]['master_metadata_track_name']].tolist()

        # Iterate through inds
        for ind in inds:
            if df.loc[ind]['artist'] == record[1]['master_metadata_album_artist_name']:
                return {'match': True, 'songExists': True, 'index': ind}

        # Return a default
        return {'match': False, 'songExists': True}
    else:
        return {'match': False, 'songExists': False}

def getTop10Artists(artists) -> dict:
    '''Finds the top 10 artists in a sorted dict'''
    # Set a counter
    counter = 0
    top10Artists = {}

    # Iterate and store
    for k, v in artists.items():
        if counter < 10:
            top10Artists[k] = v
            counter += 1
        else:
            return top10Artists

def summarize(username, year, metrics):
    '''Provides an annual summary of a set of Spotify data'''
    # A bunch of print lines I guess
    title_line = f'Spotify Metrics {year} - {username}'
    print('\n\n\n')
    print(f'{"-" * 15} {title_line} {"-" * 15}')
    print(f'You played {metrics["totalPlays"]} songs, {metrics["totalUniqueSongs"]} of which are unique!\n')
    print(f'Of these songs, you listened to {metrics["totalUniqueArtists"]} unique artists. Shall we meet them?\n')

    for ind, artist in zip(range(1,11), metrics['top10Artists']):
        print(f'{ind}.\t[{metrics["top10Artists"][artist]}] {artist}')

    print('\n')
    print(f"Let's see those top 10 songs!\n")

    for ind, song in zip(range(1,11), metrics['top10Songs'].iterrows()):
        print(f'{ind}.\t[{song[1]["playCount"]}] {song[1]["song"]}')

    print('\n')
    print(f'Overall, you listened to a total of {round(metrics["totalTimeListened"], 3)} minutes! That is equal to...')
    print(f'\t- {round(metrics["totalTimeListened"] / 60, 3)} Hours...')
    print(f'\t- {round((metrics["totalTimeListened"] / 60) / 24, 3)} Days...')
    print(f'\t- {round(metrics["totalTimeListened"] / 91, 3)} Bee Movies...')

    print('-' * ((15 * 2) + len(title_line)))

    return

def writeToFile(username, year, metrics):
    # A bunch of write lines I guess
    title_line = f'Spotify Metrics {year} - {username}'
    with open(f'Spotify Metrics {year}.txt', 'w') as output:
        output.write(f'{"-" * 15} {title_line} {"-" * 15}')
        output.write('\n')
        output.write(f'You played {metrics["totalPlays"]} songs, {metrics["totalUniqueSongs"]} of which are unique!\n')
        output.write(f'Of these songs, you listened to {metrics["totalUniqueArtists"]} unique artists. Shall we meet them?\n')

        for ind, artist in zip(range(1,11), metrics['top10Artists']):
            output.write(f'\t{ind}.\t[{metrics["top10Artists"][artist]}] {artist}\n')

        output.write('\n')
        output.write(f"Let's see those top 10 songs!\n")

        for ind, song in zip(range(1,11), metrics['top10Songs'].iterrows()):
            output.write(f'\t{ind}.\t[{song[1]["playCount"]}] {song[1]["song"]}\n')

        output.write('\n')
        output.write(f'Overall, you listened to a total of {round(metrics["totalTimeListened"], 3)} minutes! That is equal to...\n')
        output.write(f'\t- {round(metrics["totalTimeListened"] / 60, 3)} Hours...\n')
        output.write(f'\t- {round((metrics["totalTimeListened"] / 60) / 24, 3)} Days...\n')
        output.write(f'\t- {round(metrics["totalTimeListened"] / 91, 3)} Bee Movies...\n')

        output.write('-' * ((15 * 2) + len(title_line)))
    
# Start
if __name__ == '__main__':
    main()