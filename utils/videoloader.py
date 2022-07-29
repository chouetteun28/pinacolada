import utils.database as database
from vidgear.gears import CamGear
import cv2

db = database.AssetDatabase()

id = list(db.assets.keys())[1]

videos, audio = db.filter_asset("aespa", "savage")

stream = CamGear(
    source=db.get_video_path(videos[0]),
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
