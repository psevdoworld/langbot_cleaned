import requests
import bs4
import json
import pickle



urls = [
    "https://www.englishdom.com/skills/glossary/wordset/emocii-i/",
    "https://www.englishdom.com/skills/glossary/wordset/chasti-tela-i/",
    "https://www.englishdom.com/skills/glossary/wordset/peregovory-i/",
    "https://www.englishdom.com/skills/glossary/wordset/v-gorode-i/",
    "https://www.englishdom.com/skills/glossary/wordset/pogoda-i/",
    "https://www.englishdom.com/skills/glossary/wordset/domashnie-zhivotnye-i/",
    "https://www.englishdom.com/skills/glossary/wordset/v-aeroportu-i/",
    "https://www.englishdom.com/skills/glossary/wordset/produkty-i/",
    "https://www.englishdom.com/skills/glossary/wordset/professii-i/",
    "https://www.englishdom.com/skills/glossary/wordset/menedzhment-i/",

    "https://www.englishdom.com/skills/glossary/wordset/semya-i/",
    "https://www.englishdom.com/skills/glossary/wordset/top100-glagolov/",
    "https://www.englishdom.com/skills/glossary/wordset/anglijskij-dlya-razrabotchikov-ii/",
    "https://www.englishdom.com/skills/glossary/wordset/rugatelstva/",
    "https://www.englishdom.com/skills/glossary/wordset/peregovory-ii/",
    "https://www.englishdom.com/skills/glossary/wordset/samorazvitie/",
    "https://www.englishdom.com/skills/glossary/wordset/startapy-i/",
    "https://www.englishdom.com/skills/glossary/wordset/nauchnye-stepeni-i/",
    "https://www.englishdom.com/skills/glossary/wordset/filmy-i/",
    "https://www.englishdom.com/skills/glossary/wordset/shoping-i/",
    "https://www.englishdom.com/skills/glossary/wordset/fizika-i/"
]
# url = "https://www.englishdom.com/skills/glossary/wordset/top-100-slov-dlya-fce/"
url2 = "https://www.englishdom.com/skills/glossary/wordset/top-100-slov-urovnya-pre-intermediate/"


def get_audio(link):
    audio = False
    while not audio:
        try:
            res = requests.get(link)
            if res.status_code != 200:
                raise Exception("Аудио не получено")
            else:
                audio = res.content
        except Exception as e:
            print(e)
    return audio


def get_topic(url):
    topic_dict = {}
    text = False
    while not text:
        try:
            res = requests.get("https://www.englishdom.com" + url)
            if res.status_code != 200:
                raise Exception("Топик не получен")
            else:
                text = res.text
        except Exception as e:
            print(e)
    soup = bs4.BeautifulSoup(text)
    topic_name = soup.find_all('li', {"class": "item-breadcrumbs is-active"})[0].text
    topic_dict[topic_name] = {}
    all_words = soup.find_all('div', {"class": "item-list is-show js-word js-hover"})
    print(len(all_words))
    print(topic_name)
    # all_words = []
    for word_soup in all_words:
        audio_link = word_soup.find('a').get("href")
        word = word_soup.find('p', {"class": "word"}).text
        tr = word_soup.find('p', {"class": "translate"}).text
        print(word, tr, audio_link)
        audio = get_audio(audio_link)
        topic_dict[topic_name][word] = {'tr': tr, 'audio': audio}
    return topic_dict


def write_to_file(words_dict):
    with open('edom_all_topic.json', 'wb') as json_file:
        pickle.dump(words_dict, json_file, protocol=pickle.HIGHEST_PROTOCOL)


topics_dict = {}


def get_urls():
    urls_list = []
    for page in range(1, 38):
        res = requests.get(f"https://www.englishdom.com/skills/glossary/?page={page}")
        soup = bs4.BeautifulSoup(res.text)
        links = soup.find_all("a", {
            "class": "b-set b-second-bg js-filter-list-item tutorial_glossary_system-set phn__glossary__wordset__item-link"})
        for link in links:
            urls_list.append(link.get("href"))
        print(page)
    return set(urls_list) - set(urls)


for number, url in enumerate(get_urls()):
    print("number_topic", number)
    topics_dict.update(get_topic(url))
    write_to_file(topics_dict)
    print(("@"*40 + "\n")*4)
import pprint

# pprint.pprint(topics_dict)


with open('parsing/edom_all_topic.json', 'rb') as handle:
    topics_dict = pickle.load(handle)
#
# pprint.pprint(topics_dict)
#
# for topic in topics_dict:
#     for word in list(topics_dict[topic]):
#         file_name = f"test/{word}.mp3"
#         f = open(file_name, 'wb')
#         f.write(topics_dict[topic][word]["audio"])
#         f.close()

"""

with open('parsing/edom_all_topic.json', 'rb') as handle:  
    twords = pickle.load(handle) 

db_topic = [topic.name for topic in Topics.objects.all()] 

for topic in db_topic: 
    print(twords.pop(topic, None)) 

for topic in list(topics_dict)[:]: 
    topic_obj, created = Topics.objects.get_or_create(name=topic) 
     for word in list(topics_dict[topic])[:]: 
         print(word,  topics_dict[topic][word]["tr"]) 
             new_tr = topics_dict[topic][word]["tr"] 
             audio = topics_dict[topic][word]["audio"] 
             word_obj, created = Translation.objects.get_or_create(word=word) 
             if not created: 
                 if word_obj.translation.get('tr', False): 
                     if new_tr in word_obj.translation["tr"]: 
                         word_obj.translation["tr"].remove(new_tr) 
                     word_obj.translation["tr"].insert(0, new_tr) 
                 else: 
                    word_obj.translation["tr"] = [new_tr] 
                 if not word_obj.audio: 
                     file = ContentFile(audio) 
                     file.name = f"mp3/new/{word}.mp3" 
                     check_file("media/audio/mp3/new/" + word + ".mp3")  
                     word_obj.audio = file 
             else: 
                  word_obj.translation["tr"] = [new_tr] 
                  file = ContentFile(audio)  
                  check_file("media/audio/mp3/new/" + word + ".mp3") 
                  file.name = f"mp3/new/{word}.mp3"  
                  word_obj.audio = file 
             word_obj.topics.add(topic_obj) 
             word_obj.save() 
"""
"""
from django.core.files.base import ContentFile 

with open('parsing/all_words_not_db_new2.json', 'rb') as handle: 
    words = pickle.load(handle) 
    
for word in list(words): 
    if words[word].get("translation") == None: 
        words.pop(word) 
        print(word) 


for word in list(words): 
    if words[word].get("translation") == {"tr":""}: 
        words.pop(word) 
        print(word) 

for index, word in enumerate(list(words)[:2]): 
    word_obj, created = Translation.objects.get_or_create(word=word) 
    word_obj.pos = words[word].get("pos") 
    word_obj.oxford_level = words[word].get("level") 
    word_obj.translation = words[word].get("translation") 
    file = ContentFile(words[word].get("audio_bin")) 
    file.name = f"mp3/{word}.mp3"    
    word_obj.audio = file  
    word_obj.save() 
    print(index) 

"""
for index, word in enumerate(list(words)[:2]):
    word_obj, created = Translation.objects.get_or_create(word=word)
    word_obj.pos = words[word].get("pos")
    word_obj.oxford_level = words[word].get("level")
    word_obj.translation = words[word].get("translation")
    file = ContentFile(words[word].get("audio_bin"))
    file.name = f"mp3/{word}.mp3"
    word_obj.audio = file
    word_obj.save()
    print(index)
