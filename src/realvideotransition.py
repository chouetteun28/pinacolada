from cmath import sqrt
from tkinter import N
import src.videotransition as videotransition
import src.facematch as facematch
import cv2
import time
import numpy as np

TEST_ARTIST = "newjeans"
TEST_TITLE = "attention"

def main():

    matches = facematch.get_facematch(TEST_ARTIST, TEST_TITLE)
    vt = videotransition.VideoTransition(TEST_ARTIST, TEST_TITLE)

    current_index = 2
    interval_time = 0

    transitions = []

    for i in range(100000):
        if i in matches.keys():
            if interval_time >= 60:
                if current_index == matches[i][1][0]:
                    current_index = matches[i][0][0]
                    interval_time = 0
                    print(current_index)
                    print(i)
                    transitions.append((i, current_index, matches[i][1][1], matches[i][0][1]))
                elif current_index == matches[i][0][0]:
                    current_index = matches[i][1][0]
                    interval_time = 0
                    print(current_index)
                    print(i)
                    transitions.append((i, current_index, matches[i][0][1], matches[i][1][1]))
                else: 
                    interval_time += 1
            else:
                interval_time += 1
        else:
            interval_time += 1
    
    print(transitions)

    current_index = 2

    out = cv2.VideoWriter('./output.mp4', cv2.VideoWriter_fourcc(*'MP4V'), 30.0, (1280, 720))

    while True:
        vt.update_all_frames()
        is_transition = False
        for i in range(len(transitions)):
            if transitions[i][0] > vt.global_index and transitions[i][0] - 60 < vt.global_index:
                frame = vt.frames[current_index]
                trans_amount = 1 - ((transitions[i][0] - vt.global_index) / 60)
                x_offset = transitions[i][2][2][0] - transitions[i][3][2][0]
                y_offset = transitions[i][2][2][1] - transitions[i][3][2][1]
                print(transitions[i])

                aff = np.array([[1, 0, -x_offset * trans_amount * 1280], [0, 1, -y_offset * trans_amount * 720]])
                frame = cv2.warpAffine(frame, aff, (0,0))
                prev_eye_dist = sqrt((transitions[i][2][0][0] - transitions[i][2][1][0]) ** 2 + (transitions[i][2][0][1] - transitions[i][2][1][1]) ** 2).real
                next_eye_dist = sqrt((transitions[i][3][0][0] - transitions[i][3][1][0]) ** 2 + (transitions[i][3][0][1] - transitions[i][3][1][1]) ** 2).real
                scale = next_eye_dist / prev_eye_dist
                scale_factor = scale * trans_amount + 1 * (1 - trans_amount)
                aff = np.array([[scale_factor, 0, (1-scale_factor) * transitions[i][3][2][0] * trans_amount * 854], [0, scale_factor, (1-scale_factor) * transitions[i][3][2][1] * trans_amount * 720]])
                frame = cv2.warpAffine(frame, aff, (0,0))
                is_transition = True
            elif transitions[i][0] == vt.global_index:
                current_index = transitions[i][1]
                frame = vt.frames[current_index]
                is_transition = True
        if not is_transition:
            frame = vt.frames[current_index]
        out.write(frame)
        
        time.sleep(1 / 50)
        if not vt.display_frame(None, frame):
            break
    out.release()

    


if __name__ == "__main__":
    main()

