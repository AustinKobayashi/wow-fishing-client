import pyaudio
import numpy as np
import time
import traceback
import logger as lg
import servo_client as sv
import normal_distribution as nd

# Configuration
FORMAT = pyaudio.paInt16  # Format of audio data (16-bit)
CHANNELS = 1              # Number of audio channels (1 for mono)
RATE = 44100              # Sample rate (samples per second)
THRESHOLD = 3000          # Adjust this threshold as needed
CHECK_INTERVAL = 0.01     # Check interval in seconds

REEL_TIME_MIN = 0.985
REEL_TIME_MAX = 4
REEL_TIME_TAIL_PROBABILITY = 0.0005
REEL_TIME_MEAN_MAX_MODIFIER = 0.4
REEL_TIME_UNDER_MIN_MODIFIER = 10

CAST_TIME_MIN = 0.985
CAST_TIME_MAX = 3
CAST_TIME_TAIL_PROBABILITY = 0.0000005
CAST_TIME_MEAN_MAX_MODIFIER = 0.6
CAST_TIME_UNDER_MIN_MODIFIER = 0.3

LAST_CAST_MAX = 60

IDLE_TIME_MIN = 10
IDLE_TIME_MAX = 120
IDLE_PROBABILITY = 0.0023

MAX_RUN_TIME = 60 * 60 * 5

DONT_REEL_TIME = 2.1

WOW_FISHING_TIME = 28
REEL_TIME_DELAY_AFTER_CAST = 1.5


def idle(min_duration, max_duration):
    sleep_duration = np.random.uniform(min_duration, max_duration)
    lg.log(f'Idle for {sleep_duration:.2f} seconds')
    time.sleep(sleep_duration)


def main(): 
    time.sleep(2)
    try:
        sv.set_neutral()
        
        start_time = time.time()
        last_cast_time = time.time()

        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=1024)
        while not stream.is_active():
            lg.log('Waiting for audio stream to be active')
            time.sleep(0.1)

        sv.press_fishing_button('Casting')

        while True:
            if time.time() - start_time > MAX_RUN_TIME:
                lg.log('Max run time reached, exiting...')
                break

            if time.time() - last_cast_time > LAST_CAST_MAX:
                lg.log('Did not cast, recasting...')
                sv.press_fishing_button('Casting')
                last_cast_time = time.time()

            time.sleep(0.01)

            audio_data = np.frombuffer(stream.read(1024), dtype=np.int16)

            audio_level = np.abs(audio_data).mean()

            if audio_level > THRESHOLD and time.time() - last_cast_time > REEL_TIME_DELAY_AFTER_CAST:
                lg.log(f'\t\tAudio level above threshold: {audio_level}')

                reel_time = nd.get_normal_distribution(REEL_TIME_MIN, REEL_TIME_MAX, REEL_TIME_TAIL_PROBABILITY, REEL_TIME_MEAN_MAX_MODIFIER, REEL_TIME_UNDER_MIN_MODIFIER)

                lg.log(f'Reel time: {reel_time}')
                time.sleep(reel_time)

                if (time.time() - last_cast_time) + reel_time < WOW_FISHING_TIME and reel_time < DONT_REEL_TIME:
                    sv.press_fishing_button('Reeling')
                else:
                    time.sleep(max(WOW_FISHING_TIME - (time.time() - last_cast_time), 0.3))

                if np.random.rand() < IDLE_PROBABILITY:
                    idle(IDLE_TIME_MIN, IDLE_TIME_MAX)
                    last_cast_time = time.time()

                cast_time = nd.get_normal_distribution(CAST_TIME_MIN, CAST_TIME_MAX, CAST_TIME_TAIL_PROBABILITY, CAST_TIME_MEAN_MAX_MODIFIER, CAST_TIME_UNDER_MIN_MODIFIER, reel_time)

                lg.log(f'Cast time: {cast_time}')
                time.sleep(cast_time)

                sv.press_fishing_button('Casting')

                last_cast_time = time.time()

            time.sleep(CHECK_INTERVAL)
    except Exception as e:
        print(e)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()


if __name__ == '__main__':
    main()
