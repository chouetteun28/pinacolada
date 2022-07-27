import pytube
import os
import json
import sys

DOWNLOAD_RESOLUTION = "480p"
     
class AssetDatabase:
    def __init__(self):
        if not os.path.isdir("./assets/"):
            os.mkdir("./assets/")
        if not os.path.isdir("./assets/audio/"):
            os.mkdir("./assets/audio/")
        if not os.path.isdir("./assets/video/"):
            os.mkdir("./assets/video/")

        if not os.path.isfile("./assets/assets.json"):
            with open("./assets/assets.json", "w") as f:
                json.dump({}, f)
                self.assets = {}
        else:
            with open("./assets/assets.json", "r") as f:
                self.assets = json.load(f)
        self.length = len(self.assets)

    def add(self, url, song, artist, audio=False):
        if len(url.split("=")) == 1:
            print("--------------------------------\nError: Invalid URL\n")
            print("URL: " + url + "\n")

            return -1
        id = url.split("=")[1]
        if id in self.assets:
            print("--------------------------------\nError: Video already exists in database\n")
            self.logAssets(id)
            return -1
        else:
            try:
                yt = pytube.YouTube(url)
            except:
                print("--------------------------------\nError: Invalid URL\n")
                print("URL: " + url + "\n")

                return -1
            
            if not audio:
                stream = yt.streams.filter(file_extension='mp4',resolution=DOWNLOAD_RESOLUTION, type="video").desc().first()
                audiostream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                print(stream)
                print(audiostream)
                if stream is None:
                    print("--------------------------------\nError: Video is not available in the selected resolution\n")
                    return -1
                if audiostream is None:
                    print("--------------------------------\nError: Video has no audio\n")
                    return -1
                if stream.download(output_path = "./assets/video/", filename = url.split("=")[1]+".mp4") and audiostream.download(output_path = "./assets/audio/", filename = url.split("=")[1]+".mp4"):
                    self.addToDB( url, artist, song, stream, yt)
                    return 0
                else:
                    print("\nError: Video download failed, \n" + "URL: " + url + "\n")
                    return -1
            else: 
                stream = None
                audiostream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                if audiostream is None:
                    print("\nError: No audio found\n")
                    return -1
                if audiostream.download(output_path = "./assets/audio/", filename = url.split("=")[1]+".mp4"):
                    self.addToDB( url, artist, song, stream, yt, audio=True)
                    return 0
                else:
                    print("\nError: Video download failed, \n" + "URL: " + url + "\n")
                    return -1

    def addToDB(self, url, artist, song, stream, yt, audio=False):
        id = url.split("=")[1]
        self.assets[id] = {
            "url": url,
            "artist": artist,
            "song": song,
            "length": yt.length,
        }
        if audio:
            self.assets[id]["resolution"] = ""
            self.assets[id]["fps"] = ""
            self.assets[id]["type"] = "audio"
        else:
            self.assets[id]["resolution"] = stream.resolution
            self.assets[id]["fps"] = stream.fps
            self.assets[id]["type"] = "video"
            
        self.length += 1
        with open("./assets/assets.json", "w") as f:
            json.dump(self.assets, f)
        print("--------------------------------\nVideo added to database\n")
        self.logAssets(id)
    
    def logAssets(self, id):
        print("--------------------------------\nURL: " + "https://www.youtube.com/watch?v=" + id + "\n" + 
                "Artist: " + self.assets[id]["artist"] + "\n" + 
                "Song: " + self.assets[id]["song"] + "\n" + 
                "Duration: " + str(self.assets[id]["length"]) + "\n" + 
                "Resolution: " + self.assets[id]["resolution"] + "\n" + 
                "Type: " + self.assets[id]["type"] + "\n" +
                "FPS: " + str(self.assets[id]["fps"]))

    def getVideoPath(self, id):
        return "./assets/video/" + id + ".mp4"

    def getAudioPath(self, id):
        return "./assets/audio/" + id + ".mp4"

def main(asset):
    url = input("Enter URL: ")
    while 1:
        if url in asset.assets:
            print("--------------------------------\nError: Video already exists in database\n")
            asset.logAssets(url)
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
                    asset.logAssets(key)
                    counter += 1
            if counter == 0:
                print("--------------------------------\nNew artist added in database\n")
            else:
                print("--------------------------------\n" + str(counter) +" song(s) of this artist found in database\n")
        break
    song = input("Enter song: ")
    while 1:
        if song == "":
            print("--------------------------------\nError: Song not specified\n")
        else:
            counter = 0
            for key in asset.assets.keys():
                if asset.assets[key]["song"] == song:
                    asset.logAssets(key)
                    counter += 1
            if counter == 0:
                print("--------------------------------\nNew song added in database\n")
            else:
                print("--------------------------------\n" + str(counter) +" Song(s) found in database\n")
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
                    print("--------------------------------\nError: Audio already exists in database\n")
                    asset.logAssets(audio_url)
                else:
                    break
            if asset.add(audio_url, song, artist, audio=True) == 0:
                break
        else:
            break
    if asset.add(url, song, artist) == 0:
        return 0


# execute only from this file
if __name__ == "__main__":
    asset = AssetDatabase()
    while 1:
        if main(asset) == 0:
            break
