import openai
import speech_recognition as sr
import pyttsx3
import time
import json
import os
import re

# Initialize OpenAI API
openai.api_key = "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"

# Initialize the text to speech engine
engine = pyttsx3.init()

# Load or create the medication schedule
medication_schedule_file = "medication_schedule.json"
if os.path.exists(medication_schedule_file):
    with open(medication_schedule_file, "r") as f:
        medication_schedule = json.load(f)
else:
    medication_schedule = {}

def save_medication_schedule():
    with open(medication_schedule_file, "w") as f:
        json.dump(medication_schedule, f)

def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language="es")
    except:
        print("No se que ha pasao")

def generate_response(prompt):
    if "agregar medicamento" in prompt.lower():
        medication_name, time_to_take = extract_medication_and_time(prompt)
        medication_schedule[medication_name] = time_to_take
        save_medication_schedule()
        response = f"El medicamento {medication_name} ha sido programado para las {time_to_take}."
    elif "horario del medicamento" in prompt.lower():
        medication_name = extract_medication_name(prompt)
        if medication_name in medication_schedule:
            time_to_take = medication_schedule[medication_name]
            response = f"El horario del medicamento {medication_name} es a las {time_to_take}."
        else:
            response = f"No tengo información sobre el medicamento {medication_name}."
    else:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=4000,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response = response["choices"][0]["text"]
    return response

def extract_medication_and_time(prompt):
    medication_name = re.search(r"(?<=medicamento\s)(\w+)", prompt)
    time_to_take = re.search(r"(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm))", prompt)
    
    if medication_name and time_to_take:
        return medication_name.group(0), time_to_take.group(0)
    else:
        return None, None

def extract_medication_name(prompt):
    medication_name = re.search(r"(?<=medicamento\s)(\w+)", prompt)
    
    if medication_name:
        return medication_name.group(0)
    else:
        return None

# Set Spanish voice for text-to-speech engine
voices = engine.getProperty('voices')
spanish_voice = None
for voice in voices:
    if "spanish" in voice.languages:
        spanish_voice = voice.id
if spanish_voice is not None:
    engine.setProperty('voice', spanish_voice)

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def main():
    while True:
        print("Di 'Hola' para empezar a grabar")
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio, language="es")
                if transcription.lower() == "hola":
                    filename = "input.wav"
                    print("Dime que quieres mozo")
                    with sr.Microphone() as source:
                        recognizer = sr.Recognizer()
                        source.pause_threshold = 1
                        audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                    # Transcribe audio to text
                    text = transcribe_audio_to_text(filename)
                    if text:
                        print(f"Yo {text}")

                        # Generate the response
                        response = generate_response(text)
                        print(f"El bot ese dice: {response}")

                        # Read response using GPT3
                        speak_text(response)
            except Exception as e:
                print("Ahhhhhh erroor : {}".format(e))

if __name__ == "__main__":
    main()
