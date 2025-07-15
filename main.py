import soundcard as sc
import numpy as np
import threading
import queue
import time
from faster_whisper import WhisperModel
import argostranslate.package
import argostranslate.translate

# === CONFIG ===
LANGUAGE       = "fr"
SAMPLE_RATE    = 16000
CHUNK_DURATION = 5    # seconds per transcription window
STEP_DURATION  = 3    # how much to advance each time
CHUNK_SIZE     = SAMPLE_RATE * CHUNK_DURATION
STEP_SIZE      = SAMPLE_RATE * STEP_DURATION

# === 1) Ensure Argos fr→en is installed ===
print("🔍 Checking/installing Argos fr→en pack…")
argostranslate.package.update_package_index()
pkgs = argostranslate.package.get_available_packages()
pkg  = next(p for p in pkgs if p.from_code == LANGUAGE and p.to_code == "en")
argostranslate.package.install_from_path(pkg.download())

# === 2) Load faster-whisper on CPU ===
print("🧠 Loading faster-whisper model (CPU)…")
model = WhisperModel("base", device="cpu", compute_type="int8")

# === 3) Load Argos Translate model ===
print("🔍 Loading Argos Translate model…")
langs      = argostranslate.translate.get_installed_languages()
src, tgt   = (next(l for l in langs if l.code == c) for c in (LANGUAGE, "en"))
translator = src.get_translation(tgt)

# === Shared structures ===
audio_q     = queue.Queue()
lock        = threading.Lock()
last_text   = None
last_trans  = None

# === Audio reader thread ===
def audio_reader():
    mics = [m for m in sc.all_microphones(include_loopback=True) if m.isloopback]
    if not mics:
        raise RuntimeError("No loopback microphone found. Check your OS audio settings.")
    mic = mics[0]
    print(f"🎧 Capturing from: {mic.name}")
    with mic.recorder(samplerate=SAMPLE_RATE, blocksize=STEP_SIZE) as recorder:
        while True:
            frames = recorder.record(numframes=STEP_SIZE)
            mono   = np.mean(frames, axis=1)
            audio_q.put(mono.astype(np.float32))



# === Transcription + Translation thread ===
def transcriber_worker():
    global last_text, last_trans
    buffer = np.zeros((0,), dtype=np.float32)
    while True:
        chunk = audio_q.get()
        buffer = np.concatenate((buffer, chunk))
        if len(buffer) >= CHUNK_SIZE:
            segment = buffer[:CHUNK_SIZE]
            buffer  = buffer[STEP_SIZE:]
            segments, _ = model.transcribe(
                segment,
                language=LANGUAGE,
                beam_size=1,
                vad_filter=True
            )
            text = " ".join(s.text for s in segments).strip()
            if text:
                translation = translator.translate(text).strip()
                with lock:
                    last_text  = text
                    last_trans = translation

# === Printer thread (every second) ===
def printer_worker():
    global last_text, last_trans
    print("🟢 Starting live translation… (Ctrl+C to stop)\n")
    while True:
        time.sleep(0.1)
        with lock:
            if last_text:
                print(f"🗣️ {last_text}\n🌐 {last_trans}\n")
                last_text = None
                last_trans = None
            # else:
            #     print("...")

# === Main ===
if __name__ == "__main__":
    threads = [
        threading.Thread(target=audio_reader,       daemon=True),
        threading.Thread(target=transcriber_worker, daemon=True),
        threading.Thread(target=printer_worker,     daemon=True),
    ]
    for t in threads:
        t.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n❌ Stopped.")
