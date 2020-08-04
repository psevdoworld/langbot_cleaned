import pickle

import requests
import bs4
from parsing.pars_oxford import pars_words
main_page = requests.get("https://www.oxfordlearnersdictionaries.com/topic/")
main_soup = bs4.BeautifulSoup(main_page.text)

topics = main_soup.find_all("div", {"class": "topic-box"})
topic_link = [i.find("a").get("href") for i in topics]

print(topic_link)
all_topics_links = []
bad_link = []
for category in topic_link:
    try:
        res = requests.get(category)
        soup = bs4.BeautifulSoup(res.text)
        links = soup.find_all("a", {"class": "topic-box-secondary-heading"})
        links = [i.get("href") for i in links]
        print(links)
        all_topics_links += links
    except Exception as e:
        print(e)
        bad_link += [category]
print(all_topics_links)
print(len(all_topics_links))

all_words = dict()
for topic in all_topics_links:
    all_words.update(pars_words(topic))


def write_to_file(words_dict):
    with open('oxford_all.json', 'wb') as json_file:
        pickle.dump(all_words, json_file, protocol=pickle.HIGHEST_PROTOCOL)


write_to_file(all_words)

