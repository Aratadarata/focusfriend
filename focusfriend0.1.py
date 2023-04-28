import os
import time
import webbrowser
import wikipedia
import speech_recognition as sr
import pyttsx3

from datetime import datetime

# Inicialización del motor de voz
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) # 0 = masculino, 1 = femenino

def speak(text, rate=120):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def parseCommand():
    listener = sr.Recognizer()
    print('Escuchando un comando')

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)

    try:
        print('Reconociendo voz...')
        query = listener.recognize_google(input_speech, language='es')
        print(f'El discurso de entrada fue: {query}')

    except Exception as exception:
        print('No entendí eso')
        print(exception)

        return 'None'

    return query

def search_wikipedia(keyword=''):
    wikipedia.set_lang("es")
    searchResults = wikipedia.search(keyword)
    if not searchResults:
        return 'No se recibieron resultados'
    try:
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

if __name__ == '__main__':
    speak('Todos los sistemas están funcionando correctamente.')

    while True:
        query = parseCommand().lower().split()

        if query[0] == 'di':
            if 'hola' in query:
                speak('¡Hola a todos!')
            else:
                query.pop(0)  # Eliminar 'di'
                speech = ' '.join(query)
                speak(speech)

        if query[0] == 've' and query[1] == 'a':
            speak('Abriendo...')
            query = ' '.join(query[2:])
            webbrowser.open_new(query)

        if query[0] == 'wikipedia':
            query = ' '.join(query[1:])
            speak('Consultando la base de datos universal')
            time.sleep(2)
            speak(search_wikipedia(query))

        if query[0] == 'anota':
            speak('Listo para grabar tu nota')
            newNote = parseCommand().lower()
            now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            with open('nota_%s.txt' % now, 'w') as newFile:
                newFile.write(now)
                newFile.write(' ')
                newFile.write(newNote)
            speak('Nota escrita')

        if query[0] == 'salir':
            speak('Adiós')
            break
