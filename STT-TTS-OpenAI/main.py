from openai import OpenAI
import os
from playsound import playsound

# Ensure the OPENAI_API_KEY environment variable is set
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise Exception("Please set the OPENAI_API_KEY environment variable")

client = OpenAI()

# Step 1: Transcribe audio to text
with open("files/testAudio.mp3", "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
# Save the transcription to a file
with open("files/current_Transcript.txt", "w") as text_file:
    text_file.write(transcription.text)
print(transcription.text)

# Step 2: Generate speech from the transcribed text (or any input text)
# Using the corrected pattern for streaming the response and saving to a file
with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input=transcription.text,
) as response:
    # Save the generated speech to an MP3 file
    response.stream_to_file("files/current_AudioResponse.mp3")

# Step 3: Play the saved audio file
# Ensure 'playsound' is installed via pip install playsound
playsound("files/current_AudioResponse.mp3")