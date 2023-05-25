from typing import Sequence

import google.cloud.texttospeech as tts

import requests

import wave

#TOKEN = "XXX"


def unique_languages_from_voices(voices: Sequence[tts.Voice]):
    language_set = set()
    for voice in voices:
        for language_code in voice.language_codes:
            language_set.add(language_code)
    return language_set


def list_languages():
    client = tts.TextToSpeechClient()
    response = client.list_voices()
    languages = unique_languages_from_voices(response.voices)

    print(f" Languages: {len(languages)} ".center(60, "-"))
    for i, language in enumerate(sorted(languages)):
        print(f"{language:>10}", end="\n" if i % 5 == 4 else "")

def list_voices(language_code=None):
    client = tts.TextToSpeechClient()
    response = client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)

    print(f" Voices: {len(voices)} ".center(60, "-"))
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = tts.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz
        print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")

def text_to_wav(voice_name: str, text: str):
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams(
        language_code=language_code, name=voice_name
    )
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
    )

    filename = f"{voice_name}.wav"
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Generated speech saved to "{filename}"')

"""
def tel_send_wav(chat_id, wav_file_path):
    url = f'https://api.telegram.org/bot{TOKEN}/sendVoice'
    files = {'voice': open(wav_file_path, 'rb')}
    data = {'chat_id': chat_id}

    r = requests.post(url, data=data, files=files)
    return r
"""

"""
the springer nature api is the worst thing i've ever tried
import requests
import json
from datetime import datetime, timedelta

api_key = "9ac96840fcf9f785d97370b77e9ce5a7"

abstracts = []

for x in range(0, 7):
    date = (datetime.today() - timedelta(days=x)).strftime('%Y-%m-%d')
    #url = "http://api.springernature.com/meta/v2/json?q=:"+str(date)+"&api_key="+api_key
    url = "http://api.springernature.com/meta/v2/json?q=journal:nature&api_key="+api_key

    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        results = json.loads(response.text)

    for obj in results['records']:
        if 'abstract' in obj:
            abstracts.append(obj['abstract'])
"""           
from bs4 import BeautifulSoup
import datetime
 
titles = []
summary_texts = []
datetime_list = []
journal_flags = []

journals = ["nature", "ng", "nbt", "ncomms", "nataging", "natbiomedeng", "natcancer", "natcardiovascres", "ncb", "ncb", "nm", "nmeth", "nprot", "natrevbioeng", "nrc", "nrcardio", "natrevchem", "nrclinonc", "nrg", "nrm", "nsmb"]

num = 11
today = datetime.date.today() - datetime.timedelta(days=int(num)) # for biorxiv, three days ago TO GET ABSTRACTS (also 0 for titles), as DOI updates on biorxiv with about 3 days of delay

for jour in journals:
    for x in range(1,10):
        print(x)
        url = str("https://www.nature.com/search?order=relevance&journal="+str(jour)+"&date_range=2023-2023&page=" + str(x))

        response = requests.get(url)

        if response.status_code == 200:
            html_content = response.content
        else:
            print("Error retrieving HTML content:", response.status_code)

        # Create a BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all the div elements with class "c-card__body"
        card_bodies = soup.find_all('div', class_='c-card__body')

        # Loop through each div element
        for card_body in card_bodies:
            # Find the h3 element with class "c-card__title" and get its text
            title = card_body.find('h3', class_='c-card__title').get_text(strip=True)
            titles.append(title)
            journal_flags.append(jour)

        summaries = soup.find_all("div", class_="c-card__summary")
        # Extract the text from the summaries and store them in a list
        for summary in summaries:
            summary_text = summary.get_text().strip()
            summary_texts.append(summary_text)
        
        # find all elements with class="c-meta__item" and data-test="article.type"
        type_elements = soup.find_all('span', {'class': 'c-meta__item', 'data-test': 'article.type'})

        # extract the text content of each element - to later select maybe only papers & reviews
        type_values = [elem.find('span', {'class': 'c-meta__type'}).text.strip() for elem in type_elements]
       
        # find all time elements with datetime attribute
        for time_elem in soup.find_all('time', {'datetime': True}):
            datetime_list.append(time_elem['datetime'])
             
