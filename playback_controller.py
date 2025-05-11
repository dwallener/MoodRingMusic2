import threading
import time
from loopgen import LoopGen

class PlaybackController:
    def __init__(self):
        self.is_playing = False
        self.thread = None

    def start(self, loopgen_params_generator):
        if not self.is_playing:
            self.is_playing = True
            self.thread = threading.Thread(target=self.play_continuous, args=(loopgen_params_generator,))
            self.thread.start()

    def stop(self):
        self.is_playing = False
        if self.thread:
            self.thread.join()

    def play_continuous(self, params_generator):
        while self.is_playing:
            # Step 1: Pre-Generate the Next Loop
            params = next(params_generator)
            loop = LoopGen(params)
            duration = loop.generate()  # Returns real duration of the loop

            # Step 2: Start Playback in a Separate Thread
            playback_thread = threading.Thread(target=loop.play_midi, args=("loopgen_output.mid",))
            playback_thread.start()

            # Step 3: Pre-buffer Timing - Start Next Loop Slightly Before Current Ends
            overlap_time = 0.5  # Seconds to overlap transitions (tweak this if needed)
            wait_time = max(0, duration - overlap_time)

            time.sleep(wait_time)  # Wait while current loop plays

            # Step 4: Ensure Playback Finishes Before Moving On
            playback_thread.join()

            # If stopped during sleep or playback, break immediately
            if not self.is_playing:
                break