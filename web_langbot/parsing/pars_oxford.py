import requests
import bs4
from YaDictator import YaDict
import json
LOCAL = False


def pars_words(url):
    words_dict = {}
    res = requests.get(url)
    text = res.text
    soup = bs4.BeautifulSoup(text, 'html.parser')
    soup = soup.find(id="wordlistsContentPanel")
    soup = soup.find("ul", {"class": "top-g"})
    elem = soup.find_all("li")
    for word in soup.find_all("li"):
        try:
            name = word.get("data-hw")
            pos = word("span", {"class": "pos"})[0].text
            level = word.find("span", {"class": "belong-to"}).text
            audio = word.find("div", {"class": "sound audio_play_button icon-audio pron-us"}).get("data-src-mp3")
            words_dict[name] = {"pos": pos, "level": level, "audio": audio}
            print(words_dict[name])
        except Exception as e:
            print(e)
            print("######", word)
    return words_dict


def save_audio(words_dict, dir):
    where_broken = 320
    count = where_broken
    while count < len(list(words_dict)):
        for index, word in enumerate(list(words_dict)[where_broken:]):
            if (where_broken + index) % 10 == 0:
                print(where_broken + index)
            file_name = f"{dir}/{word}.mp3"
            url = "https://www.oxfordlearnersdictionaries.com" + words_dict[word]["audio"]
            try:
                res = requests.get(url)
            except Exception as e:
                print(e)
                where_broken += index
                break
            f = open(file_name, 'wb')
            f.write(res.content)
            f.close()
            count += 1

def translate(words_dict):
    for index, word in enumerate(list(words_dict)[:]):
        if index % 10 == 0:
            print(index)
        try:
            word_trans = YaDict().trans(word, words_dict[word]["pos"])
            words_dict[word]["translation"] = word_trans
        except Exception as e:
            print(index, word, e)
    return words_dict

def print_info(words_dict):
    print(words_dict)
    import pprint
    pprint.pprint(words_dict)
    print("Всего слов", len(list(words_dict)))
    _sum = 0
    for level in ("a1", "a2", "b1", "b2", "c1"):
        temp = len(list(filter(lambda x: words_dict[x]["level"] == level, words_dict.keys())))
        _sum += temp
        print(f"{level}: ", temp)
    print(_sum)


def write_to_file(words_dict):

    with open('data.json', 'w', encoding='utf8') as json_file:
        json.dump(words_dict, json_file, ensure_ascii=False)


def main():

    print("parsing...")
    words_dict = pars_words("https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000")

    print("save audio...")
    save_audio(words_dict, "media/oxford_mp3")

    # print("translating...")
    # translate(words_dict)
    write_to_file(words_dict)

    print_info(words_dict)

if __name__ == "__main__":
    main()