today_titles = [e for e, flag in zip(titles, [elem == str(today) for elem in datetime_list]) if flag]
today_journals = [e for e, flag in zip(journal_flags, [elem == str(today) for elem in datetime_list]) if flag]
today_summaries = [e for e, flag in zip(summary_texts, [elem == str(today) for elem in datetime_list]) if flag]
today_types = [e for e, flag in zip(type_values, [elem == str(today) for elem in datetime_list]) if flag]

message = "Hello! Nice to have you hear on Paper Boat, skimming through paper titles under the sun, \
    drinking preprints and sailing the sea of downloads! I hope that your week was great. On this podcast, we report the summaries of the major \
    publications of last week in the bio space in Nature journals. Please bear in mind this is an experimental feature."

one_week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
week_summaries = [e for e, date_str in zip(summary_texts, datetime_list) 
                  if datetime.datetime.strptime(date_str, '%Y-%m-%d').date() >= one_week_ago.date() 
                  and datetime.datetime.strptime(date_str, '%Y-%m-%d').date() <= datetime.datetime.today().date()]

week_summaries_str = message +"\n\n".join(week_summaries)

with open('digest.txt', 'w', encoding='utf-8') as f: 
    f.write(week_summaries_str)

msg = message


import os
import wave

text_to_wav("en-US-Neural2-H", message)
original_file_name = 'en-US-Neural2-H.wav'
new_file_name = 'comb.wav'
os.rename(original_file_name, new_file_name)
        
for j in range(0,len(week_summaries)):
    try:
        text_to_wav("en-US-Neural2-H", week_summaries[j])
        with wave.open('comb.wav', 'rb') as wav1:
            with wave.open('en-US-Neural2-H.wav', 'rb') as wav2:
                params1 = wav1.getparams()
                params2 = wav2.getparams()
                with wave.open('combined.wav', 'wb') as wav_combined:
                    wav_combined.setparams(params1)
                    data = wav1.readframes(wav1.getnframes())
                    wav_combined.writeframes(data)
                    data = wav2.readframes(wav2.getnframes())
                    wav_combined.writeframes(data)
        os.rename("combined.wav", "comb.wav")
    except Exception as e:
        print(e)
 
import os
import math

MAX_CHUNK_SIZE = 48 * 1024 * 1024  # 50 MB in bytes

# Open the input file for reading
with wave.open('comb.wav', 'rb') as input_file:
    # Determine the number of output files needed
    num_output_files = math.ceil(input_file.getnframes() * input_file.getsampwidth() / MAX_CHUNK_SIZE)

    # Split the input file into smaller chunks and write each chunk to a separate output file
    for i in range(num_output_files):
        output_file_name = f'comb{i+1}.wav'
        with wave.open(output_file_name, 'wb') as output_file:
            # Set the parameters of the output file to match the input file
            output_file.setnchannels(input_file.getnchannels())
            output_file.setsampwidth(input_file.getsampwidth())
            output_file.setframerate(input_file.getframerate())

            # Determine the number of frames to read from the input file
            num_frames = min(MAX_CHUNK_SIZE // input_file.getsampwidth(), input_file.getnframes() - input_file.tell())

            # Read the frames from the input file and write them to the output file
            frames = input_file.readframes(num_frames)
            output_file.writeframes(frames)

# Print the total size of the output files
total_output_size = sum(os.path.getsize(f'comb{i+1}.wav') for i in range(num_output_files))
print(f'Total size of output files: {total_output_size / (1024 * 1024):.2f} MB')
#tel_send_wav(586828009, "/home/fusar/paperboat/comb.wav")
