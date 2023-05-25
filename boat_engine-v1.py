# SET WEBHOOK WITH NGROK FIRST

import requests
import datetime
from bs4 import BeautifulSoup
import re
import sys

ALL_TITLES = []
ALL_JOURNALS = []

#num = int(sys.argv[1])

num = 1

#################
today = datetime.date.today() - datetime.timedelta(days=int(num)) # for biorxiv, three days ago TO GET ABSTRACTS (also 0 for titles), as DOI updates on biorxiv with about 3 days of delay

# biorXiv
url = "https://www.biorxiv.org/search/jcode%3Abiorxiv%20limit_from%3A"+str(today)+"%20limit_to%3A"+str(today)+"%20numresults%3A1000%20sort%3Arelevance-rank%20format_result%3Astandard"
titles = []
response = requests.get(url)
if response.status_code == 200:
    html_content = response.content
    # Parse the HTML using Beautiful Soup
    soup = BeautifulSoup(html_content, "html.parser")

title_spans = soup.find_all('span', class_='highwire-cite-title')

# loop through the <span> tags and print the title text
for span in title_spans:
    title = span.text.strip()
    titles.append(title)

titles = list(set(titles))

ALL_TITLES = ALL_TITLES + titles
for i in range(len(titles)):
    ALL_JOURNALS.append("biorXiv")

## Nature stuff
# currently: no distinction for papers vs commentaries, summaries from nature preview (no abstracts)
#today = datetime.date.today()
titles = []
summary_texts = []
datetime_list = []
journal_flags = []

journals = ["nature", "ng", "nbt", "ncomms", "nataging", "natbiomedeng", "natcancer", "natcardiovascres", "ncb", "ncb", "nm", "nmeth", "nprot", "natrevbioeng", "nrc", "nrcardio", "natrevchem", "nrclinonc", "nrg", "nrm", "nsmb"]


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

       # summaries = soup.find_all("div", class_="c-card__summary")
        # Extract the text from the summaries and store them in a list
       # for summary in summaries:
        #    summary_text = summary.get_text().strip()
         #   summary_texts.append(summary_text)
        
        # find all elements with class="c-meta__item" and data-test="article.type"
        type_elements = soup.find_all('span', {'class': 'c-meta__item', 'data-test': 'article.type'})

        # extract the text content of each element - to later select maybe only papers & reviews
        type_values = [elem.find('span', {'class': 'c-meta__type'}).text.strip() for elem in type_elements]
       
        # find all time elements with datetime attribute
        for time_elem in soup.find_all('time', {'datetime': True}):
            datetime_list.append(time_elem['datetime'])
             
today_titles = [e for e, flag in zip(titles, [elem == str(today) for elem in datetime_list]) if flag]
today_journals = [e for e, flag in zip(journal_flags, [elem == str(today) for elem in datetime_list]) if flag]
# today_summaries = [e for e, flag in zip(summary_texts, [elem == str(today) for elem in datetime_list]) if flag]
today_types = [e for e, flag in zip(type_values, [elem == str(today) for elem in datetime_list]) if flag]
ALL_JOURNALS = ALL_JOURNALS + today_journals
ALL_TITLES = ALL_TITLES + today_titles
# quite a few entries DO NOT HAVE SUMMARIES - so summaries cannot be currently used

"""
# cell journals: already all journals (neuron etc included), already today-only
today = str(today)
today_stripped = today.replace('-', '')
url_cell = "https://www.cell.com/action/doSearch?field1=AllField&Ppub=&Ppub="+today_stripped+"-"+today_stripped+"&SeriesKey=ajhg&SeriesKey=bpj&SeriesKey=bpr&SeriesKey=ccell&SeriesKey=cell&SeriesKey=ccbio&SeriesKey=xgen&SeriesKey=chom&SeriesKey=cmet&SeriesKey=celrep&SeriesKey=xcrm&SeriesKey=crmeth&SeriesKey=crsus&SeriesKey=stem&SeriesKey=cels&SeriesKey=curbio&SeriesKey=devcel&SeriesKey=xhgg&SeriesKey=immuni&SeriesKey=xinn&SeriesKey=isci&SeriesKey=molcel&SeriesKey=ymthe&SeriesKey=omtm&SeriesKey=omtn&SeriesKey=omto&SeriesKey=neuron&SeriesKey=stemcr&SeriesKey=stfode&SeriesKey=tibs&SeriesKey=tibtec&SeriesKey=trecan&SeriesKey=ticb&SeriesKey=tics&SeriesKey=tree&SeriesKey=tem&SeriesKey=tigs&SeriesKey=treimm&SeriesKey=timi&SeriesKey=trmome&SeriesKey=tins&SeriesKey=tips&startPage=0&pageSize=1000"

response = requests.get(url_cell)

if response.status_code == 200:
    html_content = response.content
else:
    print("Error retrieving HTML content:", response.status_code)

html_content = str(html_content)
pattern = r'title="(Select article.*?)"></input>'
titles = re.findall(pattern, html_content)
titles = [title.replace("Select article\\xc2\\xa0", "") for title in titles]
# would be cool to then annotate which journal
ALL_TITLES = ALL_TITLES + titles
for i in range(len(titles)):
    ALL_JOURNALS.append("Cell-journals")
"""

