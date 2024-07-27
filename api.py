from openai import OpenAI
import fitz 
import re

import config 

kwargs = {
    'ai_model': 'gpt4o',
    'temperature': 0.2,
    'max_tokens': 200,
    'top_p': 0.0,
    'frequency_penalty': 0.0,
    'presence_penalty': -0.5
}

class ParamsApi:
    def __init__(self, count_pages: int=2, api_key=config.api_key, model='gpt-4o'):
        self.count_pages = count_pages
        self.api_key = api_key
        self.model = model

        self.client = OpenAI(api_key=self.api_key)
        self.kwargs = {
                        'temperature': 0.2,
                        'max_tokens': 200,
                        'top_p': 0.0,
                        'frequency_penalty': 0.0,
                        'presence_penalty': -0.5
                    }
        
    def read_pdf(self, doc_path):
        document = fitz.open(doc_path)

        atricle_prompt = chr(12).join([page.get_text() for page in document.pages(0, self.count_pages)])

        return atricle_prompt
    
    def get_additional_parameters(self, doc_path):
        # сделать через tools(отдично подойдет найти параметы(если не выйдет посоветоваться с Колей))

        system_prompt = 'Тебе необходимо определять ключевые параметры научных статей\n'

        discription_prompt = ('''Тип статьи, например обзор, исследование.
Тип исследования, например фундаментальное, прикладное.
Отрасль применения - это конкретная область науки, которая изучает определенные принципы и явления, если тип исследования прикладное.
Тема статьи - это оснавная идея всего текста, кратко опиши тему – максимум 3-4 слова, например "биотопливо".
Подтема статьи, кратко опиши подтему – максимум 3-4 слова.
Цель исследования - это то, к чему стремится соискатель в своих научных исследованиях, то есть конечный результат работы, например бизнес, ESG.
Новизна статьи, в чем суть исследования – сравнение существующих, новый подход или материал и т.д.)
Фокус, на чем оснофной фокус текста, например "свойства материалов" или "процессы" и т.д.
Ключевые материалы, например  палладий, платина, медь, и т.д.
Выведи ответ в формате json''')

        messeges = [{'role': 'system', 'content': system_prompt + discription_prompt}]

        messeges.append({'role': 'user', 'content': self.read_pdf(doc_path)})

        response = self.client.chat.completions.create(
            model = self.model,
            messages = messeges
            )

        # path = f"files/{self.doc_path[:-4]}_additional_parameters.text"
        answer = response.choices[0].message.content[9:]
        answer = answer[:-5]
        return answer
        