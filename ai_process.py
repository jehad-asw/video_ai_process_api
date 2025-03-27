import os
from moviepy import VideoFileClip
import cv2
import json
import google.generativeai as genai
import speech_recognition as sr
import re

GEMINI_AI_KEY = "AIzaSyAqWjPTyAPGvvF0B2VlznyP440k-iZbgto"
if GEMINI_AI_KEY:
    genai.configure(api_key=GEMINI_AI_KEY)
AI_MODEL = "gemini-2.0-flash-exp"
UPLOAD_FOLDER = "videos"
RESULT_FOLDER = "results"
RESULT_FOLDER_DATA ="results.data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER_DATA, exist_ok=True)


def extract_key_frames(video_path, interval=5):
    """ Extracts key frames from a video every 'interval' seconds. """
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = []
    timestamps = []

    if not cap.isOpened():
        print(f"Error opening video file")
        return [], []
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % (fps * interval) == 0:
            timestamp = frame_count / fps
            hh_mm_ss = f"{int(timestamp // 3600):02}:{int((timestamp % 3600) // 60):02}:{int(timestamp % 60):02}"
            frame_path = os.path.join(RESULT_FOLDER_DATA, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_path, frame)
            frames.append(frame_path)
            timestamps.append(hh_mm_ss)
        frame_count += 1
    cap.release()
    return frames, timestamps



#Extracts audio from video and transcribes it to text.
def extract_audio(video_path):
    try:
        clip = VideoFileClip(video_path)
        audio_path = os.path.join(RESULT_FOLDER_DATA, "temp_audio.wav")
        clip.audio.write_audiofile(audio_path)

        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)

        text = r.recognize_google(audio)
        return text

    except Exception as e:
        print(f"Error extracting audio: {e}")
        return "Error extracting audio"


def analyze_with_gemini(frames, timestamps, audio_text):
    try:

        prompt = f"""
        Analyze the following video data and extract key moments.  For each key moment, provide a concise description and the corresponding timestamp. Return a list of json objects. Each object should have a 'time' and a 'text' field. 
        Consider the visual information from the key frames and the audio transcription to identify important events, topics, or changes in the scene.
        Here's the video data:  
        - **Key Frames and Timecodes**:
        """

        for i in range(len(frames)):
            prompt += f"\n  - Time: {timestamps[i]}, Frame: [Describe the visual content of frame {i}]"  # include the timestamp
            prompt += f"""
            
            - **Audio Transcription**: {audio_text}
            Example output:
            ```json
            [
              {{
                "time": "00:00:10",
                "text": "The presenter introduces the topic of the video."
              }},
              {{
                "time": "00:01:30",
                "text": "A graph showing increasing sales is displayed."
              }}
            ]
            ```
            """
        
        genai.configure(api_key=GEMINI_AI_KEY)
        model = genai.GenerativeModel(AI_MODEL)
        response = model.generate_content(prompt)

        try:

            #fetch the json part from Gemini response
            match = re.search(r"```json\n([\s\S]*?)\n```", response.text)
            if match:

                key_moments = json.loads(match.group(1))
                return key_moments

            else:
                print("No valid json found in response!")
                return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from Gemini response: {response.text}")
            return None

    except Exception as e:
        print(f"Error: {str(e)}")
        return "AI processing failed"


#this function run on 3 steps
#first extract the frames from the video
#then extract the audio (sound)
#send the data to Gemini ai to analyse it
#then save the result in json file into result folder
def run_ai_processing(file_path):
    try:
        # Extract key frames
        key_frames, timestamps = extract_key_frames(file_path, interval=5)

        # Extract audio (speech transcription)
        audio_text = extract_audio(file_path)

        # Analyze with Gemini AI
        key_moments = analyze_with_gemini(key_frames, timestamps, audio_text)

        if key_moments:
            # Prepare timecodes for setting
            timecodes = []
            for moment in key_moments:
                timecodes.append({"time": moment["time"], "text": moment["text"]})

            # Save results to json file in results folder
            video_filename = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(RESULT_FOLDER, f"{video_filename}.json")
            with open(output_path, "w") as f:
                json.dump({"key_moments": timecodes}, f, indent=4)

            return {"message": "AI processing complete", "key_moments": timecodes}
        else:
            return {"error": "AI analysis failed or returned no key moments."}


    except Exception as e:
        return {"error": str(e)}
