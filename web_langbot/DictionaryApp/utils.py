import requests
from googletrans import Translator
from gtts import gTTS


def text_to_speech(word, language="en"):
    speech = gTTS(text=word, lang=language, slow=False)
    speech.save(f"{word}.mp3")


class YaDict:
    def __init__(self, lang="en-ru"):
        self.URL = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"

        self.PARAMS = {'key': "dict.1.1.20200420T163208Z.a850de2949760f56.c8a1a882e5d1b00e8ab21e4eb84ec99251bc119a",
                       }

    def _get_trans(self, text):
        try:
            self.PARAMS["text"] = text
            r = requests.get(url=self.URL, params=self.PARAMS)
            data = r.json()
            return data["def"]
        except Exception as e:
            print(e)

    def trans(self, text, pos="any", lang="en_ru"):
        self.PARAMS["lang"] = lang
        tr = self._get_trans(text)
        if tr is not None:
            for i in tr:
                if pos == "any" or i.get("pos") in pos:
                    tr_dict = {j.get("text"): j.get("ex") if "ex" in j else None for j in i.get("tr")}
                    syn_dict = {j.get("text"): [k.get("text") for k in j.get("syn")] if "ex" in j else None for j in i.get("tr") if
                                "syn" in j}
                    return {"ts": i.get("ts"),
                            "tr": [j.get("text") for j in i.get("tr")],
                            "ex": tr_dict,
                            "syn": syn_dict}


class GooTrans:
    """this class and this bot was written in short time in may 2020
    please do not judge us, we suffered already"""
    def __init__(self):
        self.translator = Translator()

    def trans(self, text, dest='ru'):
        if dest == 'ru':
            try:
                a = self.translator.translate(text, dest=dest)

                w = a.text
                a = a.extra_data["all-translations"][0][1][:5]
                if a[0] != w:
                    a = [w, ]+[i for i in a if i != w]
                return {'tr': a}
            except Exception as e:
                print("failed to translate in trans")
                print(e)
        elif dest == 'en':
            try:
                a = self.translator.translate(text, dest=dest)
                text = a.text
                a = self.translator.translate(text, dest='ru')
                w = a.text
                a = a.extra_data["all-translations"][0][1][:5]
                if a[0] != w:
                    a = [w, ] + [i for i in a if i != w]
                return text, {'tr': a}
            except Exception as e:
                print("failed to translate ru to en in trans")
                print(e)
