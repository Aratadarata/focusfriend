# focusfriend0.7.5
# prueba input mic -> sheets

import openai
import speech_recognition as sr
import pyttsx3
import time
import json
import os
import re
import gspread  # cloud
from oauth2client.service_account import ServiceAccountCredentials

myscope = ['https://spreadsheets.google.com/feeds',
           'https://www.googleapis.com/auth/drive']  # permisos de acceso
mycreds = ServiceAccountCredentials.from_json_keyfile_name(
    'focusfriendconnection-b9ecff455eb2.json', myscope)
myclient = gspread.authorize(mycreds)

# open the file
mysheet = myclient.open('FocusFriend_Registros').sheet1

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
        # extract the text after "agregar medicamento"
        medication_prompt = prompt.split(":")[1].strip()
        medication_name, time_to_take = extract_medication_and_time(prompt)
        medication_schedule[medication_name] = time_to_take
        save_medication_schedule()
        response = f"Estimado paciente, he agregado el medicamento {medication_name} a su horario para las {time_to_take}."
        return response, medication_name

    elif "horario del medicamento" in prompt.lower():
        medication_name = extract_medication_name(prompt)
        if medication_name in medication_schedule:
            time_to_take = medication_schedule[medication_name]
            response = f"El horario del medicamento {medication_name} es a las {time_to_take}."
        else:
            response = f"No tengo información sobre el medicamento {medication_name}."
        return response, medication_name
    else:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Soy FocusFriend, un asistente médico virtual para personas con pérdida de memoria y dificultad para seguir tratamientos clínicos, creado por Marco Acosta y Luis Galindo en el Tecnológico de Monterrey, soy servicial y cordial {prompt}",
            max_tokens=4000,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response = response["choices"][0]["text"]
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
                if transcription is not None and (transcription.lower() == "focus" or "asistente"):
                    filename = "input.wav"
                    print("Por favor, hágamelo saber qué necesita.")
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

                    if "agregar medicamento" in text.lower():
                        print("Dime el nombre del medicamento")
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            source.pause_threshold = 1
                            audio = recognizer.listen(
                                source, phrase_time_limit=None, timeout=None)
                            medication_name = recognizer.recognize_google(audio, language="es")
                        
                        update_cell('FocusFriend_Registros', 2, 2, medication_name)
                        print(f"Se ha guardado el medicamento '{medication_name}' en la hoja de cálculo.")
                    else:
                        response, medication_name = generate_response(text)
                        if text:
                            print(f"Usted dijo: {text}")

                            # Generate the response
                            print(f"FocusFriend responde: {response}")

                            # Read response using GPT3
                            speak_text(response)
            except Exception as e:
                print("Error: {}".format(e))


      
if __name__ == "__main__":
    main()
