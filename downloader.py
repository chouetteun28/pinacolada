import src.assetdatabase as assetdatabase
import src.audiosync as audiosync


def main(asset):
    url = input("Enter URL: ")
    while 1:
        if url in asset.assets:
            print(
                "--------------------------------\nError: Video already exists in database\n")
            asset.log_assets(url)
        else:
            break
    artist = input("Enter artist: ")
    while 1:
        if artist == "":
            print("--------------------------------\nError: Artist not specified\n")
        else:
            counter = 0
            for key in asset.assets.keys():
                if asset.assets[key]["artist"] == artist:
                    asset.log_assets(key)
                    counter += 1
            if counter == 0:
                print("--------------------------------\nNew artist added in database\n")
            else:
                print("--------------------------------\n" + str(counter) +
                      " song(s) of this artist found in database\n")
        break
    song = input("Enter song: ")
    while 1:
        if song == "":
            print("--------------------------------\nError: Song not specified\n")
        else:
            counter = 0
            for key in asset.assets.keys():
                if asset.assets[key]["song"] == song:
                    asset.log_assets(key)
                    counter += 1
            if counter == 0:
                print("--------------------------------\nNew song added in database\n")
            else:
                print("--------------------------------\n" +
                      str(counter) + " Song(s) found in database\n")
        break
    audioExists = False
    while 1:
        for key in asset.assets.keys():
            if asset.assets[key]["artist"] == artist and asset.assets[key]["song"] == song and asset.assets[key]["type"] == "audio":
                audioExists = True
                break
        if not audioExists:
            while 1:
                print("--------------------------------\nNo audio found for this song")
                audio_url = input("Enter URL of original audio: ")
                if audio_url in asset.assets:
                    print(
                        "--------------------------------\nError: Audio already exists in database\n")
                    asset.log_assets(audio_url)
                else:
                    break
            if asset.add(audio_url, song, artist, audio=True) == 0:
                break
        else:
            break
    if asset.add(url, song, artist) == 0:
        audiosync.syncAudio(artist, song)
        return 0


# execute only from this file
if __name__ == "__main__":
    asset = assetdatabase.AssetDatabase()
    while 1:
        if main(asset) == 0:
            break