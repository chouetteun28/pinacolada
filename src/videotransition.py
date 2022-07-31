import cv2
import numpy as np
from vidgear.gears import CamGear

import src.assetdatabase as assetdatabase

"""
Only works with 30fps videos
"""
FPS = 30


class VideoTransition:
    def __init__(self, artist: str, song: str):
        db = assetdatabase.AssetDatabase()
        videos, audio = db.filter_asset(artist, song)
        self.videos = videos
        self.audio = audio
        self.duration = db.assets[self.audio]["length"]
        self.streams = [CamGear(source=db.get_video_path(id)).start()
                        for id in videos]
        self.frames = [None for _ in videos]
        self.frame_nums = [0 for _ in videos]
        self.offsets = [db.get_offset(id) for id in videos]
        self.is_loading = [False for _ in videos]
        self.resolution = int(db.get_resolution(videos[0]).replace('p', ''))
        self.resolution = (self.resolution, self.resolution // 9 * 16)
        self.placeholder = np.zeros(
            (self.resolution[0], self.resolution[1], 3), dtype=np.uint8)
        self.time = 0

        # match syncronization of videos
        for i in range(len(self.videos)):
            if self.offsets[i] > 0:
                for _ in range(int(self.offsets[i]*FPS)):
                    self.get_frame(i)
            elif self.offsets[i] < 0:
                self.frames[i] = self.placeholder

    def get_frame(self, i: int):
        if self.time + self.offsets[i] > 0:
            self.frame_nums[i] += 1
            frame = self.streams[i].read()
            if frame is None:
                return -1, False
            return frame, True
        return self.placeholder, True

    def display_frame(self, id: str = None, frame: np.ndarray = None):
        """Display frames in a opencv window

        Args:
            id (int, optional): Shows the frame of the id on the window. Shows all videos in a separate window if no values are put in. Defaults to None.
            frame (np.ndarray, optional): Shows the frame on the window. Defaults to None. Priority over id.

        Returns:
            bool: True if the window is still open, False if the window is closed (q pressed)
        """
        if id is None and frame is None:
            for i in range(len(self.videos)):
                cv2.imshow(self.videos[i], self.frames[i])
                if cv2.waitKey(1) == ord('q'):
                    return False
            return True
        elif frame is None:
            i = self.videos.index(id)
            cv2.imshow(id, self.frames[i])
            if cv2.waitKey(1) == ord('q'):
                return False
            return True
        else:
            cv2.imshow(id, frame)
            if cv2.waitKey(1) == ord('q'):
                return False
            return True

    def update_all_frames(self):
        self.time += 1 / FPS
        for i in range(len(self.videos)):
            new_frame, fetched = self.get_frame(i)
            if fetched:
                self.frames[i] = new_frame
        if self.time > self.duration:
            return False
        return True

    def close(self):
        for stream in self.streams:
            stream.stop()
        cv2.destroyAllWindows()
        return True


if __name__ == "__main__":
    vt = VideoTransition("aespa", "savage")
    while True:
        if not vt.update_all_frames():
            break
        if not vt.display_frame(vt.videos[0], vt.frames[0]):
            break
    print("Done")
    vt.close()
