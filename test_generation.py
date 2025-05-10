import streamlit as st
import random
import time
import mido
import fluidsynth
import threading

# ---- CONFIGURATION ----
SOUNDFONT_PATH = "soundfonts/FluidR3_GM.sf2"  # Assumed location

# ---- App State ----
if "looping" not in st.session_state:
    st.session_state.looping = False
if "loop_thread" not in st.session_state:
    st.session_state.loop_thread = None
if "stop_event" not in st.session_state:
    st.session_state.stop_event = threading.Event()
if "current_instrument" not in st.session_state:
    st.session_state.current_instrument = ""
if "current_bpm" not in st.session_state:
    st.session_state.current_bpm = 0

INSTRUMENT_SETS = {
    "Ambient": [88, 90, 91, 94, 95, 81, 82],
    "Jazz": [0, 1, 26, 27, 56, 57, 32, 33],
    "Electronic/EDM": [81, 82, 83, 88, 89, 90, 97, 98],
    "Pop": [0, 1, 25, 26, 80, 81]
}

GM_INSTRUMENT_NAMES = {
    0: "Acoustic Grand Piano", 1: "Bright Acoustic Piano", 25: "Acoustic Guitar (Nylon)",
    26: "Acoustic Guitar (Steel)", 32: "Acoustic Bass", 33: "Electric Bass (Finger)",
    56: "Trumpet", 57: "Trombone", 81: "Lead 1 (Square)", 82: "Lead 2 (Sawtooth)",
    88: "Pad 1 (New Age)", 89: "Pad 2 (Warm)", 90: "Pad 3 (Polysynth)",
    94: "FX 2 (Soundtrack)", 95: "FX 3 (Crystal)", 97: "FX 5 (Brightness)", 98: "FX 6 (Goblins)"
}

def get_instrument_name(program_number):
    return GM_INSTRUMENT_NAMES.get(program_number, f"Program {program_number}")

# ---- MIDI Generation ----
def generate_midi_file(filename, bpm=120, scale=[60, 62, 64, 65, 67, 69, 71], instrument=0):
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage('set_tempo', tempo=tempo))
    track.append(mido.Message('program_change', program=instrument, time=0))

    for _ in range(16):
        note = random.choice(scale)
        duration_beats = random.choice([1, 2])  # Quarter or half note
        duration_ticks = int(duration_beats * 480)
        track.append(mido.Message('note_on', note=note, velocity=80, time=0))
        track.append(mido.Message('note_off', note=note, velocity=80, time=duration_ticks))

    mid.save(filename)
    return mid.length  # Actual duration in seconds

def play_midi_file(filename, instrument_program):
    fs = fluidsynth.Synth()
    fs.start(driver="coreaudio")
    sfid = fs.sfload(SOUNDFONT_PATH)
    fs.program_select(0, sfid, 0, instrument_program)

    mid = mido.MidiFile(filename)
    for msg in mid.play():
        if msg.type == 'note_on':
            fs.noteon(0, msg.note, msg.velocity)
        elif msg.type == 'note_off':
            fs.noteoff(0, msg.note)

    fs.delete()

# ---- Loop Controller ----
def loop_playback(selected_style, stop_event):
    loop_count = 1
    last_instrument = None

    while not stop_event.is_set():
        instruments = INSTRUMENT_SETS.get(selected_style, [0])
        available_instruments = [i for i in instruments if i != last_instrument]
        instrument_program = random.choice(available_instruments) if available_instruments else random.choice(instruments)
        last_instrument = instrument_program

        bpm = random.randint(80, 140)
        scale = [60, 62, 64, 65, 67, 69, 71]  # C Major scale
        instrument_name = get_instrument_name(instrument_program)

        # Update displayed state
        st.session_state.current_instrument = f"{instrument_name} (Program {instrument_program})"
        st.session_state.current_bpm = bpm

        midi_filename = f"loop_{loop_count}.mid"
        print(f"Loop {loop_count}: Style={selected_style}, Instrument={instrument_program} ({instrument_name}), BPM={bpm}")

        midi_duration = generate_midi_file(midi_filename, bpm=bpm, scale=scale, instrument=instrument_program)
        play_midi_file(midi_filename, instrument_program)

        time.sleep(max(0, midi_duration))

        loop_count += 1

# ---- Streamlit UI ----
st.title("🎵 Continuous Generative Music (Seamless Loops)")

style_selection = st.radio("Select a Musical Style for Looping:", list(INSTRUMENT_SETS.keys()), horizontal=True)

st.markdown(f"### 🎹 Current Instrument: {st.session_state.current_instrument}")
st.markdown(f"### 🕒 Current BPM: {st.session_state.current_bpm}")

if st.button("▶️ Start Music Loop"):
    if not st.session_state.looping:
        st.session_state.looping = True
        st.session_state.stop_event.clear()
        st.session_state.loop_thread = threading.Thread(
            target=loop_playback,
            args=(style_selection, st.session_state.stop_event)
        )
        st.session_state.loop_thread.start()
        st.success("🎶 Music loop started!")

if st.button("⏹ Stop Music Loop"):
    if st.session_state.looping:
        st.session_state.stop_event.set()
        st.session_state.looping = False
        if st.session_state.loop_thread:
            st.session_state.loop_thread.join()
        st.success("🛑 Music loop stopped.")

