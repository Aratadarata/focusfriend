# focusfriend0.7.7.4
# prueba input mic -> sheets
# para agregar síntoma

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
# Palabras a números:


def convert_spanish_number(number_text):
    # Define a dictionary to map Spanish number words to their integer values.
    number_map = {
        'cero': 0, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4,
        'cinco': 5, 'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9,
        'diez': 10, 'once': 11, 'doce': 12, 'trece': 13, 'catorce': 14,
        'quince': 15, 'dieciséis': 16, 'diecisiete': 17, 'dieciocho': 18, 'diecinueve': 19,
        'veinte': 20, 'treinta': 30, 'cuarenta': 40, 'cincuenta': 50, 'sesenta': 60,
        'setenta': 70, 'ochenta': 80, 'noventa': 90, 'cien': 100, 'mil': 1000
    }
    # Split the number text into individual words and remove any punctuation.
    number_words = number_text.lower().translate(
        str.maketrans('', '', string.punctuation)).split()
    # Initialize variables for tracking the total value and the current group value.
    total_value = 0
    current_group_value = 0
    # Iterate over each word in the number text and accumulate the total value.
    for word in number_words:
        # If the word is a valid number word, add its value to the current group value.
        if word in number_map:
            current_group_value += number_map[word]

        # If the word is a group name (e.g. "mil"), multiply the current group value by the appropriate factor.
        elif word in ('mil',):
            current_group_value *= number_map[word]
            total_value += current_group_value
            current_group_value = 0

        # If the word is a "y" connector, continue accumulating the current group value.
        elif word == 'y':
            continue

        # If the word is not recognized, raise an error.
        else:
            raise ValueError("Unrecognized word: {}".format(word))

    # Add the final group value to the total and return the result.
    print(total_value + current_group_value)
    return total_value + current_group_value

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
                                        1, 3, medication_name)

                            # confirmación de que se añadió
                            response = f"Medicamento {medication_name} agregado correctamente. Dime el número de horas entre cada toma:"
                            print(response)
                            speak_text(response)
                            with sr.Microphone() as source:
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
                    elif response == "Dime el nombre del segundo medicamento":
                        print(response)
                        speak_text(response)
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        4, 3, medication_name)
            # confirmación de que se añadió
                            response = f"Segundo medicamento {medication_name} agregado correctamente. Dime el número de horas entre cada toma:"
                            print(response)
                            speak_text(response)
                            with sr.Microphone() as source:
                                recognizer = sr.Recognizer()
                                audio = recognizer.listen(source)
                                frequency = recognizer.recognize_google(
                                    audio, language="es")
                                update_cell('FocusFriend_Registros',
                                            5, 3, frequency)

                            # confirmation that the frequency was added
                            # convert_spanish_number(frequency)
                            response = f"Frecuencia del segundo medicamento {medication_name} actualizada a cada {frequency} horas."
                            print(response)
                            speak_text(response)
                            send_message(
                                "+525520945995", f"Segundo medicamento {medication_name} agregado correctamente, no olvides tomarlo cada {frequency} horas.")
                            send_message_at_time("+525520945995", f"Es hora de tomar tu medicamento: {medication_name}", datetime.datetime.now(
                            ) + datetime.timedelta(minutes=1
                                                   ))

                    elif response == "Dime el nombre del tercer medicamento":
                        print(response)
                        speak_text(response)
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        7, 3, medication_name)
            # confirmación de que se añadió
                            response = f"Tercer medicamento {medication_name} agregado correctamente. Dime el número de horas entre cada toma:"
                            print(response)
                            speak_text(response)
                            with sr.Microphone() as source:
                                recognizer = sr.Recognizer()
                                audio = recognizer.listen(source)
                                frequency = recognizer.recognize_google(
                                    audio, language="es")
                                update_cell('FocusFriend_Registros',
                                            8, 3, frequency)

                            # confirmation that the frequency was added
                            # convert_spanish_number(frequency)
                            response = f"Frecuencia del tercer medicamento {medication_name} actualizada a cada {frequency} horas."
                            print(response)
                            speak_text(response)
                            send_message(
                                "+525520945995", f"Tercer medicamento {medication_name} agregado correctamente, no olvides tomarlo cada {frequency} horas.")
                            send_message_at_time("+525520945995", f"Es hora de tomar tu medicamento: {medication_name}", datetime.datetime.now(
                            ) + datetime.timedelta(minutes=1
                                                   ))

                    elif response == "Dime el nombre del cuarto medicamento":
                        print(response)
                        speak_text(response)
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        10, 3, medication_name)
            # confirmación de que se añadió
                            response = f"Cuarto medicamento {medication_name} agregado correctamente. Dime el número de horas entre cada toma:"
                            print(response)
                            speak_text(response)
                            with sr.Microphone() as source:
                                recognizer = sr.Recognizer()
                                audio = recognizer.listen(source)
                                frequency = recognizer.recognize_google(
                                    audio, language="es")
                                update_cell('FocusFriend_Registros',
                                            11, 3, frequency)

                            # confirmation that the frequency was added
                            # convert_spanish_number(frequency)
                            response = f"Frecuencia del cuarto medicamento {medication_name} actualizada a cada {frequency} horas."
                            print(response)
                            speak_text(response)
                            send_message(
                                "+525520945995", f"Cuarto medicamento {medication_name} agregado correctamente, no olvides tomarlo cada {frequency} horas.")
                            send_message_at_time("+525520945995", f"Es hora de tomar tu medicamento: {medication_name}", datetime.datetime.now(
                            ) + datetime.timedelta(minutes=1
                                                   ))

                    elif response == "Dime el nombre del quinto medicamento":
                        print(response)
                        speak_text(response)
                        with sr.Microphone() as source:
                            recognizer = sr.Recognizer()
                            audio = recognizer.listen(source)
                            medication_name = recognizer.recognize_google(
                                audio, language="es")
                            update_cell('FocusFriend_Registros',
                                        13, 3, medication_name)
            # confirmación de que se añadió
                            response = f"Quinto medicamento {medication_name} agregado correctamente. Dime el número de horas entre cada toma:"
                            print(response)
                            speak_text(response)
                            with sr.Microphone() as source:
                                recognizer = sr.Recognizer()
                                audio = recognizer.listen(source)
                                frequency = recognizer.recognize_google(
                                    audio, language="es")
                                update_cell('FocusFriend_Registros',
                                            14, 3, frequency)

                            # confirmation that the frequency was added
                            # convert_spanish_number(frequency)
                            response = f"Frecuencia del quinto medicamento {medication_name} actualizada a cada {frequency} horas."
                            print(response)
                            speak_text(response)
                            send_message(
                                "+525520945995", f"Quinto medicamento {medication_name} agregado correctamente, no olvides tomarlo cada {frequency} horas.")
                            send_message_at_time("+525520945995", f"Es hora de tomar tu medicamento: {medication_name}", datetime.datetime.now(
                            ) + datetime.timedelta(minutes=1
                                                   ))

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
