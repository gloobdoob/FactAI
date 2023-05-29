import os
import openai
import time
import math
from retry import retry
import re
import config


openai.organization = config.organization
openai.api_key = config.api_key
openai.Model.list()

import string

def remove_non_printable(s):
    return ''.join(c for c in s if c not in string.printable)
# Retry decorator with exponential backoff


class TextCorrectorV2:
    def gpt_summarize(self, text, max_tokens):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"{text}\n\nTl;dr",
            temperature=0.1,
            max_tokens=max_tokens,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=1
        )
        return response


    def gpt_correct(self, text):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt= f"clean and correct the text and write it all in one line, remove any unnecessary characters\n\n{text}",
            temperature=0,
            max_tokens=90,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response

    #
    # def correct_tl(self, text):
    #     response = openai.Completion.create(
    #         model="text-davinci-003",
    #         prompt= f"clean the tagalog text and remove unnecessary characters or words as the text was extracted from an image using an Optical Character Recognition software, put it all in one line\n\n{text}",
    #         temperature=0,
    #         max_tokens=90,
    #         top_p=1.0,
    #         frequency_penalty=0.0,
    #         presence_penalty=0.0
    #     )
    #     return response

    @retry((openai.error.APIConnectionError, openai.error.Timeout, openai.error.APIError, openai.error.RateLimitError), delay=4, tries=6)
    def correct(self, text):
        print('correcting text')
        text = self.gpt_correct(text)
        
        return text['choices'][0]['text'].strip()


    @retry((openai.error.APIConnectionError, openai.error.Timeout, openai.error.APIError, openai.error.RateLimitError), delay=4, tries=6)
    def summarize(self, text, max_tokens=50):
        print('summarizing text')
        text = self.gpt_summarize(text, max_tokens)
        return text['choices'][0]['text'].strip()

