import pytube
import os
import json
from matplotlib import pyplot as plt
     
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

    def add(self, url, song, artist):
        id = url.split("=")[1]
        if id in self.assets:
            print("--------------------------------\nError: Video already exists in database\n")
            self.logAssets(id)
        else:
            try:
                yt = pytube.YouTube(url)
            except:
                print("--------------------------------\nError: Invalid URL\n")
                print("URL: " + url + "\n")

                return
            
            stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            print(stream)
            audiostream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

            if stream is None:
                print("\nError: No video found\n")
                return
            
            if stream.download(output_path = "./assets/video/", filename = url.split("=")[1]+".mp4") and audiostream.download(output_path = "./assets/audio/", filename = url.split("=")[1]+".mp4"):
                self.addToDB( url, artist, song, stream, yt)
            else:
                print("\nError: Video download failed, \n" + "URL: " + url + "\n")
                return

    def addToDB(self, url, artist, song, stream, yt):
        id = url.split("=")[1]
        self.assets[id] = {
            "artist": artist,
            "song": song,
            "length": yt.length,
            "resolution": stream.resolution,
            "fps": stream.fps
        }
        self.length += 1
        with open("./assets/assets.json", "w") as f:
            json.dump(self.assets, f)
        print("--------------------------------\nVideo added to database\n")
        self.logAssets(id)
    
    def logAssets(self, id):
        print("URL: " + "https://www.youtube.com/watch?v=" + id + "\n" + 
                "Artist: " + self.assets[id]["artist"] + "\n" + 
                "Song: " + self.assets[id]["song"] + "\n" + 
                "Duration: " + str(self.assets[id]["length"]) + "\n" + 
                "Resolution: " + self.assets[id]["resolution"] + "\n" + 
                "FPS: " + str(self.assets[id]["fps"]))

    def getVideoPath(self, id):
        return "./assets/video/" + id + ".mp4"

    def getAudioPath(self, id):
        return "./assets/audio/" + id + ".mp4"

# execute only from this file
if __name__ == "__main__":
    asset = AssetDatabase()

    asset.add("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "The Sign", "Ace of Base")
    asset.add("https://www.youtube.com/watch?v=dQw4Q", "The Sign", "Ace of Base")