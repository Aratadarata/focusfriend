import os
import speech_recognition as sr
from gtts import gTTS
import wikipediaapi
import sqlite3
from googlesearch import search

# Configurar el idioma de la API de Wikipedia
wiki_lang = wikipediaapi.Wikipedia('es')

# Crear y/o conectarse a la base de datos
conn = sqlite3.connect('pacientes.db')

# Crear tabla para pacientes si no existe
conn.execute('''CREATE TABLE IF NOT EXISTS pacientes
                (id INTEGER PRIMARY KEY,
                 nombre TEXT NOT NULL,
                 datos TEXT NOT NULL);''')

# Funciones para interactuar con el asistente
def escuchar():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        texto = r.recognize_google(audio, language='es-ES')
        return texto
    except:
        return None

def hablar(texto):
    tts = gTTS(texto, lang='es')
    tts.save('respuesta.mp3')
    os.system('mpg123 respuesta.mp3')

def buscar_en_wikipedia(consulta):
    pagina = wiki_lang.page(consulta)
    return pagina.summary[0:250]

def buscar_en_google(consulta):
    resultados = [j for j in search(consulta, num_results=3)]
    return resultados

def guardar_paciente(nombre, datos):
    conn.execute("INSERT INTO pacientes (nombre, datos) VALUES (?, ?)", (nombre, datos))
    conn.commit()

def obtener_datos_paciente(nombre):
    cursor = conn.execute("SELECT datos FROM pacientes WHERE nombre=?", (nombre,))
    datos = cursor.fetchone()
    if datos:
        return datos[0]
    else:
        return None

# Interactuar con el asistente
while True:
    # Escuchar al usuario y procesar su consulta
    consulta = escuchar()
    if consulta is not None:
        consulta = consulta.lower()
        palabras = consulta.split()

        if "wikipedia" in palabras:
            tema = ' '.join(palabras[palabras.index("wikipedia") + 1:])
            resultado = buscar_en_wikipedia(tema)
            hablar(resultado)

        elif "buscar" in palabras:
            tema = ' '.join(palabras[palabras.index("buscar") + 1:])
            resultados = buscar_en_google(tema)
            hablar(f"He encontrado los siguientes resultados: {', '.join(resultados)}")

        elif "guardar" in palabras and "paciente" in palabras:
            nombre = palabras[palabras.index("paciente") + 1]
            datos = ' '.join(palabras[palabras.index("datos") + 1:])
            guardar_paciente(nombre, datos)
            hablar(f"Datos guardados para el paciente {nombre}")

        elif "obtener" in palabras and "paciente" in palabras:
            nombre = palabras[palabras.index("paciente") + 1]
            datos = obtener_datos_paciente(nombre)
            if datos:
                hablar(f"Datos del paciente {nombre}: {datos}")
            else:
                hablar(f"No se encontraron datos para el paciente {nombre}")

        elif "salir" in palabras or "adiós" in palabras or "chao" in palabras:
            hablar("Adiós, que tengas un buen día.")
            break

        else:
            hablar("No entendí la consulta, por favor inténtalo de nuevo.")
