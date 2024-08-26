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
        print(atricle_prompt)
        return atricle_prompt
    
    def json_to_excel(self, content, doc_path):
        print(content)
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
               "Подтема статьи", "Цель исследования", "Новизна статьи", "Фокус", "Ключевые материалы"],
  "properties": {
    "Тип статьи": {
      "type": "string",
      "description": "Например: обзор, исследование"
    },
    "Тип исследования": {
      "type": "string",
      "description": "Например: фундаментальное - это вид научных исследований с целью совершенствования научных теорий для лучшего понимания и прогнозирования природных или других явлений.
                              , прикладное - используют научные теории для разработки технологий или методик, которые могут быть использованы для вмешательства и изменения природных или других явлений"
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
      "description": "результат к которому мы хотим придти по итогу исследования, например: бизнесовые ,environmental social governance(ESG), Маркетинговые, Социологические, Психологические"
    },                             
    "Новизна статьи": {
      "type": "string",
      "description": "в чем суть исследования, например: сравнение существующих, новый подход или материал и т.д."
    },
    "Фокус": {
      "type": "string",
      "description": "на чем оснофной фокус текста, например: 'свойства материалов', 'процессы' и т.д."
    },
    "Ключевые материалы": {
      "type": "list",
      "description": "Например: палладий, платина, медь, и т.д."
    },
}\n'''
"Выведи ответ в формате json и верни только json\n"
'''Пример: 
  A tannin-based adsorbent was synthesized by pomegranate peel tannin powder modified with
ethylenediamine (PT-ED) for the rapid and selective recovery of palladium and gold. To char-
acterize PT-ED, field emission scanning electron microscopy (FE-SEM), energy-dispersive X-ray
spectroscopy (EDS-Mapping), and Fourier transform infrared spectroscopy (FT-IR) were used.
Central composite design (CCD) was used for optimization. The kinetic, isotherm, interference of
coexisting metal ions, and thermodynamics were studied. The optimal conditions, including Au
(III) concentration  30 mg L 1, Pd (II) concentration  30 mg L 1, adsorbent mass  26 mg, pH
 2, and time  26 min with the sorption percent more than 99 %, were anticipated for both
metals using CCD. Freundlich model and pseudo-second-order expressed the isotherm and kinetic
adsorption of the both metals. The inhomogeneity of the adsorbent surface and the multi-layer
adsorption of gold and palladium ions on the PT-ED surface are depicted by the Freundlich
model. The thermodynamic investigation showed that Pd2 and Au3 ions adsorption via PT-ED
was an endothermic, spontaneous, and feasible process. The maximum adsorption capacity of
Pd2 and Au3 ions on PT-ED was 261.189 mg g 1 and 220.277 mg g 1, respectively. The prob-
able adsorption mechanism of Pd2 and Au3 ions can be ion exchange and chelation. PT-ED (26
mg) recovered gold and palladium rapidly from the co-existing metals in the printed circuit board
(PCB) scrap, including Ca, Zn, Si, Cr, Pb, Ni, Cu, Ba, W, Co, Mn, and Mg with supreme selectivity
toward gold and palladium. The results of this work suggest the use of PT-ED with high selectivity
and efficiency to recover palladium and gold from secondary sources such as PCB scrap.
  вот такой json для этого примера
 {
  "Тип статьи": "исследование",
  "Тип исследования": "прикладное",
  "Отрасль применения": "энергетика",
  "Тема статьи": "биотопливо",
  "Подтема статьи": "катализаторы",
  "Цель исследования": "environmental social governance(ESG)",
  "Новизна статьи": "новый подход",
  "Фокус": "свойства материалов",
  "Ключевые материалы": ["палладий", "золото"]
}''')


        messeges = [{'role': 'system', 'content': system_prompt + discription_prompt}]

        messeges.append({'role': 'user', 'content': self.read_pdf(doc_path)})

        response = self.client.chat.completions.create(
            model = self.model,
            messages = messeges
            )
        
        answer = self.json_to_excel(response.choices[0].message.content, doc_path)
        return answer
        


