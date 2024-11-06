from openai import OpenAI
import fitz 
import re
import pandas as pd
import json
import logging 
from bot.texts import *

import config 

api_logger = logging.getLogger('api_logger')
handler = logging.StreamHandler()
format_log = logging.Formatter("%(levelname)s:%(name)s - %(message)s")
handler.setFormatter(format_log)
api_logger.addHandler(handler)
api_logger.setLevel(logging.INFO)

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
        api_logger.info("Чтение файла")
        document = fitz.open(doc_path)

        atricle_prompt = chr(12).join([page.get_text() for page in document.pages(0, self.count_pages)])
        return atricle_prompt
    
    def json_to_df(self, content):
        api_logger.info("Преобразование файла в df 1")
        print(content)
        json_answer = content[7:]
        api_logger.info("Преобразование файла в df 2")
        json_answer = json.loads(json_answer[:-3])
        api_logger.info("Преобразование файла в df 3")
        for column_name in json_answer:
          if isinstance(json_answer[column_name], list):
             json_answer[column_name] = ['\n'.join(json_answer[column_name])]    
        api_logger.info("Преобразование файла в df 5")
        answer_df = pd.DataFrame(data=json_answer, index=[0])
        api_logger.info("Преобразование файла в df 6")
        print(answer_df)
        return answer_df
    
    def get_additional_parameters(self, document_text, discription_prompt):
        api_logger.info("Работа с api") 

        system_prompt = 'Тебе необходимо определять ключевые параметры научных статей\n'

        messeges = [{'role': 'system', 'content': system_prompt + discription_prompt}]

        messeges.append({'role': 'user', 'content': document_text})

        response = self.client.chat.completions.create(
            model = self.model,
            messages = messeges
            )
        
        answer_df = self.json_to_excel(response.choices[0].message.content)
        return answer_df
    
    def get_answer(self, doc_path):
      api_logger.info("Начало работы с api") 
      document_text = self.read_pdf(doc_path)

      api_logger.info("Обработка первой части параметров") 
      answer_concat = pd.DataFrame()

      for num_of_discription_prompt, discription_prompt in enumerate(discription_prompt_name):
        api_logger.info(f"Обработка промпта {num_of_discription_prompt}")
        answer_df = self.json_to_df(document_text, discription_prompt)
        try: 
          api_logger.info("Склейка в единую таблицу") 
          answer_concat = pd.concat([answer_concat, answer_df], axis=1)
        except:
          api_logger.info("Concat error")

      api_logger.info("Преобразование файла в xlsx")
      path = f"{doc_path[:-4]}_additional_parameters.xlsx"
      api_logger.info("Файл отправлен в дерево")
      answer_concat.to_excel(path, index=False)
      return path

