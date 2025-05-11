import streamlit as st
import random
from datetime import datetime

# Our generation class
from loopgen import LoopGen

# ---- Constants ----
GOALS = ["Focus", "Relax", "Energy", "Sleep", "Creative Flow", "Calm Confidence", "Romantic", "Reflective"]
STYLES = ["Ambient", "Jazz", "Classical", "Electronic/EDM", "Pop", "World", "Folk/Acoustic", "Cinematic/Orchestral"]

BPM_RANGES = {
    "Focus": {"Morning": (90, 110), "Midday": (100, 120), "Evening": (80, 100), "Night": (60, 80)},
    "Relax": {"Morning": (70, 90), "Midday": (80, 100), "Evening": (60, 80), "Night": (40, 60)},
    "Energy": {"Morning": (100, 120), "Midday": (120, 140), "Evening": (110, 130), "Night": (90, 110)},
    "Sleep": {"Evening": (50, 70), "Night": (40, 60)},
    "Creative Flow": {"Morning": (90, 110), "Midday": (100, 120), "Evening": (80, 100)},
    "Calm Confidence": {"Morning": (80, 100), "Midday": (90, 110), "Evening": (70, 90)},
    "Romantic": {"Evening": (60, 80), "Night": (50, 70)},
    "Reflective": {"Evening": (60, 80), "Night": (50, 70)}
}

CHORD_PROGRESSIONS = {
    "Focus": ["I-vi-IV-V", "ii-V-I", "Modal Dorian"],
    "Relax": ["I-IV-I", "I-vi-IV-I", "Lydian Static"],
    "Energy": ["I-V-vi-IV", "IV-V-I", "Dominant Cycle"],
    "Sleep": ["I-ii-I", "Pedal Tones", "Open 5ths"],
    "Creative Flow": ["I-V-vi-IV", "ii-V-I", "Modal Mixolydian"],
    "Calm Confidence": ["I-IV-V-I", "ii-V-I", "I-vi-ii-V"],
    "Romantic": ["I-vi-IV-V", "ii-V-I", "I-IV-I"],
    "Reflective": ["I-vi-IV-I", "Modal Aeolian", "I-ii-IV-V"]
}

INSTRUMENT_SETS = {
    "Ambient": [88, 90, 91, 94, 95, 81, 82],
    "Jazz": [0, 1, 26, 27, 56, 57, 32, 33],
    "Classical": [0, 48, 49, 50, 46],
    "Electronic/EDM": [81, 82, 83, 88, 89, 90, 97, 98],
    "Pop": [0, 1, 25, 26, 80, 81],
    "World": [104, 105, 106, 73, 74, 115, 116],
    "Folk/Acoustic": [24, 25, 26, 105, 22],
    "Cinematic/Orchestral": [48, 49, 60, 61, 117, 118]
}

SCALE_MAP = {
    "Focus": ["Dorian", "Mixolydian", "Major"],
    "Relax": ["Lydian", "Major", "Pentatonic"],
    "Energy": ["Major", "Mixolydian", "Phrygian"],
    "Sleep": ["Aeolian", "Dorian", "Pentatonic"],
    "Creative Flow": ["Lydian", "Mixolydian", "Dorian"],
    "Calm Confidence": ["Major", "Dorian"],
    "Romantic": ["Harmonic Minor", "Aeolian", "Major"],
    "Reflective": ["Aeolian", "Dorian", "Pentatonic"]
}

KEY_MAP = {
    "Focus": ["C", "A", "F"],
    "Relax": ["F", "Eb", "Bb"],
    "Energy": ["G", "D", "E"],
    "Sleep": ["A Minor", "C Minor", "G Minor"],
    "Creative Flow": ["E", "G", "D"],
    "Calm Confidence": ["C", "F", "Bb"],
    "Romantic": ["Bb", "D Minor", "A Minor"],
    "Reflective": ["C Minor", "D Minor", "Eb", "G Minor"]
}

