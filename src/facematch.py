from cgi import test
import src.videotransition as videotransition
import src.poseestimator as poseestimator
import cv2
import matplotlib.pyplot as plt

# Constants
TEST_ARTIST = "newjeans"
TEST_TITLE = "attention"


def face_area(face_landmarks):
    left_eye = face_landmarks[33]
    right_eye = face_landmarks[263]
    nose = face_landmarks[94]

    area_face = 1/2 * abs(left_eye.x * right_eye.y + right_eye.x * nose.y + nose.x * left_eye.y - left_eye.y * right_eye.x - right_eye.y * nose.x - nose.y * left_eye.x)

    return area_face

def face_nose(face_landmarks):
    return face_landmarks[94]

def face_left_eye(face_landmarks):
    return face_landmarks[33]

def face_right_eye(face_landmarks):
    return face_landmarks[263]

def face_coords(face_landmarks):
    left_eye = face_landmarks[33]
    right_eye = face_landmarks[263]
    nose = face_landmarks[94]

    return ((left_eye.x, left_eye.y), (right_eye.x, right_eye.y), (nose.x, nose.y))

def face_normalize(face_landmarks):
    left_eye = face_landmarks[33]
    right_eye = face_landmarks[263]
    nose = face_landmarks[94]

    landmarks = []

    for i in range(len(face_landmarks)):
        face_landmarks_x = (face_landmarks[i].x - nose.x) / (right_eye.x - left_eye.x)
        face_landmarks_y = (face_landmarks[i].y - nose.y) / (right_eye.y - left_eye.y)

        landmarks.append((face_landmarks_x, face_landmarks_y))

    return landmarks

def face_similarity(face_landmarks_1, face_landmarks_2):
    face_normalized_1 = face_normalize(face_landmarks_1)
    face_normalized_2 = face_normalize(face_landmarks_2)

    error = 0

    for i in range(len(face_normalized_1)):
        error += (face_normalized_1[i][0] - face_normalized_2[i][0]) ** 2 + (face_normalized_1[i][1] - face_normalized_2[i][1]) ** 2

    return error
    


def get_facematch(artist, title):
    vt = videotransition.VideoTransition(artist, title)
    pe = poseestimator.PoseEstimator(pose=False, face_mesh=True,
                       face_detection=False, bounding_box=False)

    log_face_area = [[] for i in range(len(vt.videos))]
    log_face_coords_x = [[] for i in range(len(vt.videos))]
    log_face_coords_y = [[] for i in range(len(vt.videos))]
    log_face_match = {}

    face_meshes = [None for _ in range(len(vt.videos))]

    while True:
        if not vt.update_all_frames():
            break

        valid_face_meshes = [None for _ in range(len(vt.videos))]

        for i, frame in enumerate(vt.frames):
            face_meshes[i] = pe.get_face_mesh(vt.frames[i])
            faces = face_meshes[i].multi_face_landmarks

            if faces is not None:
                if len(faces) == 1:
                    face_landmarks = faces[0].landmark
                    area = face_area(face_landmarks)
                    nose = face_nose(face_landmarks)
                    log_face_area[i].append(area)
                    log_face_coords_x[i].append(nose.x)
                    log_face_coords_y[i].append(nose.y)
                    if area > 0.002 and nose.x > 0.3 and nose.y < 0.7:
                        valid_face_meshes[i] = face_landmarks
                        # print("Valid face")
                else:
                    log_face_area[i].append(0)
                    log_face_coords_x[i].append(0)
                    log_face_coords_y[i].append(0)
            else:
                log_face_area[i].append(0)
                log_face_coords_x[i].append(0)
                log_face_coords_y[i].append(0)

        filtered_meshes_index = [i for i in range(len(vt.videos)) if valid_face_meshes[i] is not None]

        match_candidate = []

        if len(filtered_meshes_index) >= 2:
            for i in range(len(filtered_meshes_index)):
                for j in range(i + 1, len(filtered_meshes_index)):
                    index_1, index_2 = filtered_meshes_index[i], filtered_meshes_index[j]
                    face_landmarks_1 = valid_face_meshes[index_1]
                    face_landmarks_2 = valid_face_meshes[index_2]
                    similarity = face_similarity(face_landmarks_1, face_landmarks_2)
                    match_candidate.append((similarity, (index_1, face_coords(face_landmarks_1)), (index_2, face_coords(face_landmarks_2))))
        
            min_error_pair = min(match_candidate, key=lambda x: x[0])

            if min_error_pair[0] < 5000:
                print("Match found")
                print("Error: " + str(min_error_pair[0]))
                print("Frame: " + str(min_error_pair[1]))
                print("Frame: " + str(min_error_pair[2]))
                log_face_match[vt.global_index] = (min_error_pair[1], min_error_pair[2])
                


        # if valid_face_meshes[0] is not None and valid_face_meshes[1] is not None:
        #     similarity = face_similarity(valid_face_meshes[0], valid_face_meshes[1])
        #     log_face_similarity.append(similarity)
        #     # print(similarity)

        #     if similarity < 5000:
        #         print("Face Matches")
        #         print("Similarity: {}".format(similarity))

        # else:
        #     log_face_similarity.append(0)


        # test_frame = vt.frames[0]

        # face_meshes = pe.get_face_mesh(test_frame)
        # faces = face_meshes.multi_face_landmarks
        # if faces is not None:
        #     face_num = len(faces)

        #     if face_num == 1:
        #         face_landmarks = faces[0].landmark
        #         area = face_area(face_landmarks)

        #         print(area)

        #         log_face_area.append(area)

        #         if area > 0.002:

        #             for i in range(len(faces[0].landmark)):

        #                 landmark = faces[0].landmark[i]

        #                 if i in [33, 263, 94]:
        #                     cv2.circle(test_frame, (int(landmark.x  * test_frame.shape[1]), int(landmark.y * test_frame.shape[0])), 1, (0, 0, 255), -1)
        #                 else:
        #                     cv2.circle(test_frame, (int(landmark.x  * test_frame.shape[1]), int(landmark.y * test_frame.shape[0])), 1, (0, 255, 0), -1)

        #             log_face_coords_x.append(face_nose(face_landmarks).x)
        #             log_face_coords_y.append(face_nose(face_landmarks).y)

        #         else:
        #             log_face_coords_x.append(0)
        #             log_face_coords_y.append(0)

        if not vt.display_frame():
            break

    vt.close()
    # plt.subplot(3, 1, 1)
    # plt.plot(log_face_similarity)
    # plt.title("Face Error")
    # plt.subplot(3, 1, 2)
    # plt.plot(log_face_coords_x[0])
    # plt.title("Nose X_1")
    # plt.subplot(3, 1, 3)
    # plt.plot(log_face_coords_x[1])
    # plt.title("Nose X_2")
    # plt.show()

    return log_face_match
    
def main():
    face_match = get_facematch(TEST_ARTIST, TEST_TITLE)
    print(face_match)

if __name__ == "__main__":
    main()


