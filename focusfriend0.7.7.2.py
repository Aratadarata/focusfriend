# focusfriend0.7.7.2
# prueba input mic -> sheets
# para agregar síntoma

import openai
import speech_recognition as sr
import pyttsx3
import time
import datetime
import json
import os
import re
import gspread  # cloud
import pywhatkit
from oauth2client.service_account import ServiceAccountCredentials

myscope = ['https://spreadsheets.google.com/feeds',
           'https://www.googleapis.com/auth/drive']  # permisos de acceso
mycreds = ServiceAccountCredentials.from_json_keyfile_name(
    'focusfriendconnection-b9ecff455eb2.json', myscope)
myclient = gspread.authorize(mycreds)

# open the file
mysheet = myclient.open('FocusFriend_Registros').sheet1

med = mysheet.cell(2, 5).value

rows = mysheet.get_all_records()
row2 = mysheet.row_values(2)  # Info de usuario: Luis
print('Lista de usuarios:')
print(rows)
print('El primer usuario:')
print(row2)
print('Primer contacto de Luis:')
print(mysheet.cell(2, 17).value)  # para celda específica (y,x)

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

# Information update


def update_sheet(sheet_name, data):
    # Open the Google Sheets spreadsheet
    sh = myclient.open(sheet_name)

    # Select the first sheet in the spreadsheet
    worksheet = sh.sheet1

    # Append the data to the sheet
    worksheet.append_row(data)


def update_cell(sheet_name, row_num, col_num, data):  # ?????
    # Open the Google Sheets spreadsheet
    sh = myclient.open(sheet_name)

    # Select the first sheet in the spreadsheet
    worksheet = sh.sheet1

    # Update the cell with the given row and column numbers
    worksheet.update_cell(row_num, col_num, data)


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
        print("No se pudo transcribir el audio.")


def generate_response(prompt):
    if "agregar medicamento" in prompt.lower():
        response = "Dime el nombre del medicamento"
        medication_name = None

    elif "agregar segundo medicamento" in prompt.lower():
        response = "Dime el nombre del segundo medicamento"
        medication_name = None

        # agregar síntoma(s)
    elif "agregar síntoma" in prompt.lower():
        response = "Dime cuál es tu síntoma"
        medication_name = None

    elif f"agregar síntoma para {mysheet.cell(2,5).value}" in prompt.lower():
        response = f"Dime cuál es tu síntoma con el medicamento {mysheet.cell(2, 5).value}"
        medication_name = None

    else:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Soy FocusFriend, un asistente médico virtual para personas con pérdida de memoria y dificultad para seguir tratamientos clínicos, creado por Marco Acosta y Luis Galindo en el Tecnológico de Monterrey, soy servicial y cordial {prompt}",
            max_tokens=4000,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response = response["choices"][0]["text"]
        medication_name = None

    return response, medication_name


def get_medication_info(medication_name):  # ???
    # code to fetch medication info from API
    medication_info = get_medication_info(medication_name)
    return medication_info


def extract_medication_and_time(prompt):
    medication_name = re.search(r"(?<=medicamento\s)(\w+)", prompt)
    time_to_take = re.search(r"(\d{1,2}:\d{2}\s?(?:AM|PM|am|pm))", prompt)

    if medication_name and time_to_take:
        return medication_name.group(0), time_to_take.group(0)
    elif medication_name:
        return medication_name.group(0), None
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
# voice id en español ES-MX
engine.setProperty('voice', voices[2].id)

# editing default configuration
engine. setProperty('rate', 178)
engine.setProperty('volume', 0.7)


def speak_text(text):
    engine.say(text)
    engine.runAndWait()


def main():
    while True:
        print("Di 'Focus o asistente' para empezar a grabar")
        with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(
                    audio, language="es")
                if transcription is not None and (transcription.lower() == "focus" or transcription.lower() == "asistente"):
                    filename = "input.wav"

                    # respuesta de activación
                    response = "Hola, ¿en qué puedo servirte?"
                    print(response)
                    speak_text(response)

                    with sr.Microphone() as source:
                        recognizer = sr.Recognizer()
                        # tiempo de espera para respuesta
                        source.pause_threshold = 1
                        audio = recognizer.listen(
                            source, phrase_time_limit=None, timeout=None)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                    # Transcribe audio to text
                    text = transcribe_audio_to_text(filename)

                    response, medication_name = generate_response(text)

                    if response == "Dime el nombre del medicamento":
                        print(response)
                        speak_text(response)
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        2, 2, medication_name)
                            # confirmación de que se añadió
                            response = f"Medicamento {medication_name} agregado correctamente"
                            print(response)
                            speak_text(response)

                    elif response == "Dime el nombre del segundo medicamento":
                        print(response)
                        speak_text(response)
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        2, 5, medication_name)
                            # confirmación de que se añadió
                            response = f"El segundo medicamento {medication_name} se agregó correctamente"
                            print(response)
                            speak_text(response)

                    elif response == "Dime cuál es tu síntoma":
                        print(response)
                        speak_text(response)
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        2, 4, medication_name)
                            # confirmación de que se añadió
                            response = f"Síntoma {medication_name} agregado correctamente"
                            print(response)
                            speak_text(response)

                    elif response == f"Dime cuál es tu síntoma con el medicamento {mysheet.cell(2, 5).value}":
                        print(response)
                        speak_text(response)
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        2, 7, medication_name)
                            # confirmación de que se añadió
                            response = f"Síntoma con el medicamento {mysheet.cell(2,5).value} agregado correctamente"
                            print(response)
                            speak_text(response)

                    else:
                        if text:
                            print(f"Usted dijo: {text}")

                            # Generate the response
                            response = generate_response(text)
                            print(f"FocusFriend responde: {response}")

                            # Read response using GPT3
                            speak_text(response)
                else:
                    print("No se pudo transcribir el audio.")
            except Exception as e:
                print("Error: {}".format(e))


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
