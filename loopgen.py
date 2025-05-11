import mido
import streamlit as st
import time
import fluidsynth

NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9,
    'A#': 10, 'Bb': 10, 'B': 11
}

class LoopGen:
    def __init__(self, params: dict):
        self.simulated_hour = params.get("simulated_hour", 0)
        self.circadian_phase = params.get("circadian_phase", "Unknown")
        self.bpm = params.get("bpm", 120)
        self.chord_progression = params.get("chord_progression", "I-IV-V-I")
        self.scale = params.get("scale", "Major")
        self.key = params.get("key", "C")
        self.instruments = params.get("instruments", [])
        self.print_parameters()
        
    def print_parameters(self):
        st.write("🎵 **LoopGen Parameters Loaded:**")
        st.write(f"• Simulated Hour: {self.simulated_hour}")
        st.write(f"• Circadian Phase: {self.circadian_phase}")
        st.write(f"• BPM: {self.bpm}")
        st.write(f"• Chord Progression: {self.chord_progression}")
        st.write(f"• Scale: {self.scale}")
        st.write(f"• Key: {self.key}")
        st.write(f"• Instruments: {self.instruments}")

    # Play the generated MIDI
    def play_midi(self, file_path):
        fs = fluidsynth.Synth()
        fs.start(driver="coreaudio")  # On MacOS, use 'coreaudio'; for Windows/Linux, try 'dsound' or 'alsa'
        sfid = fs.sfload("soundfonts/FluidR3_GM.sf2")  # Adjust path if needed
        fs.program_select(0, sfid, 0, 0)

        mid = mido.MidiFile(file_path)
        for msg in mid.play():
            if msg.type == 'note_on':
                fs.noteon(0, msg.note, msg.velocity)
            elif msg.type == 'note_off':
                fs.noteoff(0, msg.note)
            elif msg.type == 'program_change':
                fs.program_change(0, msg.program)
            time.sleep(msg.time)

        fs.delete()

    # generate the midi
    def generate(self):
        ticks_per_beat = 480
        tempo = mido.bpm2tempo(self.bpm)
        mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        # Instrument setup
        instrument_program = self.instruments[0] if self.instruments else 0
        track.append(mido.Message('program_change', program=instrument_program, time=0))

        # Build Notes
        scale_notes = self.get_scale_notes(self.key, self.scale)
        chord_notes = self.get_chord_notes(scale_notes, self.chord_progression)

        for chord in chord_notes:
            for note in chord:
                track.append(mido.Message('note_on', note=note, velocity=64, time=0))
            # Hold chord for a full beat (ticks_per_beat)
            for note in chord:
                track.append(mido.Message('note_off', note=note, velocity=64, time=ticks_per_beat))

        # Save MIDI
        output_file = "loopgen_output.mid"
        mid.save(output_file)
        st.success(f"🎶 MIDI file generated: `{output_file}`")
        self.play_midi(output_file)

    def get_scale_notes(self, key, scale_name):
        semitone_steps = {
            "Major": [0, 2, 4, 5, 7, 9, 11],
            "Minor": [0, 2, 3, 5, 7, 8, 10],
            "Pentatonic": [0, 2, 4, 7, 9],
            "Dorian": [0, 2, 3, 5, 7, 9, 10],
            "Mixolydian": [0, 2, 4, 5, 7, 9, 10],
            "Lydian": [0, 2, 4, 6, 7, 9, 11],
            "Aeolian": [0, 2, 3, 5, 7, 8, 10],
            "Phrygian": [0, 1, 3, 5, 7, 8, 10],
            "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11]
        }
        steps = semitone_steps.get(scale_name, semitone_steps["Major"])
        key_base = NOTE_TO_MIDI.get(key.replace(" Minor", "").replace(" Major", ""), 0) + 60  # Middle octave
        return [key_base + step for step in steps]

    def get_chord_notes(self, scale_notes, progression):
        numeral_map = {
            "I": 0, "ii": 1, "iii": 2, "IV": 3, "V": 4, "vi": 5, "vii": 6
        }
        chords = []
        progression_parts = progression.replace('-', ' ').split()
        for numeral in progression_parts:
            degree = numeral_map.get(numeral, 0)
            root = scale_notes[degree % len(scale_notes)]
            third = scale_notes[(degree + 2) % len(scale_notes)]
            fifth = scale_notes[(degree + 4) % len(scale_notes)]
            chords.append([root, third, fifth])
        return chords