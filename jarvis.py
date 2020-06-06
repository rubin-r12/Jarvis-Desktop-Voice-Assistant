from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import random
import smtplib
import pytz


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENSIONS = ["rd", "th", "st", "nd"]
CALENDAR_STRS = ["what do i have", "do i have plans","am i busy"] 

def speak(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice',voices[1].id)
    engine.say(text)
    engine.runAndWait()


def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_events(day, service):

    if day == None:
        return
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())

    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)


    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax = end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("+")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12)
                start_time = start_time + "pm"
            
            speak(event["summary"] + " at " + start_time)


def get_date(text):
    # Deriving date from text representing speech
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month != -1:
        year += 1
    
    if day < today.day and month == -1 and day != -1:
        month += 1
    
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7
        return today + datetime.timedelta(dif)
    
    if month == -1 or day == -1:
        return None
    return datetime.date(month=month, day=day, year=year)


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")

    else:
        speak("Good Evening!")
    
    speak("I am Jarvis. Please tell me how can I help you")

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.login('youremail@email.com','pass')
    server.sendmail('youremail@email.com', to, content)
    server.close()

def takeCommand():
    '''it takes microphone input from the user and returns string output
    '''
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        text = r.listen(source)

    try:
        print("Recognizing...")
        text =  r.recognize_google(text, language = 'en-in')
        print(f"User said: {text}\n")

    except Exception as e:
        # print(e)
        print("Please try again.")
        return "None"
    return text

if __name__ == "__main__":

    service = authenticate_google()
    wishMe()

    while True:
        text = takeCommand().lower()

        if 'event'in text:
            # speak('sure sir, what should i look for?')
            # text = takeCommand().lower()
            try:
                for phrase in CALENDAR_STRS:
                    if phrase in text:
                        date = get_date(text)
                        if date:
                            get_events(date, service)
            except Exception as e:
                # print(e)
                speak('Please try again.')
             
            date = get_date(text)
            get_events(date, service) 
             

        #searching wikipedia based on text
        elif 'wikipedia' in text:
            speak('Searching Wikipedia...')
            text = text.replace("wikipedia","")
            results = wikipedia.summary(text, sentences = 2)
            speak("According to Wikipedia")
            print(results)
            speak(results)
        
        #opening youtube
        elif 'open youtube' in text:
            webbrowser.open("youtube.com")

        #opening google
        elif 'open google' in text:
            webbrowser.open("google.com")
        
        #playing music
        elif'play' in text:
            music_dir = 'C:\\Users\\91741\\Documents\\Friends'
            songs = os.listdir(music_dir)
            n = random.randint(0,len(songs))
            os.startfile(os.path.join(music_dir, songs[n]))

        #Speaking current time
        elif 'time' in text:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, The time is {strTime}")

        #opening VS code
        elif 'code' in text:
            codePath = "C:\\Users\\91741\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            os.startfile(codePath)
        
        #sending an email
        elif 'mail' in text:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "receiveremail@email.com"
                sendEmail(to, content)
                speak("Email has been sent!")
            except Exception as e:
                print(e)
                speak("Sorry! I cant send it now. Please try again later.")
        elif 'quit' or 'bye' in text:
            speak("Bye, See you later!")
            exit()                
        

