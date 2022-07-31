import mediapipe as mp
import src.videotransition as videotransition
import cv2
import torch

class PoseEstimator:
    def __init__(self, pose = True, face_mesh = True, face_detection = True, bounding_box = True):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.ifpose = pose
        self.iffacemesh = face_mesh
        self.iffacedetection = face_detection
        self.ifboundingbox = bounding_box
        if self.ifpose:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5,model_complexity=2)
        if self.iffacemesh:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=5, refine_landmarks=True, min_detection_confidence=0.3,min_tracking_confidence=0.5)
        if self.iffacedetection:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.2)
        if self.ifboundingbox:
            self.boundingbox_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

    def get_pose(self, frame):
        return self.pose.process(frame)
    
    def get_face_mesh(self, frame):
        return self.face_mesh.process(frame)

    def get_face_detection(self, frame):
        return self.face_detection.process(frame)
    
    def get_boundingbox(self, frame):
        results = self.boundingbox_model(frame)
        df = results.pandas().xyxy[0]
        return df

    def draw_pose(self, frame, results):
        self.mp_drawing.draw_landmarks(
            frame, 
            results.pose_landmarks, 
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())

    def draw_face_mesh(self, frame, results):
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_tesselation_style())
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_contours_style())
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_iris_connections_style())
    
    def draw_face_detection(self, frame, results):
        if results.detections:
            for detection in results.detections:
                self.mp_drawing.draw_detection(
                    frame, detection)
    
    def draw_boundingbox(self, frame, results):
        for index, row in results.iterrows():
            if row['confidence'] > 0.5 and row['name'] == 'person':
                cv2.rectangle(frame, (int(row['xmin']), int(row['ymin'])), (int(row['xmax']), int(row['ymax'])), (0, 255, 0), 2)

    def process(self, frame, draw_pose=True, draw_face_mesh=True, draw_face_detection=True, draw_boundingbox=True):
        if self.ifpose:
            result = self.get_pose(frame)
            if draw_pose:
                self.draw_pose(frame, result)
        if self.iffacemesh:
            result = self.get_face_mesh(frame)
            if draw_face_mesh:
                self.draw_face_mesh(frame, result)
        if self.iffacedetection:
            result = self.get_face_detection(frame)
            if draw_face_detection:
                self.draw_face_detection(frame, result)
        if self.ifboundingbox:
            result = self.get_boundingbox(frame)
            if draw_boundingbox:
                self.draw_boundingbox(frame, result)
        return frame

    def close(self):
        self.pose.close()
        self.face_mesh.close()
        self.face_detection.close()
        self.boundingbox_model.close()

    def __del__(self):
        self.close()
        return 0
    
if __name__ == "__main__":
    vt = videotransition.VideoTransition("aespa", "savage")
    pe = PoseEstimator(pose = True, face_mesh = True, face_detection = True, bounding_box = True)
    while True:
        if not vt.update_all_frames():
            break
        frame = cv2.cvtColor(vt.frames[0], cv2.COLOR_BGR2RGB)
        frame = pe.process(frame, draw_pose = True, draw_face_mesh = True, draw_face_detection = True, draw_boundingbox = True)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if not vt.display_frame(frame=frame):
            break
    vt.close()
    pe.close()
    print("Done")