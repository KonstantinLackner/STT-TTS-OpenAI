from openai import OpenAI
import os
from playsound import playsound
import wave
import pyaudio

# Ensure the OPENAI_API_KEY environment variable is set
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise Exception("Please set the OPENAI_API_KEY environment variable")

client = OpenAI()


def record_audio(WAVE_OUTPUT_FILENAME="recorded.wav", RECORD_SECONDS=5):
    FORMAT = pyaudio.paInt16  # Audio format
    CHANNELS = 1  # Mono audio
    RATE = 44100  # Sample rate
    CHUNK = 1024  # Data chunk size
    p = pyaudio.PyAudio()

    # Start recording
    stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    print("Recording...")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Finished recording.")

    # Stop recording
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


record_audio("audio_input.wav", 5)

# Transcribe the recorded audio
with open("audio_input.wav", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
print(transcription.text)

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": transcription.text}],
    stream=True,
)

response_text = ""

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
        response_text += chunk.choices[0].delta.content


with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input=response_text,
) as response:
    # Save the generated speech to an MP3 file
    response.stream_to_file("files/current_AudioResponse.mp3")

# Step 3: Play the saved audio file
# Ensure 'playsound' is installed via pip install playsound
playsound("files/current_AudioResponse.mp3")
