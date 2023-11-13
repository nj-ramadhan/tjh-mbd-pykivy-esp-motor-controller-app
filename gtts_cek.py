# pip install --upgrade wheel

from gtts import gTTS
import os
import time
import playsound

def speak(text):
    tts = gTTS(text=text, lang='id', slow=False)
    filename = 'voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)

speak ('silahkan atur ketinggian tumbler anda dengan menekan tombol naik dan turun')