import threading
import time
from loopgen import LoopGen

class PlaybackController:
    def __init__(self):
        self.is_playing = False
        self.stop_event = threading.Event()
        self.thread = None
        self.event_log = []  # Local log instead of using st.session_state directly

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

    def log_event(self, key, bpm):
        timestamp = time.strftime("%H:%M:%S")
        self.event_log.append((timestamp, key, bpm))
        if len(self.event_log) > 20:
            self.event_log.pop(0)

    def play_continuous(self, params_generator):
        current_key = None

        while not self.stop_event.is_set():
            params = next(params_generator)
            new_key = params.get("key", "Unknown")
            bpm = params.get("bpm", "Unknown")

            if current_key and new_key != current_key:
                self.log_event(new_key, bpm)
            else:
                self.log_event(new_key, bpm)

            current_key = new_key

            loop = LoopGen(params)
            duration = loop.generate()

            playback_thread = threading.Thread(target=loop.play_midi, args=("loopgen_output.mid",))
            playback_thread.start()

            wait_time = max(0, duration - 0.5)
            check_interval = 0.1
            elapsed = 0

            while elapsed < wait_time and not self.stop_event.is_set():
                time.sleep(check_interval)
                elapsed += check_interval

            playback_thread.join()

        self.is_playing = False