from openai import OpenAI
import fitz 
import re
import pandas as pd
import json

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
    
    def json_to_excel(self, content, doc_path):
        json_answer = content[7:]
        json_answer = json.loads(json_answer[:-3])

        json_answer['Ключевые материалы'] = ['\n'.join(json_answer['Ключевые материалы'])]
        answer_df = pd.DataFrame(data=json_answer)
        
        path = f"{doc_path[:-4]}_additional_parameters.xlsx"
        answer_df.to_excel(path, index=False)
        return path
    
    def get_additional_parameters(self, doc_path):

        system_prompt = 'Тебе необходимо определять ключевые параметры научных статей\n'

        discription_prompt = ('''{        
"required": [ "Тип статьи", "Тип исследования", "Отрасль применения", "Тема статьи",
               "Подтема статьи", "Новизна статьи", "Фокус", "Ключевые материалы"],
  "properties": {
    "Тип статьи": {
      "type": "string",
      "description": "Например: обзор, исследование"
    },
    "Тип исследования": {
      "type": "string",
      "description": "Например: фундаментальное, прикладное"
    },
    "Отрасль применения": {
      "type": "string",
      "description": "это область или сфера деятельности, в которой результаты исследования могут быть применены на практике, если тип исследования прикладное. Например: энеретика, информационные технологии, медицина, образование. Максимум 1-2 слова"
    },
    "Тема статьи": {
      "type": "string",
      "description": "это оснавная идея всего текста, кратко опиши тему – максимум 1-2 слова, например: 'биотопливо"
    },
    "Подтема статьи": {
      "type": "string",
      "description": "кратко опиши подтему – максимум 1-2 слова, например: 'катализаторы'"
    },
    "Цель исследования": {
      "type": "string",
      "description": "результат к которому мы хотим придти по итогу исследования, например: бизнесовые ,ESG, Научные, Маркетинговые, Социологические, Психологические"
    },                             
    "Новизна статьи": {
      "type": "string",
      "description": "в чем суть исследования – сравнение существующих, новый подход или материал и т.д."
    },
    "Фокус": {
      "type": "string",
      "description": "на чем оснофной фокус текста, например 'свойства материалов' или 'процессы' и т.д."
    },
    "Ключевые материалы": {
      "type": "list",
      "description": "Например: палладий, платина, медь, и т.д."
    },
}\n'''
"Выведи ответ в формате json и верни только json")


        messeges = [{'role': 'system', 'content': system_prompt + discription_prompt}]

        messeges.append({'role': 'user', 'content': self.read_pdf(doc_path)})

        response = self.client.chat.completions.create(
            model = self.model,
            messages = messeges
            )
        
        answer = self.json_to_excel(response.choices[0].message.content, doc_path)
        return answer
        