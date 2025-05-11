import mido
import streamlit as st
import time
import fluidsynth
import random

NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9,
    'A#': 10, 'Bb': 10, 'B': 11
}

class LoopGen:
    def __init__(self, params: dict):
        self.params = params
        self.simulated_hour = params.get("simulated_hour", 0)
        self.circadian_phase = params.get("circadian_phase", "Unknown")
        self.bpm = params.get("bpm", 120)
        self.chord_progression = params.get("chord_progression", "I-IV-V-I")
        self.scale = params.get("scale", "Major")
        self.key = params.get("key", "C")
        self.instruments = params.get("instruments", [])
        self.phrase_length = params.get("phrase_length", 8)
        self.print_parameters()

    def print_parameters(self):
        st.write("🎵 **LoopGen Parameters Loaded:**")
        for k, v in self.params.items():
            st.write(f"• {k.replace('_', ' ').title()}: {v}")

    def play_midi(self, file_path):
        fs = fluidsynth.Synth()
        fs.start(driver="coreaudio")
        sfid = fs.sfload("soundfonts/FluidR3_GM.sf2")
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

    def generate_melody_sequence(self, scale_notes, length, rhythm, upcoming_key=None):
        sequence = []
        current_note = random.choice(scale_notes)
        pivot_zone = length // 4

        if upcoming_key:
            next_scale_notes = self.get_scale_notes(upcoming_key, self.scale)
            common_notes = list(set(scale_notes) & set(next_scale_notes))
        else:
            common_notes = []

        for i in range(length):
            if upcoming_key and i >= (length - pivot_zone) and common_notes:
                current_note = random.choice(common_notes)
            else:
                move = random.choices([-2, -1, 1, 2, -3, 3], weights=[10, 30, 30, 10, 10, 10])[0]
                next_index = scale_notes.index(current_note) + move
                next_index = max(0, min(next_index, len(scale_notes) - 1))
                current_note = scale_notes[next_index]

            sequence.append(current_note)
        return sequence

    def generate(self):
        ticks_per_beat = 480
        mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
        chord_track = mido.MidiTrack()
        melody_track = mido.MidiTrack()
        bass_track = mido.MidiTrack()
        mid.tracks.extend([chord_track, melody_track, bass_track])

        chord_instr = self.instruments[0] if self.instruments else 0
        melody_instr = self.instruments[1] if len(self.instruments) > 1 else (chord_instr + 1) % 128
        bass_instr = self.instruments[2] if len(self.instruments) > 2 else 33

        chord_track.append(mido.Message('program_change', program=chord_instr, channel=0, time=0))
        melody_track.append(mido.Message('program_change', program=melody_instr, channel=1, time=0))
        bass_track.append(mido.Message('program_change', program=bass_instr, channel=2, time=0))

        scale_notes = self.get_scale_notes(self.key, self.scale)
        current_key = self.key
        progression_sections = self.chord_progression.split('-')

        for section in progression_sections:
            upcoming_key = current_key
            if "bridge" in section and random.random() < 0.5:
                # Key Change!
                possible_keys = [k for k in NOTE_TO_MIDI if k != current_key]
                if possible_keys:
                    upcoming_key = random.choice(possible_keys)

            # Chords
            chord = self.get_chord_notes(scale_notes, section.strip())
            for note in chord:
                chord_track.append(mido.Message('note_on', note=note, velocity=50, time=0, channel=0))
            for note in chord:
                chord_track.append(mido.Message('note_off', note=note, velocity=50, time=ticks_per_beat, channel=0))

            # Melody
            melody_rhythm = [ticks_per_beat // 2, ticks_per_beat // 4, ticks_per_beat // 4]
            melody_len = self.phrase_length * 2
            melody_seq = self.generate_melody_sequence(scale_notes, melody_len, melody_rhythm, upcoming_key)

            for note in melody_seq:
                for duration in melody_rhythm:
                    melody_track.append(mido.Message('note_on', note=note, velocity=100, time=0, channel=1))
                    melody_track.append(mido.Message('note_off', note=note, velocity=100, time=duration, channel=1))

            # Bass Pivot
            pivot_zone = self.phrase_length // 4
            for i in range(self.phrase_length):
                bass_note = chord[0] - 12 if i < (self.phrase_length - pivot_zone) else chord[0]
                bass_note = max(36, bass_note)
                bass_track.append(mido.Message('note_on', note=bass_note, velocity=80, time=0, channel=2))
                bass_track.append(mido.Message('note_off', note=bass_note, velocity=80, time=ticks_per_beat, channel=2))

            current_key = upcoming_key
            scale_notes = self.get_scale_notes(current_key, self.scale)

        output_file = "loopgen_output.mid"
        mid.save(output_file)
        st.success(f"🎶 MIDI file generated with melody and bass: `{output_file}`")

        self.play_midi(output_file)
        return mid.length  # Return duration for the playback controller

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
        key_base = NOTE_TO_MIDI.get(key.replace(" Minor", "").replace(" Major", ""), 0) + 60
        return [key_base + step for step in steps]

    def get_chord_notes(self, scale_notes, numeral):
        numeral_map = {"I": 0, "ii": 1, "iii": 2, "IV": 3, "V": 4, "vi": 5, "vii": 6}
        degree = numeral_map.get(numeral, 0)
        root = scale_notes[degree % len(scale_notes)]
        third = scale_notes[(degree + 2) % len(scale_notes)]
        fifth = scale_notes[(degree + 4) % len(scale_notes)]
        return [root, third, fifth]