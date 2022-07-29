from audioop import avg
from multiprocessing import pool
import matplotlib
import utils.database as database
import pydub
import pydub.playback
import array
import numpy as np
import matplotlib.pyplot as plt

SAMPLE_FREQ = 44100
KERNEL_SIZE = 500
POOL_TIME = 100


def avg_pool(arr: np.ndarray):
    """average pooling of the array

    Args:
        arr (np.ndarray): array to be averaged
    """
    total_steps = POOL_TIME * SAMPLE_FREQ
    steps = total_steps // KERNEL_SIZE
    total_steps = steps * KERNEL_SIZE
    return np.average(arr[:total_steps].reshape(-1, KERNEL_SIZE), axis=1)


def syncAudio(artist, song):
    """Sync the audio of the video with the audio of the song

    Args:
        artist (str): Music artist(without space, lowercase)
        song (str): Name of the song(without space, lowercase)

    Returns:
        void: None
    """
    db = database.AssetDatabase()
    videos, audio = db.filter_asset(artist, song)
    if len(videos) == 0:
        print("[AudioSync] No videos found for this song")
        return -1
    if not audio:
        print("[AudioSync] No audio found for this song")
        return -1
    for video in videos:
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

        # plot_amplitude(original)
        # plt.subplot(2, 1, 1)
        # plt.plot(np.linspace(0.0, POOL_TIME, original.shape[0]),original)
        # plt.subplot(2, 1, 2)
        # plt.plot(np.linspace(0.0, POOL_TIME, sound.shape[0]),sound)
        # plt.show()

        corr = np.correlate(original, sound, mode='full')
        # plt.plot(np.linspace(0, POOL_TIME, int(POOL_TIME*44100/KERNEL_SIZE)), corr[0:original.shape[0]])
        # plt.show()

        delta_t = POOL_TIME - np.argmax(corr)*KERNEL_SIZE/44100
        db.set_offset(video, delta_t)
        db.log_assets(video)


if __name__ == "__main__":
    syncAudio("gidle", "tomboy")
