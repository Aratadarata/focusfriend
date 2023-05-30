# focusfriend0.7.7.5
# prueba input mic -> sheets
# para agregar síntoma
#un solo medicamento
import openai
import speech_recognition as sr
import pyttsx3
import time
import datetime
import threading
import json
import os
import re
import gspread  # cloud
import pywhatkit
import string
import sounddevice as sd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from pydub import AudioSegment
from io import BytesIO
import soundfile as sf

from ledsRespeaker2MicHat import Pixels

# Crear un objeto de píxeles
pixels = Pixels()

# En algún lugar de tu código cuando tu asistente está a punto de escuchar
pixels.listen()

# En algún lugar de tu código cuando tu asistente está pensando o procesando algo
pixels.think()

# En algún lugar de tu código cuando tu asistente está hablando
pixels.speak()

# En algún lugar de tu código cuando tu asistente no está haciendo nada
pixels.off()

myscope = ['https://spreadsheets.google.com/feeds',
           'https://www.googleapis.com/auth/drive']  # permisos de acceso
mycreds = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/focus/focuspy/focusfriendconnection-b9ecff455eb2.json',
   myscope
)

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
    # Utilizamos speech_recognition para transcribir
    recognizer = sr.Recognizer()
    # Aquí se abre el archivo en modo de lectura y no se utiliza sounddevice
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
        frequency = None

    elif "agregar segundo medicamento" in prompt.lower():
        response = "Dime el nombre del segundo medicamento"
        medication_name = None

    elif "agregar tercer medicamento" in prompt.lower():
        response = "Dime el nombre del tercer medicamento"
        medication_name = None

    elif "agregar cuarto medicamento" in prompt.lower():
        response = "Dime el nombre del cuarto medicamento"
        medication_name = None

    elif "agregar quinto medicamento" in prompt.lower():
        response = "Dime el nombre del quinto medicamento"
        medication_name = None

    elif "menciona mis medicamentos" in prompt.lower():
        # response = "Dime el nombre del tercer medicamento"
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
            prompt=f"Tu nombre es FocusFriend, eres un asistente médico virtual creado por Marco Acosta y Luis Galindo, eres servicial y cordial, tu principal función es consientizar a los pacientes acerca de la adherencia médica, tus respuestas son breves {prompt}",
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
# Palabras a números:
# Whatsapp:
def send_message(phone_number, message):
    try:
        pywhatkit.sendwhatmsg_instantly(phone_no=phone_number, message=message)
        print("Mensaje Enviado")
    except:
        print("Ocurrio Un Error")
# send_message("+525520945995", "¡Recordatorio! Toma tu paracetamol")


def send_message_at_time(phone_no, message, send_time):
    def send():
        pywhatkit.sendwhatmsg(phone_no=phone_no, message=message,
                              time_hour=send_time.hour, time_min=send_time.minute, wait_time=10)
    thread = threading.Thread(target=send)
    thread.start()
# send_time = datetime.datetime.now() + datetime.timedelta(minutes=1)


# Set Spanish voice for text-to-speech engine
voices = engine.getProperty('voices')
# voice id en español ES-MX
engine.setProperty('voice', voices[21].id)

# editing default configuration
engine. setProperty('rate', 168)
engine.setProperty('volume', 0.9)


def speak_text(text):
    engine.say(text)
    engine.runAndWait()


def main():

    fs = 44100
    seconds = 5  # Duration of recording
    device_index_input = 8 #8
    device_index_output = 7 #7, change this to your output device index

    while True:
        print("Di 'Focus o asistente' para empezar a grabar")
        pixels.listen()
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, device=device_index_input)
        print("Recording Audio")
        sd.wait()  # Wait until recording is finished
        print("Audio recording complete")

        # Convert recording to wav format
        filename = "input.wav"
        sf.write(filename, myrecording, fs)  # write as WAV file

        recognizer = sr.Recognizer()

        with sr.AudioFile(filename) as source:
            recognizer = sr.Recognizer()
            audio = recognizer.record(source)
            try:
                transcription = recognizer.recognize_google(
                    audio, language="es")
                if transcription is not None and (transcription.lower() == "focus" or transcription.lower() == "asistente"):
                    print("Hola, ¿en qué puedo servirte?")
                    pixels.think()
                    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, device=device_index_input)
                    print("Recording Audio")
                    sd.wait()  # Wait until recording is finished
                    print("Audio recording complete")

                    # Convert recording to wav format
                    filename = "input.wav"
                    sf.write(filename, myrecording, fs)

        # Transcribe audio to text
                    text = transcribe_audio_to_text(filename)

                    response, medication_name = generate_response(text)
                    pixels.speak()
                    if response == "Dime el nombre del medicamento":
                        print(response)
                        speak_text(response)
                        with sd.rec(int(seconds * fs), samplerate=fs, channels=2, device=device_index_input)  as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        1, 3, medication_name)

                            # confirmación de que se añadió
                            pixels.speak()
                            response = f"Medicamento {medication_name} agregado correctamente. Dime el número de horas entre cada toma:"
                            print(response)
                            speak_text(response)
                            with sd.rec(int(seconds * fs), samplerate=fs, channels=2, device=device_index_input)  as source:
                                recognizer = sr.Recognizer()
                                audio = recognizer.listen(source)
                                frequency = recognizer.recognize_google(
                                    audio, language="es")
                                update_cell('FocusFriend_Registros',
                                            2, 3, frequency)

                            # confirmation that the frequency was added
                            # convert_spanish_number(frequency)
                            response = f"Frecuencia de {medication_name} actualizada a cada {frequency} horas."
                            print(response)
                            speak_text(response)
                            send_message(
                                "+525520945995", f"Medicamento {medication_name} agregado correctamente, no olvides tomarlo cada {frequency} horas.")
                            send_message_at_time("+525520945995", f"Es hora de tomar tu medicamento: {medication_name}", datetime.datetime.now(
                            ) + datetime.timedelta(minutes=1
                                                   ))

                    elif response == "Dime cuál es tu síntoma":
                        print(response)
                        speak_text(response)
                        with sd.rec(int(seconds * fs), samplerate=fs, channels=2, device=device_index_input)  as source:
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
                        with sd.rec(int(seconds * fs), samplerate=fs, channels=2, device=device_index_input)  as source:
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
