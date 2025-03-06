import google.generativeai as genai
from google.api_core import exceptions 
import pandas as pd # Import for exception handling
import pyttsx3
import speech_recognition as sr

api_keys = ["AIzaSyB8m_g5zV1oyLB4aiOlJLz_2JYJDB2qWMw", "AIzaSyD2_tdcwwPs4tlwfeD33GLu9fBFt7dTBP4", "AIzaSyAPq4ipEARK_6X_JPMME-vUEyXZeCmfo9s"]
current_key_index = 0

def get_api_key():
    global current_key_index
    key = api_keys[current_key_index]
    current_key_index = (current_key_index + 1) % len(api_keys)
    return key

def say_text(text,speed):
  # Split text into chunks (replace with actual segmentation logic)
  chunks = text.split(". ")

  text_speech = pyttsx3.init()
  #print(speed)
  text_speech.setProperty('rate',speed)
  for chunk in chunks:
    # Estimate time for each chunk (replace with timing logic)
    estimated_time = len(chunk) / 100  # Placeholder: 100 words per second

    text_speech.say(chunk)
    # Display the subtitle chunk for estimated_time duration (implementation needed)

    text_speech.runAndWait()


# Initialize recognizer
r = sr.Recognizer()

# Use the microphone as the source for input and calibrate it once
with sr.Microphone() as source:
    print("Please wait. Calibrating microphone...")
    # Listen for 5 seconds and create the ambient noise energy level
    r.adjust_for_ambient_noise(source, duration=5)
    print("Microphone calibrated.")

def listen():
    # Use the already calibrated microphone source
    with sr.Microphone() as source:
        print("Tell me your Query!")
        speed=300
        say_text("Tell me your Query",300)

        # Capture the audio data
        audio_data = r.listen(source)

        print("Recognizing...")

        # Recognize speech using Google Web Speech API
        try:
            text = r.recognize_google(audio_data)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return "repeat"
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return ""
        
def preprocess_data(file_path):
    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)
    
    # Optional: Remove rows with missing values in important columns
    df = df.dropna(subset=['ID', 'Faculty Name', 'Position', 'Mobile Number', 'Email ID', 'Cabin Number'])
    
    # Optional: Clean data by stripping extra spaces or handling empty fields
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df[df['Faculty Name'] != '']  # Ensure 'Faculty Name' is not empty
    
    professors_info = "The following is a list of professors and their details:\n"
    
    # Loop through the rows and construct the information
    for _, row in df.iterrows():
        professors_info += (f"ID: {row['ID']}, Name: {row['Faculty Name']}, Position: {row['Position']}, "
                            f"Mobile: {row['Mobile Number']}, Email: {row['Email ID']}, "
                            f"Cabin Number: {row['Cabin Number']}.\n")
    
    return professors_info
        

def chat_loop(api_key):
    file_path = 'Profs_name.xlsx'  # Replace with your Excel file path
    professors_info = preprocess_data(file_path)
    #print(professors_info)
    #print(df)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    query_count = 0
    
    while True:
        #user_input = input("You: ").lower()  # Convert input to lowercase for case-insensitive termination
        user_input=listen()
        if user_input == "stop":
            break
        if user_input == "repeat":
            continue

        if query_count % 2 == 0:  # Rotate API key every 5 queries
            api_key = get_api_key()
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            chat = model.start_chat(history=[])

        user_input_l = (f"Here is the context of professor details:\n{professors_info}\n\n"
                  f"Now, based on the above information, answer the following question:\n{user_input}")
        #print(user_input_l)  # Uncomment if you want to see the formatted user input
        #user_input_d = "i need a 2 comma seperated word reply with 2 colours that best represents " + user_input + "for a dark mode application from the give list of colours that are given in their hex codes" + str(samsung_clrs)
        #print(user_input_l)  # Uncomment if you want to see the formatted user input
        
        try:
            response_l = chat.send_message(user_input_l)
            print(f"Linda: {response_l.text}")
            speed = 200  # Adjust speed as needed
            say_text(f"{response_l.text}", speed)
        except exceptions.ResourceExhausted:
            print("API quota exceeded. Please try again later.")
            break

        #response_b = chat.send_message(user_input_d)
        #print(f"Dark: {response_b.text}")

    #AIzaSyB8m_g5zV1oyLB4aiOlJLz_2JYJDB2qWMw