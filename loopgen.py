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
        self.simulated_hour = params.get("simulated_hour", 0)
        self.circadian_phase = params.get("circadian_phase", "Unknown")
        self.bpm = params.get("bpm", 120)
        self.chord_progression = params.get("chord_progression", "I-IV-V-I")
        self.scale = params.get("scale", "Major")
        self.key = params.get("key", "C")
        self.instruments = params.get("instruments", [])
        self.print_parameters()
        
    def get_midi_duration(self, midi_file_path):
        mid = mido.MidiFile(midi_file_path)
        return mid.length  # Returns duration in seconds

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

    # create unique melodic sequences
    def generate_melody_sequence(self, scale_notes, length, rhythm, start_note=None):
        sequence = []
        current_note = start_note or random.choice(scale_notes)

        # Define some simple motifs
        motifs = [
            [0, 2, 4],        # Ascending steps
            [0, -2, -4],      # Descending steps
            [0, 1, -1],       # Step up, then down (turn)
            [0, 2, -1],       # Ascend then descend
            [0, -3, 1],       # Leap down, step up
        ]

        for _ in range(length):
            if _ % 2 == 0:
                motif = random.choice([[0, 2, 4], [0, 1, -1]])  # "Call" motifs
            else:
                motif = random.choice([[0, -2, -4], [0, -1, 1]])  # "Response" motifs            
            # motif = random.choice(motifs)
            for interval in motif:
                next_index = scale_notes.index(current_note) + interval
                next_index = max(0, min(next_index, len(scale_notes) - 1))
                current_note = scale_notes[next_index]
                sequence.append(current_note)

        # Limit to requested length
        return sequence[:length]

    # generate the midi
    def generate(self):
        ticks_per_beat = 480
        tempo = mido.bpm2tempo(self.bpm)
        mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)

        chord_track = mido.MidiTrack()
        melody_track = mido.MidiTrack()
        mid.tracks.append(chord_track)
        mid.tracks.append(melody_track)

        # Instruments
        chord_instrument = self.instruments[0] if self.instruments else 0
        melody_instrument = self.instruments[1] if len(self.instruments) > 1 else (chord_instrument + 1) % 128  # Ensure it's different

        # Assign instruments to separate channels
        chord_track.append(mido.Message('program_change', program=chord_instrument, channel=0, time=0))
        melody_track.append(mido.Message('program_change', program=melody_instrument, channel=1, time=0))

        scale_notes = self.get_scale_notes(self.key, self.scale)
        chord_notes = self.get_chord_notes(scale_notes, self.chord_progression)

        # Chord Sequence on Channel 0
        for chord in chord_notes:
            for note in chord:
                chord_track.append(mido.Message('note_on', note=note, velocity=50, time=0, channel=0))
            for note in chord:
                chord_track.append(mido.Message('note_off', note=note, velocity=50, time=ticks_per_beat, channel=0))
        
        # Melody Sequence on Channel 1
        melody_rhythm = [ticks_per_beat // 2, ticks_per_beat // 4, ticks_per_beat // 4]
        melody_sequence = self.generate_melody_sequence(scale_notes, len(chord_notes) * 2, melody_rhythm)

        for note in melody_sequence:
            for duration in melody_rhythm:
                melody_track.append(mido.Message('note_on', note=note, velocity=100, time=0, channel=1))  # Louder melody
                melody_track.append(mido.Message('note_off', note=note, velocity=100, time=duration, channel=1))

        # Bass Sequence - Select Instruments
        bass_track = mido.MidiTrack()
        mid.tracks.append(bass_track)
        bass_instrument = self.instruments[2] if len(self.instruments) > 2 else 33  # Default to Acoustic Bass if not enough instruments

        # Assign bass instrument to Channel 2
        bass_track.append(mido.Message('program_change', program=bass_instrument, channel=2, time=0))

        # Generate Bass Line - Root notes of each chord, dropped by 1-2 octaves

        # Generate Bass Line - More Lively!
        for chord in chord_notes:
            root = chord[0] - 12  # One octave lower
            root = max(36, root)

            # Root-Octave Pulse
            octave = root + 12
            bass_track.append(mido.Message('note_on', note=root, velocity=80, time=0, channel=2))
            bass_track.append(mido.Message('note_off', note=root, velocity=80, time=ticks_per_beat // 2, channel=2))

            bass_track.append(mido.Message('note_on', note=octave, velocity=80, time=0, channel=2))
            bass_track.append(mido.Message('note_off', note=octave, velocity=80, time=ticks_per_beat // 2, channel=2))

            # Walking Bass: Add a passing note (next scale degree up)
            next_note = root + 2  # Whole step up
            bass_track.append(mido.Message('note_on', note=next_note, velocity=70, time=0, channel=2))
            bass_track.append(mido.Message('note_off', note=next_note, velocity=70, time=ticks_per_beat // 2, channel=2))

            # Resolve back to root
            bass_track.append(mido.Message('note_on', note=root, velocity=90, time=0, channel=2))
            bass_track.append(mido.Message('note_off', note=root, velocity=90, time=ticks_per_beat // 2, channel=2))

        output_file = "loopgen_output.mid"
        mid.save(output_file)
        duration = self.get_midi_duration(output_file)
        st.success(f"🎶 MIDI file generated: `{output_file}`")

        self.play_midi(output_file
        )
        return duration 
        
    # 
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