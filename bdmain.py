import json
import math
import os
import random
from openai import OpenAI
import sounddevice as sd
import wave
import numpy as np
import speech_recognition as sr


# 1. LADEN DER JSON DATEIEN (API & PROMPT)

api_key_folder = None
system_prompt = ""

# API-Key laden
try: 
    with open("api_key_folder.json", "r", encoding="utf-8") as file:
        api_key_data = json.load(file)
        api_key_folder = api_key_data["api_key"]
        print("API wird gelesen. YEYYYYY")
except Exception:
    print("Nüscht da mit API.")

# System Prompt laden
try:
    with open("system_prompt.json", "r", encoding="utf-8") as file: 
        prompt_data = json.load(file)
        if isinstance(prompt_data["system_prompt"], list):
            system_prompt = "\n".join(prompt_data["system_prompt"])
        else:
            system_prompt = prompt_data["system_prompt"]
except Exception as e:
    print(f"Fehler beim Laden des System Prompts: {e}")

# 2. OPENAI CLIENT INITIALISIEREN

if not api_key_folder:
    print("[Fehler]: Ohne API-Key kann das Programm nicht starten.")
    exit()

client = OpenAI(api_key=api_key_folder)

# Chat-Verlauf starten und den System Prompt verankern
messages = [
    {"role": "system", "content": system_prompt}
]

# 3. LIVE-SPRACHERKENNUNG & API-ANTWORT

def live_spracherkennung():
    recognizer = sr.Recognizer()
    
    # Zuhören
    # 2 sek Stille abwarten bevor du das Zuhören beendest 
    recognizer.pause_threshold = 2.0  
    # Wie lange muss Stille herrschen, nachdem Sprache erkannt wurde (Standard ist 0.5)
    recognizer.non_speaking_duration = 1.0

    # Mikrofon als Audioquelle nutzen
    with sr.Microphone() as source:
        print("Mikrofon wird kalibriert")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Ich höre zu.")
        
        while True:
            try:
                # ANPASSUNG: phrase_time_limit von 5 auf 15 Sekunden erhöht
                audio = recognizer.listen(source, phrase_time_limit=15)
                
                # Text via Google API umwandeln
                user_text = recognizer.recognize_google(audio, language="de-DE")
                print(f"\nDu: {user_text}")
                
                # Benutzereingabe dem Chat-Verlauf hinzufügen
                messages.append({"role": "user", "content": user_text})
                print("Roboter denkt nach...", end="\r")
                
                # Anfrage an OpenAI senden
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7
                )
                
                # Antwort extrahieren
                bot_response = response.choices[0].message.content
                print(f"Lumi: {bot_response}")
                
                # Antwort dem Verlauf hinzufügen
                messages.append({"role": "assistant", "content": bot_response})
                
            except sr.UnknownValueError:
                # Wird ausgelöst, wenn das Mikrofon Geräusche, aber keine Wörter erkennt
                pass
            except sr.RequestError as e:
                print(f"\n[Fehler]: Verbindungsproblem mit dem Sprachdienst: {e}")
            except Exception as e:
                print(f"\n[Fehler bei der API-Anfrage]: {e}")
            except KeyboardInterrupt:
                print("\n Programm beendet")
                break

if __name__ == "__main__":
    live_spracherkennung()

# wake words 
#wake_words = [ "Lumi ", "" ]

# neutrale Kopfposition 
