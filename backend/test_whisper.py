import whisper
import warnings

def test():
    print("Loading whisper model...")
    model = whisper.load_model("base")
    print("Model loaded. Transcribing...")
    # create a dummy audio file or use a real one
    # I'll just use sample audio.
    # Actually wait, whisper can transcribe just any wav file
    # let me generate a 1 sec sine wave
    import numpy as np
    import soundfile as sf
    sr = 16000
    t = np.linspace(0, 1, sr)
    audio = np.sin(2 * np.pi * 440 * t)
    sf.write('test_tone.wav', audio, sr)
    
    try:
        res = model.transcribe('test_tone.wav')
        print(res['text'])
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
