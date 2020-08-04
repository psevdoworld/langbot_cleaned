import requests


class YaDict:
    """this class and this bot was written in short time in april 2020
    please do not judge us, we suffered already"""
    def __init__(self, lang="en-ru"):
        self.URL = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"

        self.PARAMS = {'key': "dict.1.1.20200420T163208Z.a850de2949760f56.c8a1a882e5d1b00e8ab21e4eb84ec99251bc119a",
                       'lang': lang,
                       }

    def _get_trans(self, text):
        try:
            self.PARAMS["text"] = text
            r = requests.get(url=self.URL, params=self.PARAMS)
            data = r.json()
            return data["def"]
        except Exception as e:
            print(e)

    def trans(self, text, pos="any"):
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
