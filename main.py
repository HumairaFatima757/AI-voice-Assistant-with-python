from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from threading import Thread

# voice assistant libraries
import pyaudio
import wave
import datetime
import speech_recognition as sr
from gtts import gTTS
import playsound
from pydub import AudioSegment
import webbrowser
import pyautogui
import wikipedia
import requests
import os
import pygame
import smtplib
# import androidhelper
import pyjokes



# Define the root layout
class RootScreen(Screen):
    pass

# Define the second screen
class SecondScreen(Screen):
    pass


# Define the app
class MyApp(App):
    activities = []
    listeningToTodo = False
    def build(self):
        Builder.load_file('my_layout.kv')
        sm = ScreenManager()
        root_screen = RootScreen(name='root')
        second_screen = SecondScreen(name='second_screen')
        sm.add_widget(root_screen)
        sm.add_widget(second_screen)
        return sm


    # Method to run voice bot
    def run_voice_assistant(self):
        # Your existing code for the voice assistant functions
        # recognizer = sr.Recognizer()

        # def open_application(app_name):
        #     droid = androidhelper.Android()
        #     app_name = app_name.lower()
        #     if app_name == "whatsapp":
        #         droid.startActivity("android.intent.action.MAIN", None, None, None, False, "com.whatsapp", "com.whatsapp.HomeActivity")
        #     elif app_name == "browser":
        #         droid.startActivity("android.intent.action.VIEW", "https://www.google.com", None, None, False, None, None)
        #     elif app_name == "music":
        #         # You would need to replace com.example.musicapp with the actual package name of your music app.
        #         droid.startActivity("android.intent.action.MAIN", None, None, None, False, "com.example.musicapp", None)
        #     elif app_name == "messaging":
        #         # You would need to replace com.example.messagingapp with the actual package name of your messaging app.
        #         droid.startActivity("android.intent.action.MAIN", None, None, None, False, "com.example.messagingapp", None)
        #     elif app_name == "calendar":
        #         # You would need to replace com.example.calendarapp with the actual package name of your calendar app.
        #         droid.startActivity("android.intent.action.MAIN", None, None, None, False, "com.example.calendarapp", None)
        #     else:
        #         second_screen = self.root.get_screen('second_screen')
        #         second_screen.ids.caption_label.text = "Sorry, I can't open that application." + '\n'
        #         print("Sorry, I can't open that application.")

        def open_gmail_composer():
            gmail_url = f"https://mail.google.com/mail/u/0/#inbox?compose=new"
            webbrowser.open(gmail_url)

        def tell_joke():
            clean_joke = pyjokes.get_joke(category='neutral')
            return clean_joke

        def open_application(app_name):
            if app_name.lower() == "whatsapp":
                os.system("whatsapp.exe")
            elif app_name.lower() == "notepad":
                os.system("notepad.exe")
            elif app_name.lower() == "calculator":
                os.system("calc.exe")
            elif app_name.lower() == "browser":
                webbrowser.open("https://www.google.com")
            else:
                second_screen = self.root.get_screen('second_screen')
                second_screen.ids.caption_label.text = "Sorry, I can't open that application." + '\n'
                print("Sorry, I can't open that application.")

        def process_command(command):
            app_name = command.replace("open ", "").strip()
            second_screen = self.root.get_screen('second_screen')
            second_screen.ids.caption_label.text = app_name + '\n'
            print(app_name)
            open_application(app_name)

        def listen_for_command():
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                second_screen = self.root.get_screen('second_screen')
                second_screen.ids.caption_label.text = "Listening for commands..." + '\n'
                second_screen.ids.response_label.text = ""  # Reset response label text
                print("Listening for commands...")

                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                second_screen = self.root.get_screen('second_screen')
                second_screen.ids.caption_label.text = "You said: " + command + '\n'
                print("You said:", command)
                return command.lower()
            except sr.UnknownValueError:
                second_screen = self.root.get_screen('second_screen')
                second_screen.ids.caption_label.text = "Sorry, I could not understand what you said." + '\n'
                print("Sorry, I could not understand what you said.")
                return None
            except sr.RequestError:
                second_screen = self.root.get_screen('second_screen')
                second_screen.ids.caption_label.text = "Sorry, there was an error with the Google Speech Recognition API." + '\n'
                print("Sorry, there was an error with the Google Speech Recognition API.")
                return None
            except Exception as e:
                second_screen = self.root.get_screen('second_screen')
                second_screen.ids.caption_label.text = "An error occurred" + '\n'
                print("An error occurred.", e)
                return None

        def respond(response_text):
            second_screen = self.root.get_screen('second_screen')
            second_screen.ids.response_label.text = response_text + '\n'
            print(response_text)
            tts = gTTS(text=response_text, lang='en')
            tts.save("response.mp3")
            # playsound.playsound("response.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("response.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Adjust the tick rate if needed
            pygame.mixer.quit()
            os.remove("response.mp3")  # Remove the temporary audio file after playing

        def record_audio(duration=5, chunk_size=1024, sample_format=pyaudio.paInt16, channels=1, sample_rate=44100):
            audio = pyaudio.PyAudio()
            stream = audio.open(format=sample_format, channels=channels, rate=sample_rate, frames_per_buffer=chunk_size,
                                input=True)
            second_screen = self.root.get_screen('second_screen')
            second_screen.ids.response_label.text = "Recording..." + '\n'
            print("Recording...")
            frames = []
            for _ in range(int(sample_rate / chunk_size * duration)):
                data = stream.read(chunk_size)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            audio.terminate()
            second_screen = self.root.get_screen('second_screen')
            second_screen.ids.response_label.text = "Finished recording." + '\n'
            print("Finished recording.")
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"recorded_audio_{timestamp}.wav"
            with wave.open(file_name, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(audio.get_sample_size(sample_format))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
            second_screen = self.root.get_screen('second_screen')
            second_screen.ids.response_label.text = f"Audio saved as {file_name}" + '\n'
            print(f"Audio saved as {file_name}")
            return file_name

        def search_wikipedia(query):
            try:
                summary = wikipedia.summary(query, sentences=1)
                return summary
            except wikipedia.exceptions.DisambiguationError as e:
                return "Wikipedia page not working right now"
            except wikipedia.exceptions.PageError as e:
                return "Wikipedia page not working right now"
            except Exception as e:
                return "Wikipedia page not working right now"

        def get_current_time():
            now = datetime.datetime.now()
            meridiem = "AM" if now.hour < 12 else "PM"
            hour = now.hour % 12
            if hour == 0:
                hour = 12
            minute = str(now.minute).zfill(2)
            time_str = f"It is {hour}:{minute} {meridiem}."
            return time_str

        def get_current_date():
            now = datetime.datetime.now()
            date_str = now.strftime("Today is %A, %B %d, %Y.")
            return date_str

        # WEATHER FUNCTION
        def get_weather(city):
            # p61EYikaH75Wi4KxTr5BGGpHFVrRulzi

            api_key = "p61EYikaH75Wi4KxTr5BGGpHFVrRulzi"
            base_url = "http://dataservice.accuweather.com/currentconditions/v1/"
            location_key = "261158"  # You can obtain this from AccuWeather or use the city name directly if supported
            params = {
                "apikey": api_key,
                "details": "true",
            }
            complete_url = f"{base_url}{location_key}"
            response = requests.get(complete_url, params=params)
            data = response.json()
            if response.status_code == 200 and data:
                weather_description = data[0]["WeatherText"]
                temperature = data[0]["Temperature"]["Metric"]["Value"]
                return f"The weather in {city} is {weather_description} with a temperature of {temperature} degrees Celsius."
            else:
                return "Sorry, I couldn't retrieve the weather information."



        respond("Welcome to Your Personal AI assistant, What do you want to say?")

        while True:
            # global activities
            # global listeningToTodo
            command = listen_for_command()
            if command:
                   
                if "add activity" in command or "activity" in command:
                  self.listeningToTodo = True
                  while self.listeningToTodo:
                     command = listen_for_command()  # Get the next command
                     if command is not None:
                            if "no more activities" in command:
                              self.listeningToTodo = False
                              respond("Okay, stopping. You have " + str(len(self.activities)) + " activities currently in your list.")
                            elif "add activity" in command or "activity" in command:
                               self.listeningToTodo = True
                               respond("Sure, what is the activity?")
                            else:
                                self.activities.append(command)
                                respond("Adding '" + command + "' to your activities list. You have " + str(len(self.activities)) + " activities currently in your list.")
                                respond("What is the next activity?")
                     else:
                             respond("Sorry, I couldn't understand your command. Please try again.")

                elif "weather" in command:
                    city = "Karachi"  # Replace with the desired city name
                    weather_info = get_weather(city)
                    respond(weather_info)
                elif any(word in command for word in
                         ["open whatsapp", "whatsapp", "open notepad", "notepad", "open calculator"]):
                    process_command(command)
                elif ("take a screenshot" or "ss" or "capture ss") in command:
                    pyautogui.screenshot("screenshot.png")
                    respond("I took a screenshot for you.")
                elif ("open youtube" or "youtube" or "open the youtube") in command:
                    respond("Opening YouTube.")
                    webbrowser.open("https://www.youtube.com/")
                elif "open google" in command.lower() or "open the google" in command.lower() or "google" in command.lower():
                    respond("Opening Google....")
                    webbrowser.open("https://www.google.com/")
                elif "tell me a joke" in command or "joke" in command:
                    joke = tell_joke()
                    respond("Sure! Here's a joke:")
                    respond(joke)
                    # OPEN GOOGLE KEEP
                elif "open notes" in command or "open google keep" in command:  # Input: open notes or open google keep
                    respond("Opening Google Keep.")
                    webbrowser.open("https://keep.google.com/")

                elif ("record audio" or "audio record" or "audio recorder" or "record the audio") in command:  # Input: record audio
                    respond("Starting audio recording. Speak now.")
                    audio_file = record_audio()
                    respond("Audio recording complete. ")
                elif "time" in command:  # Input: Tell me the time?
                    time_str = get_current_time()
                    respond(time_str)
                elif "date" in command or "today" in command:  # input: What is today's date?
                    date_str = get_current_date()
                    respond(date_str)
                elif any(word in command for word in ["who", "what", "how", "when", "where"]):  # Input: Who is __________?
                    wiki_summary = search_wikipedia(command)
                    respond(wiki_summary)
                elif "exit" in command:
                    respond("Goodbye!")
                    break
                elif "email" in command or "send email" in command or "gmail" in command or "open gmail" in command or "open email composer" in command:
                    open_gmail_composer()
                else:
                    respond("Sorry, I'm not sure how to handle that command.")


    # Method to switch to the second screen
    def switch_to_second_screen(self):
        self.root.current = 'second_screen'

        # Call the method to run the voice bot when the button is clicked
        voice_bot_thread = Thread(target=self.run_voice_assistant)
        voice_bot_thread.daemon = True
        voice_bot_thread.start()

if __name__ == '__main__':
    app = MyApp()
    app.run()
    





