CIRCADIAN_KEY_BIAS = {
    "Morning": ["C", "G", "F", "A"],
    "Midday": ["D", "E", "G", "A"],
    "Early Afternoon": ["E", "G", "A", "D"],
    "Late Afternoon": ["F", "Bb", "Eb"],
    "Evening": ["Bb", "Eb", "C Minor", "D Minor"],
    "Night": ["A Minor", "C Minor", "G Minor", "D Minor"],
    "Sleep": ["A Minor", "C Minor", "G Minor"]
}

# ---- Circadian Functions ----
def get_circadian_phase(hour):
    if 6 <= hour < 9:
        return "Morning"
    elif 9 <= hour < 12:
        return "Midday"
    elif 12 <= hour < 15:
        return "Early Afternoon"
    elif 15 <= hour < 18:
        return "Late Afternoon"
    elif 18 <= hour < 21:
        return "Evening"
    elif 21 <= hour < 24:
        return "Night"
    else:
        return "Sleep"

def select_biased_key(goal, phase):
    goal_keys = KEY_MAP.get(goal, ["C"])
    phase_keys = CIRCADIAN_KEY_BIAS.get(phase, ["C"])
    common_keys = list(set(goal_keys) & set(phase_keys))
    if common_keys:
        return random.choice(common_keys)
    combined_keys = goal_keys + phase_keys * 2
    return random.choice(combined_keys)

def generate_music_parameters(goal, style, hour):
    phase = get_circadian_phase(hour)
    bpm_range = BPM_RANGES.get(goal, {}).get(phase, (80, 100))
    bpm = random.randint(*bpm_range)
    chosen_progression = random.choice(CHORD_PROGRESSIONS.get(goal, ["I-IV-V-I"]))
    full_instrument_set = INSTRUMENT_SETS.get(style, [0])
    chosen_instruments = random.sample(full_instrument_set, min(len(full_instrument_set), random.choice([3, 4])))
    chosen_scale = random.choice(SCALE_MAP.get(goal, ["Major"]))
    chosen_key = select_biased_key(goal, phase)

    return {
        "simulated_hour": hour,
        "circadian_phase": phase,
        "bpm": bpm,
        "chord_progression": chosen_progression,
        "scale": chosen_scale,
        "key": chosen_key,
        "instruments": chosen_instruments
    }

# ---- Music Generation Class ----
class GenerateMusic:
    def __init__(self, params):
        self.params = params

    def generate(self):
        st.info("🎧 [Stub] Music generation started with parameters:")
        st.json(self.params)

# ---- Streamlit UI ----
st.title("🎵 Daily Wellness Music Generator")

st.subheader("🎯 Choose Your Wellness Goal")
goal_selection = st.radio("Select a Goal:", GOALS, horizontal=True)

st.subheader("🎵 Choose Your Musical Style")
style_selection = st.radio("Select a Style:", STYLES, horizontal=True)

if "simulated_hour" not in st.session_state:
    st.session_state.simulated_hour = 7  # Start day at 7 AM

if goal_selection and style_selection:
    st.markdown("---")
    st.subheader("🕒 **Testing: Simulate Time of Day**")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏪ Back 1 Hour"):
            st.session_state.simulated_hour = (st.session_state.simulated_hour - 1) % 24
    with col2:
        st.write(f"### {st.session_state.simulated_hour:02d}:00h")
    with col3:
        if st.button("⏩ Forward 1 Hour"):
            st.session_state.simulated_hour = (st.session_state.simulated_hour + 1) % 24

    params = generate_music_parameters(goal_selection, style_selection, st.session_state.simulated_hour)

    st.subheader("🎶 Generated Music Parameters for Simulated Time")
    st.json(params)

    if st.button("🎹 Generate Music"):
        generator = GenerateMusic(params)
        generator.generate()

    if st.button("🎵 Play Loop"):
        loop = LoopGen(params)
        loop.generate()