"""
########### NOT WORKING
# science journals: month by month - have to then manually select the day as for nature
today = datetime.date.today() - datetime.timedelta(days=3) #############
today_year = str(today.year)
today_month = str(today.month)
url_science = "https://www.science.org/action/doSearch?field1=AllField+&ConceptID=&publication=&Ppub=&AfterMonth="+today_month+"&AfterYear="+today_year+"&BeforeMonth="+today_month+"&BeforeYear="+today_year+"&adobe_mc=MCMID%3D86460751373585336670386334450110048934%7CMCORGID%3D242B6472541199F70A4C98A6%2540AdobeOrg%7CTS%3D1680966920&startPage=0&pageSize=1000&adobe_mc=MCMID%3D86460751373585336670386334450110048934%7CMCORGID%3D242B6472541199F70A4C98A6%2540AdobeOrg%7CTS%3D1680966949"

response = requests.get(url_science)

#if response.status_code == 200:
html_content = response.text
#else:
 #   print("Error retrieving HTML content:", response.status_code)
""" 
 

# elife: have to check first #pages one by one on pag parameter and check manually the day..
# genomebiology same, nejm same
titles = []
dates = []

for pag in range(1,9):
    url_elife = "https://elifesciences.org/search?for=&sort=date&order=descending&page="+str(pag)

    response = requests.get(url_elife)
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Error retrieving HTML content:", response.status_code)
    
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all the title elements and extract their text
    titles_tempo = [title.text for title in soup.find_all('a', class_='teaser__header_text_link')]
    titles = titles + titles_tempo
    
    dates_temp = []
    for date_elem in soup.find_all('span', {'class': 'date'}):
        date_str = date_elem.find('time')['datetime']
        dates_temp.append(date_str[:10])
    while len(dates_temp) < 10: # brutally overwriting in case of missing dates (10-wise) as there can be podcasts in the main page which have no date recorded...
        dates_temp.append(dates_temp[1])
    dates = dates + dates_temp
        
today_titles = [e for e, flag in zip(titles, [elem == str(today) for elem in dates]) if flag]

ALL_TITLES = ALL_TITLES + today_titles
for i in range(len(today_titles)):
    ALL_JOURNALS.append("eLife")

# genome biology / bmc
from datetime import datetime
titles = []
dates = []
for pag in range(1,25):
    url_genomebio = "https://www.biomedcentral.com/search?searchType=publisherSearch&sort=PubDate&page="+str(pag)+"&query="

    response = requests.get(url_genomebio)
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Error retrieving HTML content:", response.status_code)
        
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all the <h3> tags with the class 'c-listing__title'
    title_tags = soup.find_all('h3', class_='c-listing__title')

    # Extract the text from the <a> tags within the <h3> tags and store it in a list
    titles_tempo = [title_tag.a.text for title_tag in title_tags]
    titles = titles + titles_tempo
    
    # Find the <span> tag with the itemprop attribute set to "datePublished"
    date_tags = soup.find_all('span', itemprop='datePublished')

    for date_tag in date_tags:
        date_text = date_tag.text.strip()
        date_obj = datetime.strptime(date_text, '%d %B %Y')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        dates.append(str(formatted_date))
today_titles = [e for e, flag in zip(titles, [elem == str(today) for elem in dates]) if flag]  

ALL_TITLES = ALL_TITLES + today_titles
for i in range(len(today_titles)):
    ALL_JOURNALS.append("BMC")

