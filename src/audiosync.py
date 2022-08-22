from audioop import avg
from multiprocessing import pool
import matplotlib
import src.assetdatabase as assetdatabase
import pydub
import pydub.playback
import array
import numpy as np
import matplotlib.pyplot as plt

SAMPLE_FREQ = 44100
KERNEL_SIZE = 200
POOL_TIME = 120


def avg_pool(arr: np.ndarray):
    """average pooling of the array

    Args:
        arr (np.ndarray): array to be averaged
    """
    total_steps = POOL_TIME * SAMPLE_FREQ
    steps = total_steps // KERNEL_SIZE
    total_steps = steps * KERNEL_SIZE
    print(total_steps)
    return np.average(arr[:total_steps].reshape(-1, KERNEL_SIZE), axis=1)


def syncAudio(artist: str, song: str, plot: bool = False, skip_existing: bool = True):
    """Sync the audio of the video with the audio of the song

    Args:
        artist (str): Music artist(without space, lowercase)
        song (str): Name of the song(without space, lowercase)
        plot (bool, optional): if the plot should be shown. Defaults to False.
        skip_existing (bool, optional): if the video should be skipped if it already exists. Defaults to True.

    Returns:
        void: None
    """
    db = assetdatabase.AssetDatabase()
    videos, audio = db.filter_asset(artist, song)
    if len(videos) == 0:
        print("[AudioSync] No videos found for this song")
        return -1
    if not audio:
        print("[AudioSync] No audio found for this song")
        return -1
    for video in videos:
        if (db.assets[video]["offset"] != -1) and skip_existing:
            continue
        original = pydub.AudioSegment.from_file(
            db.get_audio_path(audio)).split_to_mono()
        sound = pydub.AudioSegment.from_file(
            db.get_audio_path(video)).split_to_mono()
        original = np.array(original[0].get_array_of_samples())
        sound = np.array(sound[0].get_array_of_samples())
        original = np.abs(original.astype(np.float32))
        sound = np.abs(sound.astype(np.float32))
        original = avg_pool(original)
        sound = avg_pool(sound)

        original = original - np.average(original)
        sound = sound - np.average(sound)

        if plot:
            plt.subplot(2, 1, 1)
            plt.plot(np.linspace(0.0, POOL_TIME, original.shape[0]), original)
            plt.subplot(2, 1, 2)
            plt.plot(np.linspace(0.0, POOL_TIME, sound.shape[0]), sound)
            plt.show()

        corr = np.correlate(original, sound, mode='full')

        if plot:
            plt.plot(np.linspace(-POOL_TIME, POOL_TIME,
                     int(POOL_TIME*SAMPLE_FREQ*2/KERNEL_SIZE)-1), corr)
            plt.show()

        delta_t = POOL_TIME - np.argmax(corr)*KERNEL_SIZE/44100
        db.set_offset(video, delta_t)
        db.log_assets(video)


if __name__ == "__main__":
    syncAudio("ive", "lovedive", True, False)
