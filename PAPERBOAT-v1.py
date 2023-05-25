import requests
from flask import Flask
from flask import request
from flask import Response
from scihub import SciHub # scihub part: source -> https://github.com/zaytoun/scihub.py
import os
import re
import random
import json
import datetime
from bs4 import BeautifulSoup
from pyzotero import zotero

try:
    with open('telegram_key.txt', 'r') as file:
        TOKEN = file.read()
except Exception as e:
        print(e)

try:
    with open('zotero_key.txt', 'r') as file:
        ZOTapi_key = file.read()
except Exception as e:
        print(e)

try:
    with open('zotero_id.txt', 'r') as file:
        library_id = file.read()
except Exception as e:
        print(e)

try:
    with open('openai_key.txt', 'r') as file:
        openai_key = file.read()
except Exception as e:
        print(e)

TOKEN='your_token'

library_type = 'user'
zot = zotero.Zotero(library_id, library_type, ZOTapi_key)

app = Flask(__name__)

def parse_message(message):
    print("message-->",message)
    if 'message' not in message or 'chat' not in message['message'] or 'id' not in message['message']['chat'] or 'text' not in message['message']:
        return None, None
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id, txt

def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    r = requests.post(url, json=payload)
    return r

last_txt = str()
"""
def tel_send_pdf(chat_id, pdf_file_path):
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
    files = {'document': open(pdf_file_path, 'rb')}
    data = {'chat_id': chat_id}
    r = requests.post(url, data=data, files=files)
    return r
"""

def tel_send_pdf(chat_id, pdf_file_path):
    url = f'https://api.telegram.org/bot{TOKEN}/sendDocument'
    files = {'document': open(pdf_file_path, 'rb')}
    data = {'chat_id': chat_id}
    timeout = 100
    r = requests.post(url, data=data, files=files, timeout=timeout)
    return r


def tel_send_wav(chat_id, wav_file_path):
    url = f'https://api.telegram.org/bot{TOKEN}/sendVoice'
    files = {'voice': open(wav_file_path, 'rb')}
    data = {'chat_id': chat_id}

    r = requests.post(url, data=data, files=files)
    return r

def partition_string(message):
    max_length = 4096
    lines = message.split("\n")
    partitions = []
    current_partition = ""

    for line in lines:
        if len(current_partition + line) <= max_length:
            current_partition += line + "\n"
        else:
            partitions.append(current_partition)
            current_partition = line + "\n"

    if current_partition:
        partitions.append(current_partition)

    return partitions

def convert_title_to_doi(title):
    url = f"https://api.crossref.org/works?query.title={title}"
    response = requests.get(url)
    if response.status_code == 200:
        results = json.loads(response.content)['message']['items']
        if len(results) > 0:
            return results[0]['DOI']
    return None

def add_to_zotero(title, doi):
    template = zot.item_template('journalArticle')
    template['DOI'] = doi
    template['title'] = title
    resp = zot.create_items([template])
    return None

