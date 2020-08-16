import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg2
import config as creds
from sqlalchemy import create_engine

# Create a function that cleans up the genre data format and compares to incoming artist genre info
def genre_cleaner(genre):
    temp5 = genre

    # Remove the [, ], and ' characters from the spotify_genre data
    waxC = ["[", "]", "'"]

    for char in waxC:
        print(temp5)
        temp5 = temp5.replace(char, "")

    # Strip out leading spaces and convert sporify_genre data from string to array
    classGenre = temp5.split(",")
    classGenreHolder = []
    for item in classGenre:
        classGenreHolder.append(item.strip())
    classGenre = classGenreHolder
    classGenre = list( dict.fromkeys(classGenre))
    return classGenre

# Create a function to compare the genres
def genreCompare(artistGenre, dbGenre):
    count = 0
    for genre in artistGenre:
        for item in dbGenre:
            if genre == item:
                count +=1
                #print(f"Incoming Genre is: {genre}\n Caegory Genre is: {item}")
    return float(count/len(artistGenre)*100)

def findSong(charateristics, genreData, popularity):
    database=creds.database
    user=creds.user
    password=creds.password
    host=creds.host
    port=5432
    engine = create_engine('postgresql+psycopg2://'+user+':'+password+'@'+host+':'+str(port)+'/'+database)

    dbConnect = engine.connect()

    songData = pd.read_sql("select * from \"audio_features\"", dbConnect)

    songData["spotify_track_popularity"] = pd.to_numeric(songData["spotify_track_popularity"], errors='coerce')
    songData.dropna(subset=["spotify_track_popularity"], inplace=True)
    # print(songData.info())

    # print( type(charateristics))
    # print(charateristics)

    returnData = pd.DataFrame(columns=["Artist", "Song", "TrackID"])
    # print(returnData.info())
    # returnData = {}
    # songData = pd.read_excel("Resources/Hot 100 Audio Features - cleaned.xlsx")
    #inputGenre = genreData
    print("Right before from_dict")
    finalChar = pd.DataFrame.from_dict(charateristics, orient='index')
    finalChar = finalChar.transpose()
    # print(finalChar)
    songInfo = pd.DataFrame.from_dict(finalChar)
    songInfo.insert(loc=0, column="spotify_track_popularity", value=popularity)

    # songDataTest = songData.head().copy()
    # for i in songDataTest.iterrows():
    #     temp3 = i[1].spotify_genre
    #     waxC = ["[", "]", "'"]

    #     for char in waxC:
    #         temp3 = temp3.replace(char, "")

    #     classification3 = temp3.split(",")
    #     classHolder3 = []
    #     for item in classification3:
    #         classHolder3.append(item.strip())
    #         classification3 = classHolder3

    #     classification3 = list( dict.fromkeys(classification3))
    #     print(classification3)

    # Splitting Data into X and y values with Track Duration being the key for y parameter
    XTD = songData[["spotify_track_popularity", "danceability", "energy", "key", "loudness", "mode",
                    "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo",
                    "time_signature"]]
    # ytd = songData["spotify_track_duration_ms"].values.reshape(-1, 1)


    # Create KMeans Model
    from sklearn.cluster import KMeans
    print("Right before kmeans=1024")
    kmeans = KMeans(n_clusters=1024)

    # Train/Fit model
    kmeans.fit(XTD)

    # Predict
    print("Right before predict XTD")
    predicted_clusters = kmeans.predict(XTD)

    songInfo = songInfo[["spotify_track_popularity", "danceability", "energy", "key", "loudness", "mode",
                    "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo",
                    "time_signature"]]
    print("Right before predict songInfo")
    predicted_songInfo = kmeans.predict(songInfo)

    # Assign data cluster number to new field in dataframe for the songs
    songData["Cluster"] = predicted_clusters

    songDataCopy = songData.loc[songData["Cluster"] == predicted_songInfo[0]].copy()

    for i in songDataCopy.iterrows():
    #temp2 = i[1].spotify_genre
        # print("Inside trying to find songs")
        tempGenre = genre_cleaner(i[1].spotify_genre)
    #print(tempGenre)

        x = genreCompare(genreData, tempGenre)
        if x >= 50:
            print(i[1].spotify_genre)
            print(str(x)+"%")
            print(f"Performer: {i[1].performer}\nSong: {i[1].song}\n\n")
            # returnData.update({i[1].Performer : i[1].Song})
            returnData.loc[len(returnData)] = [i[1].performer, i[1].song, i[1].spotify_track_id]
    print(returnData)
    return returnData
