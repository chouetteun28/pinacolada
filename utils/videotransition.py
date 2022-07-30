import utils.database as database
from vidgear.gears import CamGear
import cv2
import numpy as np

"""
Only works with 30fps videos
"""
FPS = 30

class VideoTransition:
    def __init__(self, artist, song):
        db = database.AssetDatabase()
        videos, audio = db.filter_asset(artist, song)
        self.videos = videos
        self.audio = audio
        self.streams = [CamGear(source=db.get_video_path(id)).start() for id in videos ]
        self.frames = [None for _ in videos]
        self.frame_nums = [0 for _ in videos]
        self.offsets = [db.get_offset(id) for id in videos]
        self.is_loading = [False for _ in videos]
        self.placeholder = np.zeros((720, 480, 3), dtype=np.uint8)
        self.time = 0

        # match syncronization of videos
        for i in range(len(self.videos)):
            if self.offsets[i] > 0:
                for _ in range(int(self.offsets[i]*FPS)):
                    self.get_frame(i)
            elif self.offsets[i] < 0:
                self.frames[i] = self.placeholder
        
    def get_frame(self, i):
        if self.time + self.offsets[i] > 0:
            self.frame_nums[i] += 1
            frame = self.streams[i].read()
            if frame is None:
                return -1, False
            return frame, True
        return self.placeholder, True

    def display_frame(self):
        for i in range(len(self.videos)):
            cv2.imshow("frame" + self.videos[i], self.frames[i])
            if cv2.waitKey(1) == ord('q'):
                return False
        return True

    def update_all_frames(self):
        self.time += 1 / FPS
        print(self.time)
        print(self.frame_nums)
        for i in range(len(self.videos)):
            new_frame, fetched = self.get_frame(i)
            if fetched:  
                self.frames[i] = new_frame
        if not self.display_frame():
            return False
        return True

if __name__ == "__main__":
    vt = VideoTransition("ive", "lovedive")
    while vt.update_all_frames():
        pass
    print("Done")
    cv2.destroyAllWindows()