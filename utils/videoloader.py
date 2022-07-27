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

    cv2.imshow("frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
stream.stop()