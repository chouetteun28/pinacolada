from typing import Tuple
import pytube
import os
import json
import sys

DOWNLOAD_RESOLUTION = "720p"

class AssetDatabase:
    def __init__(self):
        """
        Initialize the database
        """
        if not os.path.isdir("./assets/"):
            os.mkdir("./assets/")
        if not os.path.isdir("./assets/audio/"):
            os.mkdir("./assets/audio/")
        if not os.path.isdir("./assets/video/"):
            os.mkdir("./assets/video/")

        if not os.path.isfile("./assets/assets.json"):
            self.assets = {}
            self.save_assets()
        else:
            with open("./assets/assets.json", "r") as f:
                self.assets = json.load(f)
        self.length = len(self.assets)

    def add(self, url: str, song: str, artist: str, audio: bool = False):
        """Adds a video to the database

        Args:
            url (str): URL of the video
            song (str): Name of the song(without space, lowercase)
            artist (str): Music artist(without space, lowercase)
            audio (bool, optional): if the url is for only audio. Defaults to False.

        Returns:
            int: 0 when successful, -1 when aborts
        """
        if len(url.split("=")) == 1:
            print("--------------------------------\nError: Invalid URL\n")
            print("URL: " + url + "\n")

            return -1
        id = url.split("=")[1]
        if id in self.assets:
            print(
                "--------------------------------\nError: Video already exists in database\n")
            self.log_assets(id)
            return -1
        else:
            try:
                yt = pytube.YouTube(url)
            except:
                print("--------------------------------\nError: Invalid URL\n")
                print("URL: " + url + "\n")

                return -1

            if not audio:
                stream = yt.streams.filter(
                    file_extension='mp4', resolution=DOWNLOAD_RESOLUTION, type="video").desc().first()
                audiostream = yt.streams.filter(
                    only_audio=True, file_extension='mp4').first()
                print(stream)
                print(audiostream)
                if stream is None:
                    print(
                        "--------------------------------\nError: Video is not available in the selected resolution\n")
                    return -1
                if audiostream is None:
                    print(
                        "--------------------------------\nError: Video has no audio\n")
                    return -1
                if stream.download(output_path="./assets/video/", filename=url.split("=")[1]+".mp4") and audiostream.download(output_path="./assets/audio/", filename=url.split("=")[1]+".mp4"):
                    self.add_to_db(url, artist, song, stream, yt)
                    return 0
                else:
                    print("\nError: Video download failed, \n" +
                          "URL: " + url + "\n")
                    return -1
            else:
                stream = None
                audiostream = yt.streams.filter(
                    only_audio=True, file_extension='mp4').first()
                if audiostream is None:
                    print("\nError: No audio found\n")
                    return -1
                if audiostream.download(output_path="./assets/audio/", filename=url.split("=")[1]+".mp4"):
                    self.add_to_db(url, artist, song, stream, yt, audio=True)
                    return 0
                else:
                    print("\nError: Video download failed, \n" +
                          "URL: " + url + "\n")
                    return -1

    def add_to_db(self, url: str, artist: str, song: str, stream: pytube.Stream, yt: pytube.YouTube, audio=False):
        """Adds a video to the database based on the given information

        Args:
            url (str): URL of the video
            artist (str): Music artist(without space, lowercase)
            song (str): Name of the song(without space, lowercase)
            stream (pytube.Stream): Stream of the video
            yt (pytube.YouTube): YouTube object of the video
            audio (bool, optional): If the url is only audio. Defaults to False.
        """
        id = url.split("=")[1]
        self.assets[id] = {
            "url": url,
            "artist": artist,
            "song": song,
            "length": yt.length,
        }
        if audio:
            self.assets[id]["type"] = "audio"
        else:
            self.assets[id]["resolution"] = stream.resolution
            self.assets[id]["fps"] = stream.fps
            self.assets[id]["type"] = "video"
            self.assets[id]["offset"] = -1

        self.length += 1
        self.save_assets()
        print("--------------------------------\nVideo added to database\n")
        self.log_assets(id)

    def log_assets(self, id):
        """Logs the video information to the console

        Args:
            id (str): id of the video
        """
        print("--------------------------------\nURL: " + "https://www.youtube.com/watch?v=" + id + "\n" +
              "Artist: " + self.assets[id]["artist"] + "\n" +
              "Song: " + self.assets[id]["song"] + "\n" +
              "Duration: " + str(self.assets[id]["length"]) + "\n" +
              "Type: " + self.assets[id]["type"])
        if self.assets[id]["type"] == "video":
            print("Resolution: " + self.assets[id]["resolution"] + "\n" +
                  "Offset: " + str(self.assets[id]["offset"]) + "\n" +
                  "FPS: " + str(self.assets[id]["fps"]))

    def get_video_path(self, id: str):
        """get the path of the video

        Args:
            id (str): id of the video

        Returns:
            str: path of video file
        """
        return "./assets/video/" + id + ".mp4"

    def get_audio_path(self, id: str):
        """get the path of the audio

        Args:
            id (str): id of the video

        Returns:
            str: path of audio file
        """
        return "./assets/audio/" + id + ".mp4"

    def get_offset(self, id: str):
        """get the offset of the video

        Args:
            id (str): id of the video

        Returns:
            int: offset of the video
        """
        return self.assets[id]["offset"]

    def filter_asset(self, artist: str, song: str) -> Tuple[list[str], str]:
        """filters the database for a specific artist and song

        Args:
            artist (str): Music artist(without space, lowercase)
            song (str): Name of the song(without space, lowercase)

        Returns:
            tuple(list, str): (id of audio, list of id of the videos)
        """
        videos = []
        audio = None
        for id in self.assets:
            if self.assets[id]["artist"] == artist and self.assets[id]["song"] == song:
                if self.assets[id]["type"] == "video":
                    videos.append(id)
                elif self.assets[id]["type"] == "audio":
                    audio = id
        return videos, audio

    def set_offset(self, id: str, offset: int):
        """sets the offset of the video

        Args:
            id (str): id of the video
            offset (int): offset of the video
        """
        self.assets[id]["offset"] = offset
        self.save_assets()

    def save_assets(self):
        """saves the assets to the database
        """
        with open("./assets/assets.json", "w") as f:
            json.dump(self.assets, f)

    def del_asset(self, id: str):
        """deletes the asset from the database

        Args:
            id (str): id of the video
        """
        os.remove(self.get_audio_path(id))
        if self.assets[id]["type"] == "video":
            os.remove(self.get_video_path(id))
        self.assets.pop(id)
        self.save_assets()
        self.length -= 1
