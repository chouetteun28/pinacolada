from collections import namedtuple
import av
import pytube
import os
import json
from collections import namedtuple
     
class AssetDatabase:
    def __init__(self):
        if not os.path.isdir("./assets/"):
            os.mkdir("./assets/")

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
            self.log_assets(id)
        else:
            try:
                yt = pytube.YouTube(url)
            except:
                print("--------------------------------\nError: Invalid URL\n")
                print("URL: " + url + "\n")

                return
            
            stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()

            if stream is None:
                print("\nError: No video found\n")
                return
            
            if stream.download(output_path = "./assets/", filename = url.split("=")[1]+".mp4"):
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
        self.log_assets(id)
    
    def log_assets(self, id):
        print("URL: " + "https://www.youtube.com/watch?v=" + id + "\n" + 
                "Artist: " + self.assets[id]["artist"] + "\n" + 
                "Song: " + self.assets[id]["song"] + "\n" + 
                "Duration: " + str(self.assets[id]["length"]) + "\n" + 
                "Resolution: " + self.assets[id]["resolution"] + "\n" + 
                "FPS: " + str(self.assets[id]["fps"]))

class VideoLoader:
    def __init__(self, id, db):
        self.db = db
        self.id = id
        self.video_path = "./assets/" + id + ".mp4"
        self.video_path = video_path
        self.container = av.container.open(self.video_path)
        self.frameNum = 0
        self.frame = None
        self.original_frame = None
        self.stream = self.container.streams.video[0]
        self.total_frames = self.stream.frames
        self.seek(0)

    def iter_frames(self):
        for packet in self.container.demux(self.stream):
            if packet.dts is None:
                continue
            for frame in packet.decode():
                yield frame

    def __del__(self):
        self.container.close()

    def load_frame(self, frameNum=None):
        if frameNum is not None:
            self.seek(frameNum)
        try:
            frame = next(self.iter)
        except StopIteration:
            self.end = True
            return None
        self.frameNum += 1
        self.original_frame = frame.to_ndarray(format='bgr24')
    def seek(self, frame):
        pts = int(frame * self.stream.duration / self.stream.frames)
        self.container.seek(pts, stream=self.stream)
        for j, f in enumerate(self.iter_frames()):
            if f.pts >= pts - 1:
                break
        self.end = False
        self.frameNum = frame
        self.iter = iter(self.iter_frames())
        
        
asset = AssetDatabase()

asset.add("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "The Sign", "Ace of Base")
asset.add("https://www.youtube.com/watch?v=dQw4Q", "The Sign", "Ace of Base")