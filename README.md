# Paper Boat

Hey there! Are you an academic? Then probably you want to stay updated about all the papers and preprints published out there on a daily basis, but the information is so disperse, plus, it’s complicated to download papers. If you feel like that, then you are in the right place! 
Paper Boat is a Telegram bot that delivers you the titles of all preprints and papers published today in all major journals, and helps you download them by DOI or title (from biorXiv, arXiv, or SciHub, the latter taking a little bit after a paper is published).

If you are at EPFL, you will soon be able to play with Paper Boat on Telegram: https://t.me/paperboatbot Start exploring & share me with friends!
Currently I've shut it down but a beta version will hopefully be available in the summer.

The Paper Boat engine currently runs every morning at 6 AM CET to retrieve papers and preprints published the previous day. The Telegram bot is active 24/7 to download papers for you (occasionally it sends you very random papers if you make typos in the titles) and to send you the list of papers published the day before. The Paper Boat Podcast engine currently runs every Sunday to send you a digest of the previous week papers in Nature and Cell Journals (as a test), in podcast form.

Paper Boat is currently available only for people at EPFL in Lausanne, but you can download the code and start a new Telegram Bot and, with minor edits, test it on your server – I suggest using ngrok. I will consider making Paper Boat available outside of EPFL if people here think it’s useful. Paper Boat is currently biology-centric, but future releases aim at making it more general, starting from computer science journals as a second milestone.

I’m working on Paper Boat as a side project once in a while, and I am more than happy to welcome potential collaborators. You can write me at luca.fusarbassini@epfl.ch. Yet-to-comment-well code: https://github.com/lucafusarbassini/paperboat

Currently the bot scrapes biorXiv, arXiv, the Nature journals, the Cell journals (some days has issues with Cell), eLife, Genome Biology. Probably I should also explore the journals’ APIs, of which I haven’t studied anything yet.

A note of caution: the CrossRef API is huge but from what I understand things can go wrong – for example, if you want to download Attention Is All You Need by title, you’ll get a 1993 Structural Survey paper (lol). Also, currently the bot gets slow if there are several users simultaneously active, and sometimes sends duplicates of papers.
I am deeply thankful to the developers of the SciHub, Zotero, CrossRef, Google Cloud Voice, and OpenAI APIs.

These are the features currently implemented in Paper Boat:
/today delivers you a list of papers published in the last 24h (actually, before 6am CET) in major biology journals, biorXiv, and arXiv, divided by publisher. More journals will be added soon.
/doi downloads a paper by DOI from SciHub
/biorxiv downloads a paper by DOI from biorXiv
/arxiv downloads a paper by DOI from arXiv
/download attempts to download a paper by its title using CrossRef to find the DOI
/downloadtoday downloads today’s biorXiv papers by number (eg, /downloadtoday 27 will download the 27th biorXiv paper in the list)
/digest delivers you an AI-generated summary of last week research in the journals currently scraped
/podcast delivers you the digest in podcast form (with a pretty good AI-generated voice)
/info delivers you all the info you need to get started
/github sends you the GitHub link to this project, where you can find detailed info


Here are a few high-priority features I’d love to implement [0 solving scraping problems with Science and NEJM]:
1.	Reduce information overload by sub-selecting papers for topic and relevance
a.	A user-centric paper ranking
b.	Topic detection
Idea: use BERT + build dataset with "all" published literature with zotero to be used for fine-tuning
c.	LLMs to detect innovative research vs most less-innovative papers
2.	[implemented but $$] ChatGPT-based 3-phrases summaries for (at least) top daily papers 
3.	[implemented but $$] Explain abstracts in simple terms (ChatGPT-based)
4.	Function to return authors' names from paper's title or DOI
5.	Differentiate papers vs reviews, commentaries, etc
6.	User-centric message scheduler (eg, receive Nature Biotech updates on a weekly basis on Friday)
7.	Deliver DOI links to papers published today (not yet listed on CrossRef)
8.	Save relevant papers and preprints to collection / Zotero
Zotero is currently integrated but with my own API key, and is able to put DOI and title only (no metadata creation like adding from web)
9.	Performance (eg, conversion titles and DOIs is slow) + CrossRef API usage results in mistakes
10.	Add the possibility to ask for imprecise titles and retrieve 2-3 closest approximation paper pdfs

As website-scraping is a journal-specific task to implement (okay, ChatGPT helps a lot but still), there are infinite journals for which we still need a scraper. I’d love if you could help by writing some scrapers.
Starting from biology, medicine, and computer science, for example, we need scrapers for:
https://www.medrxiv.org/
https://academic.oup.com/nar
https://nips.cc/
https://www.sciencedirect.com/journal/computational-statistics-and-data-analysis
https://onlinelibrary.wiley.com/journal/10970258
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=69
https://www.tandfonline.com/toc/uasa20/current
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=5962385
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=34
https://nips.cc/
https://www.jmlr.org/
https://ascopubs.org/journal/jco/
https://www.thelancet.com/
https://genesdev.cshlp.org/
https://genome.cshlp.org/
https://ieeexplore.ieee.org/xpl/conhome/1000147/all-proceedings
https://jamanetwork.com/
https://iclr.cc/
https://www.pnas.org/
https://eccv2022.ecva.net/
https://journals.plos.org/plosone/
https://rnajournal.cshlp.org/
https://www.embopress.org/journal/14602075
https://imstat.org/journals-and-publications/annals-of-statistics/
https://academic.oup.com/jrsssb
https://www.annualreviews.org/journal/statistics
https://imstat.org/journals-and-publications/annals-of-probability/
https://academic.oup.com/biostatistics
https://academic.oup.com/biomet
https://www.jmlr.org/
https://projecteuclid.org/journals/bayesian-analysis
https://www.tandfonline.com/journals/hmbr20
https://www.sciencedirect.com/journal/neurocomputing
https://www.nowpublishers.com/MAL
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=34
https://www.springer.com/journal/11263
https://www.nature.com/natmachintell/
https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=5962385
https://www.sciencedirect.com/journal/pattern-recognition
https://www.sciencedirect.com/journal/neural-networks

And many more! Then there come Mathematics, Physics, Engineering… the only limit is imagination. I envision this as a collaborative endeavor and some friends have suggested organizing a Paper Boat Hackathon for this reason: let’s see how it goes, maybe we could do that!

There are also some more advanced features one might think to implement, but currently I’d rather keep this simple. Examples:
1.	A text-to-voice AI narrator to make a podcast out of the daily papers you can easily listen at breakfast, walking or while coding - more like a story
2.	Connections with LinkedIn/Twitter, and social media (eg papers from your niche and contacts)
3.	Paper Boat wrap - weekly / yearly... for specific subsets: overall view of the field
4.	Make it a website too (some people don’t have Telegram)
5.	A recommendation engine / advanced ranking based on users history of downloads
6.	A function to connect people who liked/saved the same papers
7.	Integrate with Humata AI
8.	Weekly relevance assessment based on overall user downloads, likes, forwarded etc – some sort of "decentralized peer review" or trend detection
9.	Translation to users’ preferred language
10.	[…]