def convert_today_url(number):
    with open('TodayPapers.txt', 'r', encoding='utf-8') as file:
            contents = file.read()
    rows = contents.strip().split('\n')
    table = [row.split('$') for row in rows] ############
    tit = table[number-1]
    if tit[1] == "biorXiv":
        ########################################
        today = datetime.date.today() - datetime.timedelta(days=1) # for biorxiv, three days ago TO GET ABSTRACTS (also 0 for titles), as DOI updates on biorxiv with about 3 days of delay
        url = "https://www.biorxiv.org/search/jcode%3Abiorxiv%20limit_from%3A"+str(today)+"%20limit_to%3A"+str(today)+"%20numresults%3A1000%20sort%3Arelevance-rank%20format_result%3Astandard"
        titles = []
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.content
        soup = BeautifulSoup(html_content, "html.parser")

        table = []

        for cite in soup.find_all("div", class_="highwire-cite highwire-cite-highwire-article highwire-citation-biorxiv-article-pap-list clearfix"):
            title = cite.find("span", class_="highwire-cite-title").text.strip()
            doi = re.findall(r'\b10\.\d+\/\S+(?=")', str(cite))[0]
            table.append([title, doi])
        title = tit[0]
        for first, second in table:
            if first == title:
                doi = second
        return doi
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    info_bot_short = "Hey, welcome to Paper Boat! A peaceful place to relax scrolling the titles of today's papers and \
        preprints under the sun, and downloading papers from the past of human civilization while sailing this blue sea!\
        Info, manual, code, contact on GitHub: https://github.com/lucafusarbassini/paperboat"
    with open('infobot.txt', 'r') as file:
        info_bot = file.read()
    xt = ""

    try:
        if request.method == 'POST':
            chat_id, txt = parse_message(request.get_json())
            if chat_id is None or txt is None:
                return Response('ok', status=200)
            t = txt[:5]
            ti = txt[:9]
            td = txt[:10]
            tt = txt[:15]
            ta = txt[:7]
            if t == "/doi ":
                xt = txt[5:]
            if ti == "/biorxiv ":
                xt = txt[9:]
            if ta == "/arxiv ":
                xt = txt[7:]
            if td == "/download ":
                xt = txt[10:]
            if tt == "/downloadtoday ":
                xt = txt[15:]
            if txt == "/today":
                with open('TodayPapers.txt', 'r', encoding='utf-8') as file:
                    contents = file.read()

                rows = contents.strip().split('\n')
                table = [row.split('$') for row in rows]

                journal_to_papers = {}
                for row in table[0:]:
                    title, journal = row[0], row[1]
                    if journal not in journal_to_papers:
                        journal_to_papers[journal] = []
                    journal_to_papers[journal].append(title)

                message = "Papers published today:"

                j = 1

                for journal, papers in journal_to_papers.items():
                    message += f"\n\n\n*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n{journal}:\n*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n\n"
                    for i, paper in enumerate(papers, start=1):
                        message += f"({j}) {paper}\n\n"
                        j += 1
                for elem in partition_string(message):
                    tel_send_message(chat_id, elem)
            elif txt == "/doi":
                tel_send_message(chat_id, "Enter the DOI like this: /doi xxxxxxxxxxxx")
            elif txt == "/biorxiv":
                tel_send_message(chat_id, "Enter the biorXiv DOI like this: /biorxiv xxxxxxxxxxxx")
            elif txt == "/arxiv":
                tel_send_message(chat_id, "Enter the arXiv DOI like this: /arxiv xxxxxxxxxxxx")
            elif txt == "/download":
                tel_send_message(chat_id, "Enter the exact title of the paper like this: /download xxxxxxxxxxxx")
            elif txt == "/downloadtoday":
                tel_send_message(chat_id, "[Available only for biorXiv papers] Enter the number of the paper like this: /downloadtoday N")
            elif t == "/doi ":
                random_number = str(random.randint(1, 100000))
                sh = SciHub()
                result = sh.download(xt, path="papero"+random_number+".pdf")
                tel_send_pdf(chat_id, "papero"+random_number+".pdf")
                os.remove("papero"+random_number+".pdf")
            elif ti == "/biorxiv ":
                url = xt
                doi_pattern = re.compile(r"(10\.\d+\/\S+)")  # pattern for matching DOI
                match = doi_pattern.search(url)
                if match:
                    doi_substr = match.group(1)
                else:
                    return Response('ok', status=200)
                url = "https://www.biorxiv.org/content/"+doi_substr+"v1.full.pdf"
                response = requests.get(url)
                random_number = str(random.randint(1, 100000))
                with open("biorxiv"+random_number+".pdf", "wb") as f:
                    f.write(response.content)
                tel_send_pdf(chat_id, "biorxiv"+random_number+".pdf")
                os.remove("biorxiv"+random_number+".pdf")
            elif ta == "/arxiv ":
                url = xt
                doi_pattern = re.compile(r"\d+\.\d+$")   # pattern for matching DOI
                match = doi_pattern.search(url)
                if match:
                    doi_substr = match.group(0)
                else:
                    return Response('ok', status=200)
                url = "https://arxiv.org/pdf/"+doi_substr+".pdf"
                response = requests.get(url)
                random_number = str(random.randint(1, 100000))
                with open("arxiv"+random_number+".pdf", "wb") as f:
                    f.write(response.content)
                tel_send_pdf(chat_id, "arxiv"+random_number+".pdf")
                os.remove("arxiv"+random_number+".pdf")
            elif td == "/download ":
                title = xt
                doi = "https://doi.org/"+str(convert_title_to_doi(title))
                url = doi
                doi_pattern = re.compile(r"(10\.\d+\/\S+)")
                match = doi_pattern.search(url)
                if match:
                    doi_substr = match.group(1)
                else:
                    return Response('ok', status=200)
                url = "https://www.biorxiv.org/content/"+doi_substr+"v1.full.pdf"
                response = requests.get(url)
                if response:
                    random_number = str(random.randint(1, 100000))
                    with open("biorxiv"+random_number+".pdf", "wb") as f:
                        f.write(response.content)
                    tel_send_pdf(chat_id, "biorxiv"+random_number+".pdf")
                    os.remove("biorxiv"+random_number+".pdf")
                else:
                    sh = SciHub()
                    random_number = str(random.randint(1, 100000))
                    result = sh.download(doi, path="papero"+random_number+".pdf")
                    tel_send_pdf(chat_id, "papero"+random_number+".pdf")
                    os.remove("papero"+random_number+".pdf")
                url = "https://arxiv.org/pdf/"+doi_substr+".pdf"
                response = requests.get(url)
                if response:
                    random_number = str(random.randint(1, 100000))
                    with open("arxiv"+random_number+".pdf", "wb") as f:
                        f.write(response.content)
                    tel_send_pdf(chat_id, "arxiv"+random_number+".pdf")
                    os.remove("arxiv"+random_number+".pdf")
            elif tt == "/downloadtoday ":
                print(xt)
                url = convert_today_url(int(xt))
                print(url)
                doi_pattern = re.compile(r"(10\.\d+\/\S+)")  # pattern for matching DOI
                match = doi_pattern.search(url)
                print(match)
                if match:
                    doi_substr = match.group(1)
                else:
                    return Response('ok', status=200)
                url = "https://www.biorxiv.org/content/"+doi_substr+".full.pdf"
                print(url)
                response = requests.get(url)
                random_number = str(random.randint(1, 100000))
                with open("biorxiv"+random_number+".pdf", "wb") as f:
                    f.write(response.content)
                tel_send_pdf(chat_id, "biorxiv"+random_number+".pdf")
                os.remove("biorxiv"+random_number+".pdf")
            elif txt == "/info":
                tel_send_message(chat_id, info_bot)
            elif txt == "/github":
                tel_send_message(chat_id, "https://github.com/lucafusarbassini/paperboat")
            elif txt == "/digest":
                with open('digest.txt', 'r') as file:
                    digest = file.read()
                    for elem in partition_string(digest):
                        tel_send_message(chat_id, elem)
            elif txt == "/podcast":
                try:
                    tel_send_wav(chat_id, "/home/fusar/paperboat/comb1.wav")
                except Exception as e:
                    print(e)
                try:
                    tel_send_wav(chat_id, "/home/fusar/paperboat/comb2.wav")
                except Exception as e:
                    print(e)
                try:
                    tel_send_wav(chat_id, "/home/fusar/paperboat/comb3.wav")
                except Exception as e:
                    print(e)
                try:
                    tel_send_wav(chat_id, "/home/fusar/paperboat/comb4.wav")
                except Exception as e:
                    print(e)
                try:
                    tel_send_wav(chat_id, "/home/fusar/paperboat/comb5.wav")
                except Exception as e:
                    print(e)

            else:
                tel_send_message(chat_id, "Check out the Telegram menu for commands")
            return Response('ok', status=200)
        else:
            return "<h1>Welcome!</h1>"
    except Exception as e:
        print(e)
        return Response('ok', status=200)

if __name__ == '__main__':
   app.run(debug=True, port=5000)