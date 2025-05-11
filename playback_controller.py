import threading
import time
from loopgen import LoopGen

class PlaybackController:
    def __init__(self):
        self.is_playing = False
        self.stop_event = threading.Event()
        self.thread = None

    def start(self, loopgen_params_generator):
        if not self.is_playing:
            self.is_playing = True
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.play_continuous, args=(loopgen_params_generator,))
            self.thread.start()

    def stop(self):
        self.is_playing = False
        self.stop_event.set()
        if self.thread:
            self.thread.join()

    def play_continuous(self, params_generator):
        while not self.stop_event.is_set():
            params = next(params_generator)
            loop = LoopGen(params)
            duration = loop.generate()  # Generate and return real duration of the loop

            playback_thread = threading.Thread(target=loop.play_midi, args=("loopgen_output.mid",))
            playback_thread.start()

            # Smart waiting loop to frequently check for Stop event
            wait_time = max(0, duration - 0.5)  # Overlap adjustment
            check_interval = 0.1  # Check every 100ms
            elapsed = 0

            while elapsed < wait_time and not self.stop_event.is_set():
                time.sleep(check_interval)
                elapsed += check_interval

            playback_thread.join()

        self.is_playing = False  # Ensure state resets when exiting loop