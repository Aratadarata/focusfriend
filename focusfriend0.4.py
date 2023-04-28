import openai
import speech_recognition as sr
import pyttsx3
import time

# Initialize OpenAI API
openai.api_key = "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"
# Initialize the text to speech engine
engine = pyttsx3.init()


def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language="es")
    except:
        print("No se pudo transcribir el audio")

def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Estimado modelo de lenguaje, por favor proporciona una respuesta formal y completa en español para la siguiente consulta: {prompt}",
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response["choices"][0]["text"]

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
                    print("Por favor, realiza tu pregunta")
                    with sr.Microphone() as source:
                        recognizer = sr.Recognizer()
                        source.pause_threshold = 1
                        audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                    # Transcribe audio to text
                    text = transcribe_audio_to_text(filename)
                    if text:
                        print(f"Tu pregunta fue: {text}")

                        # Generate the response
                        response = generate_response(text)
                        print(f"La respuesta es: {response}")

                        # Speak response using GPT3
                        speak_text(response)
            except Exception as e:
                print("Error: {}".format(e))

if __name__ == "__main__":
    main()

