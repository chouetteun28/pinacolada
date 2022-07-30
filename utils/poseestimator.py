import mediapipe as mp
import utils.videotransition as videotransition
import cv2

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh

with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, min_tracking_confidence=0.5,model_complexity=2, ) as pose:
    with mp_face_mesh.FaceMesh(max_num_faces=5, refine_landmarks=True, min_detection_confidence=0.4,min_tracking_confidence=0.5) as face_mesh:
        vt = videotransition.VideoTransition("aespa", "savage")
        while True:
            vt.update_all_frames()
            frame = cv2.cvtColor(vt.frames[0], cv2.COLOR_BGR2RGB)
            pose_results = pose.process(frame)
            face_mesh_results = face_mesh.process(vt.frames[0])
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                frame, 
                pose_results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            if face_mesh_results.multi_face_landmarks:
                for face_landmarks in face_mesh_results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_tesselation_style())
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_contours_style())
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_iris_connections_style())
            if not vt.display_frame(frame=frame):
                break

    vt.close()