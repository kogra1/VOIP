import sounddevice as sd
import scipy.io.wavfile as wav
import pyaudio
import wave

CHUNK = 160


def record_audio(duration, sample_rate, filename="output.wav"):
    print("Recording audio...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")
    wav.write(filename, sample_rate, audio_data)
    print(f"Audio saved to {filename}")
    return audio_data

def live_capture(sample_rate, filename="client_live_output.wav"):
    print("Starting live audio capture... Press Ctrl+C to stop and save.")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=CHUNK)

    recording = []

    # try:
    while True:
        chunk = stream.read(CHUNK)
        recording.append(chunk)
        yield chunk

    # except KeyboardInterrupt:
    #     print("Stopping live audio capture...")
    
    # finally:
    #     stream.stop_stream()
    #     stream.close()
    #     audio.terminate()

        # with wave.open(filename, 'wb') as f:
        #     f.setnchannels(1)
        #     f.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        #     f.setframerate(sample_rate)
        #     f.writeframes(b''.join(recording))
        # print(f"Live audio saved to {filename}")