"""
# nejm SAME PROBLEM AS SCIENCE: 403 - FORBIDDEN
titles = []
dates = []
for pag in range(1,25):
    url_nejm = "https://www.nejm.org/search?searchType=advancedSearch&sortBy=date+&exactPhrase=&atLeastOneWord=&withoutTheWords=&searchWithin=fullText&articleCategory=&date=past6Months&author=&authorAndOr=AND&startPage="+str(pag)+"&isFiltered=true"

    response = requests.get(url_nejm)
    if response.status_code == 200:
        html_content = response.content
    else:
        print("Error retrieving HTML content:", response.status_code)
        
    soup = BeautifulSoup(html_content, 'html.parser')
"""

# mettere poi dei checks per assicurarsi che il retrieval abbia funzionato da tutti i giornali

#plosbio - NO GUARANTEE OF COMPLETENESS: CURRENTLY RUNNING ON THE RSS FEED AS THE all publications page opens an html with no obvious way to get to titles
##url_plosbio = "https://journals.plos.org/plosbiology/search?resultsPerPage=1000&q=publication_date%3A%5B"+str(today)+"T00%3A00%3A00Z%20TO%20"+str(today)+"T23%3A59%3A59Z%5D&page=1&utm_content=a&utm_campaign=ENG-467"
#url_plosbio = "https://journals.plos.org/plosbiology/feed/atom"
#response = requests.get(url_plosbio)
#if response.status_code == 200:
#    html_content = response.content
#else:
 #   print("Error retrieving HTML content:", response.status_code)
        
# Create a BeautifulSoup object from the XML string
#soup = BeautifulSoup(html_content, 'xml')

# Find all the title tags and extract their text
#titles = [title.text for title in soup.find_all('title')]
#titles = [title for title in titles if title != 'PLOS Biology']
# problem: no dates notion in the RSS feed - will keep old stuff...
#ALL_TITLES = ALL_TITLES + titles
#for i in range(len(titles)):
#    ALL_JOURNALS.append("PLOS-biology")


# arxiv
import datetime
todayplus = today = datetime.date.today() - datetime.timedelta(days=int(num))#- datetime.timedelta(days=2)
today = datetime.date.today() - datetime.timedelta(days=(int(num)+2)) # currently may repeat yesterday's titles...
url_arxiv = "https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-computer_science=y&classification-q_biology=y&classification-statistics=y&classification-include_cross_list=include&date-year=&date-filter_by=date_range&date-from_date="+str(today)+"&date-to_date="+str(todayplus)+"&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first"

response = requests.get(url_arxiv)
if response.status_code == 200:
    html_content = response.content
    # Parse the HTML using Beautiful Soup
    soup = BeautifulSoup(html_content, "html.parser")
    p_tags = soup.find_all('p', {'class': 'title is-5 mathjax'})
    titles = []
    for p in p_tags:
        title = p.text.strip()  # remove leading/trailing whitespace
        titles.append(title)
ALL_TITLES = ALL_TITLES + titles
for i in range(len(titles)):
    ALL_JOURNALS.append("ArXiv")

url_arxiv = "https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-computer_science=y&classification-q_biology=y&classification-statistics=y&classification-include_cross_list=include&date-year=&date-filter_by=date_range&date-from_date="+str(today)+"&date-to_date="+str(todayplus)+"&date-date_type=submitted_date&abstracts=show&size=200&order=-announced_date_first&start=200"

response = requests.get(url_arxiv)
if response.status_code == 200:
    html_content = response.content
    # Parse the HTML using Beautiful Soup
    soup = BeautifulSoup(html_content, "html.parser")
    p_tags = soup.find_all('p', {'class': 'title is-5 mathjax'})
    titles = []
    for p in p_tags:
        title = p.text.strip()  # remove leading/trailing whitespace
        titles.append(title)
ALL_TITLES = ALL_TITLES + titles
for i in range(len(titles)):
    ALL_JOURNALS.append("ArXiv")
       
with open('TodayPapers'+str(todayplus)+'.txt', 'w', encoding='utf-8') as f: 
    for x, y in zip(ALL_TITLES, ALL_JOURNALS):
        f.write(f'{x}${y}\n')

with open('TodayPapers.txt', 'w', encoding='utf-8') as f: 
    for x, y in zip(ALL_TITLES, ALL_JOURNALS):
        f.write(f'{x}${y}\n')

# Email address: paperboat@chatgpt-freetelegrambot.iam.gserviceaccount.com 


