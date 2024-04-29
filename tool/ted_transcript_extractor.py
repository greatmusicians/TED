# coding=utf-8

import sys
import re
import html
import json
import requests
import datetime

"""
https://www.ted.com/talks/mustafa_suleyman_what_is_an_ai_anyway
"""


class TED:
    def __init__(self, url: str) -> None:
        self.url = url
        self.title = ""
        self.subtitle_filename = ""
        self.content = ""

    def init_subtitle(self):
        response = requests.get(self.url)
        response.raise_for_status()
        m = re.search("<title>(.*)</title>", response.text)
        if m != None:
            self.title = m.group(1)
            self.title = re.sub("\s*\|.*", "", self.title).strip()
        m = re.search(
            'content="https://www.ted.com/talks/(\w+)"',
            response.text,
        )
        if m != None:
            self.subtitle_filename = m.group(1)
        self.content = response.text

    def extract_transcript(self):
        json_text = self.content.split('"paragraphs":[')[1]
        json_text = json_text.split('}]}]},"video":')[0]
        json_text = '{"paragraphs":[' + json_text + "}]}]}"
        json_obj = json.loads(json_text)
        paragraph_list: list[str] = []
        for paragraph in json_obj["paragraphs"]:
            p_text = ""
            for cue in paragraph["cues"]:
                text = re.sub("\s+", " ", cue["text"])
                p_text += text + " "
            paragraph_list.append(p_text)
        self.content = "\n\n".join(paragraph_list)

    def extract_transcript_2(self):
        content_list = self.content.split('"transcript":"')
        if len(content_list) > 1:
            self.content = content_list[1]
            self.content = self.content.split('","embedUrl"')[0]
            self.content = html.unescape(self.content)

    def save_content(self):
        filename = f"{self.get_time_str()}.txt"
        with open(filename, "w") as f:
            f.write(self.content)
        print(f"save to: {filename}")

    def get_time_str(self):
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


if __name__ == "__main__":
    talk_url = sys.argv[-1]

    ted = TED(talk_url)
    ted.init_subtitle()
    ted.extract_transcript()
    ted.save_content()
