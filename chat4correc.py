from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha

# OpenAI GPT-3
import openai

# Load credentials
import os
from dotenv import load_dotenv
load_dotenv()

# Google TTS
import google.cloud.texttospeech as tts
import pygame
import time

# Mute ALSA errors...
from ctypes import *
from contextlib import contextmanager

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    try: 
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        print('')

### PARAMETERS ###
activationWords = ['ordenador', 'calculadora', 'shodan', 'showdown']
tts_type = 'local' # google or local

# Local speech engine initialisation
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # 0 = male, 1 = female

# Google TTS client
def google_text_to_wav(voice_name: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])

    # Set the text input to be synthesized
    text_input = tts.SynthesisInput(text=text)

    # Build the voice request, select the language code ("es-ES") and the voice name
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )

    # Select the type of audio file you want returned
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input, voice=voice_params, audio_config=audio_config
    )

    return response.audio_content

# Configure browser
# Set the path
firefox_path = r"usr/bin/firefox"
# Register the browser
webbrowser.register('firefox', None, 
                    webbrowser.BackgroundBrowser(firefox_path))

# Wolfram Alpha client
appId = '5R49J7-J888YX9J2V'
wolframClient = wolframalpha.Client(appId)

def speak(text, rate = 120):
    time.sleep(0.3)

    if tts_type == 'local':
        engine.setProperty('rate', rate) 
        engine.say(text)
        engine.runAndWait()
    if tts_type == 'google':
        speech = google_text_to_wav('es-ES-Standard-C', text)
        pygame.mixer.init(frequency=12000, buffer = 512)
        speech_sound = pygame.mixer.Sound(speech)
        speech_sound.play()
        time.sleep(len(text.split()))
        pygame.mixer.quit()

def parseCommand():
    with noalsaerr():
        listener = sr.Recognizer()
        print('Escuchando una orden...')

        with sr.Microphone() as source:
            listener.pause_threshold = 2
            input_speech = listener.listen(source)

        try:
            print('Reconociendo el habla...')
            query = listener.recognize_google
            print(f'La orden fue: {query}')

        except Exception as exception:
            print('No entendí la orden')
            print(exception)

            return 'None'

        return query

def search_wikipedia(keyword=''):
    searchResults = wikipedia.search(keyword)
    if not searchResults:
        return 'No se encontraron resultados'
    try: 
        wikiPage = wikipedia.page(searchResults[0]) 
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']

def search_wolframalpha(keyword=''):
    response = wolframClient.query(keyword)
  
    # @success: Wolfram Alpha fue capaz de resolver la consulta
    # @numpods: Número de resultados devueltos
    # pod: Lista de resultados. Esto también puede contener subpods

    # Consulta no resuelta
    if response['@success'] == 'false':
        speak('No pude calcular')
    # Consulta resuelta
    else: 
        result = ''
        # Pregunta
        pod0 = response['pod'][0]
        # Puede contener respuesta (tiene el mayor valor de confianza) 
        # si es primaria o tiene el título de resultado o definición, entonces es el resultado oficial
        pod1 = response['pod'][1]
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            # Obtener el resultado
            result = listOrDict(pod1['subpod'])
            # Eliminar sección entre paréntesis
            return result.split('(')[0]
        else:
            # Obtener la interpretación de pod0
            question = listOrDict(pod0['subpod'])
            # Eliminar sección entre paréntesis
            question = question.split('(')[0]
            # Podríamos buscar en wikipedia en lugar de esto
            return question

def query_openai(prompt = ""):
    openai.organization = os.environ['OPENAI_ORG']
    openai.api_key = os.environ['OPENAI_API_KEY']

    # Temperature es una medida de aleatoriedad
    # Max_tokens es el número de tokens a generar
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=80,

    )

    return response.choices[0].text

# Bucle principal
if __name__ == '__main__': 
    speak('Todos los sistemas están operativos', 120)

    while True:
        # Parsear como una lista
        # query = 'ordenador decir hola'.split()
        query = parseCommand().lower().split()

        if query[0] in activationWords and len(query) > 1:
            query.pop(0)

            # Establecer comandos
            if query[0] == 'decir':
                if 'hola' in query:
                    speak('¡Saludos!')
                else:
                    query.pop(0) # Eliminar 'decir'
                    speech = ' '.join(query) 
                    speak(speech)

            # Consultar a OpenAI
            if
            query[0] == 'perspicacia':
                query.pop(0) # Eliminar 'perspicacia'
                query = ' '.join(query)
                speech = query_openai(query)
                speak("Entendido")
                speak(speech)

            # Navegación
            if query[0] == 'ir' and query[1] == 'a':
                speak('Abriendo... ')
                # Suponemos que la estructura es palabra de activación + ir a, así que eliminamos las dos siguientes palabras
                query = ' '.join(query[2:])
                webbrowser.get('firefox').open_new(query)

            # Wikipedia
            if query[0] == 'wikipedia':
                query = ' '.join(query[1:])
                speak('Buscando en la base de datos universal')
                time.sleep(2)
                speak(search_wikipedia(query))

            # Wolfram Alpha
            if query[0] == 'calcular' or query[0] == 'computadora':
                query = ' '.join(query[1:])
                try:
                    result = search_wolframalpha(query)
                    speak(result)
                except:
                    speak('No pude calcular')

            # Tomar notas
            if query[0] == 'registrar':
                speak('Listo para grabar tu nota')
                newNote = parseCommand().lower()
                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                with open('note_%s.txt' % now, 'w') as newFile:
                    newFile.write(now)
                    newFile.write(' ')
                    newFile.write(newNote)
                speak('Nota escrita')

            if query[0] == 'salir':
                speak('Adiós')
                break
