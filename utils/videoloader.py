import downloader
from vidgear.gears import CamGear
import cv2

db = downloader.AssetDatabase()

id = list(db.assets.keys())[0]

stream = CamGear(
    source = db.getVideoPath(id),
).start()

while True:
    frame = stream.read()
    if frame is None:
        break

    # invert image color
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 1)
    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
stream.stop()