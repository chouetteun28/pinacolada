import av
import pytube
import os
import json
        
class AssetDatabase:
    def __init__(self):
        if not os.path.isfile("./assets/assets.json"):
            with open("./assets/assets.json", "w") as f:
                json.dump({}, f)
                self.assets = {}
        else:
            with open("./assets/assets.json", "r") as f:
                self.assets = json.load(f)
        self.length = len(self.assets)
    def add(self, id, title, artist, song, duration, resolution):
        self.assets[id] = {
            "title": title,
            "artist": artist,
            "song": song,
            "duration": duration,
            "resolution": resolution
        }
        self.length += 1
        with open("./assets/assets.json", "w") as f:
            json.dump(self.assets, f)

class Video:
    def __init__(self, asset, url, artist, song):
        try:
            self.yt = pytube.YouTube(url)
        except:
            print("\nError: Invalid URL\n")
            exit()
        self.asset = asset
        self.title = self.yt.title
        self.id = url.split("=")[1]
        self.song = song
        self.artist = artist
        self.duration = self.yt.length
        self.download()
    
    def download(self):
        stream = self.yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        self.resolution = stream.resolution
        print(stream)
        if stream.download(output_path = "./assets/", filename = self.id+".mp4"):
            self.asset.add(self.id, self.title, self.artist, self.song, self.duration, self.resolution)
    
    def initVideoLoader(self):
        self.videoLoader = VideoLoader("./assets/", self.id+".mp4")


class VideoLoader:
    def __init__(self, video_path):
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

Video(asset ,"https://www.youtube.com/watch?v=61QSHrOuGEA", "artist", "song")
Video(asset ,"https://www.youtube.com/watch?v=jhFDyDgMVUI", "artist", "song")