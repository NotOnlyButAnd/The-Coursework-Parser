import os
import requests
import time

# Входная директория с текстами промпотв
g_prompt_text_dir = 'data\\output_llm'
g_yandexgpt_text_dir = 'data\\output_YandexGPT'

# Базовый URL и заголовки для отправки запросов
url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers = {
    "Content-Type": "application/json",
    # TODO: НЕЛЬЗЯ публиковать этот ключ в GIT !!!! (ПОДУМАТЬ как заменить)
    "Authorization": "Api-Key XXXXXXXXXXXXXXXXXXXXXXXXX"
}

start_time = time.time()

# Рекурсивный проход по директории (входной) и обработка каждого из файлов
# цикл по всем директориям в input_dir
for root_dir, _, files in os.walk(g_prompt_text_dir):
    # цикл по всем файлам в текущей директории
    for filename in files:

        cur_file_dir = os.path.join(root_dir, filename)
        print(f'INPUT_DIR: {cur_file_dir}')

        # читаем текущий текст промпта:
        with open(cur_file_dir, 'r', encoding='utf-8') as f:
            prompt_text = ''.join(f.readlines())
            print(f'---Запрос:---\n"{prompt_text}"')

            # Составляем объект промпта для API
            prompt = {
                "modelUri": "gpt://XXXXXXXXXXXXXXX/yandexgpt",
                # TODO: НЕЛЬЗЯ публиковать этот ключ в GIT !!!! (ПОДУМАТЬ как заменить)
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.4
                },
                "messages": [
                    {
                        "role": "user",
                        "text": prompt_text
                    }
                ]
            }

            response = requests.post(url, headers=headers, json=prompt)
            result = response.json()
            print(f'---Ответ:---\n"{result}"')

            with open(f'{g_yandexgpt_text_dir}\\TECH_{filename}', 'w', encoding='utf-8') as f_w:
                f_w.write(str(result))
            with open(f'{g_yandexgpt_text_dir}\\{filename}', 'w', encoding='utf-8') as f_w:
                f_w.write(result['result']['alternatives'][0]['message']['text'])

            print()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"The task took {elapsed_time:.2f} seconds to complete.")
# Пять файлов обрабатывались 50 sec
# 200 - 2000 sec
# => по 10 sec на один запрос