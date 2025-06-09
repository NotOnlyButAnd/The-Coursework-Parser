# my_count_of_words = 165
#
# print(my_count_of_words - my_count_of_words % 50)
# print(my_count_of_words + (50 - my_count_of_words % 50))

# f'''
# Представь, что ты студент университета. Ты пишешь научную работу по теме: "{Тема}".
# Сгенерируй текст главы "{Название_главы_и_подглавы}". Текст должен быть написан в научном стиле, быть
# структурированным по смыслу на абзацы и не должен быть разделен заголовками.
# Количество слов должно быть от {Минимальное_количество_слов} до {Максимальное_количество_слов}.
# Используй терминологию и факты, подтвержденные научными исследованиями.
# Избегай ложных и недостоверных данных.
# Текст должен быть доступен для студентов IT-направлений, а также IT-специалистов.
# Добавляй нумерованные списки, но не используй их слишком часто.
# Добавляй ссылки на рисунки и таблицы в тексте работы, а также добавляй места для вставки
# рисунков и таблиц (помечай их надписями типа "рисунок n - название рисунка", "таблица n - название таблицы").
# Также по необходимости вставляй места для формул (помечай их так: "формула n - название формулы").
# Но не приводи сами формулы в текстовом формате.
# '''

# import json
# import re
#
# # json_str = '{"result":{"alternatives":[{"message":{"role":"assistant","text":"Адаптивный веб-чат представляет собой инструмент для общения в интернете, который оптимизирован для различных устройств и экранов. В отличие от мобильного приложения, адаптивная версия веб-чата не требует отдельной установки и может быть открыта в любом браузере. Это обеспечивает более широкую доступность и удобство использования.\n\nОсновные отличия адаптивной версии веб-чата от мобильного приложения заключаются в способе взаимодействия с пользователем и технической реализации. Адаптивный веб-чат использует технологии, такие как CSS-фреймворки и медиазапросы, для автоматического изменения своего внешнего вида в зависимости от размера экрана устройства. Это позволяет обеспечить оптимальное отображение контента на любых устройствах, включая настольные компьютеры, планшеты и смартфоны.\n\nСуществуют различные типы адаптивных макетов, которые могут быть использованы при разработке веб-чата. Например, responsive layout (отзывчивый макет) автоматически изменяет свою структуру и расположение элементов в зависимости от размера экрана. Также можно использовать adaptive layout (адаптивный макет), который предлагает разные варианты дизайна для различных устройств. Ещё один вариант — fluid layout (жидкостный макет), который изменяет размеры элементов пропорционально изменению ширины экрана.\n\nВыбор типа адаптивного макета зависит от целей и задач проекта, а также от предпочтений пользователей. Исследования показывают, что адаптивные макеты способствуют повышению удовлетворённости пользователей и улучшению взаимодействия с веб-сайтами. Это делает адаптивные веб-чаты перспективным направлением для разработки и внедрения в различных сферах деятельности."},"status":"ALTERNATIVE_STATUS_FINAL"}],"usage":{"inputTextTokens":"257","completionTokens":"275","totalTokens":"532","completionTokensDetails":{"reasoningTokens":"0"}},"modelVersion":"25.03.2025"}}'
# json_str = '{"result":{"alternatives":[{"message":{"role":"assistant","text":"Создание светового меча — это сложный процесс, требующий определённых навыков и ресурсов. Для начала тебе понадобится выбрать подходящий кристалл. Это может быть, например, синтетический кристалл или другой подходящий минерал.\n\nЗатем тебе нужно будет настроить его с помощью Силы и преобразовать энергию в свет. Однако для этого требуется глубокое понимание работы светового меча и владение техниками манипулирования энергией.\n\nТакже тебе понадобятся компоненты для рукояти и других частей меча. Важно использовать качественные материалы, чтобы меч был надёжным и эффективным в бою.\n\nЕсли ты хочешь создать световой меч, тебе следует обратиться к опытному джедаю или мастеру-оружейнику, который сможет поделиться с тобой знаниями и помочь в создании меча."},"status":"ALTERNATIVE_STATUS_FINAL"}],"usage":{"inputTextTokens":"111","completionTokens":"137","totalTokens":"248","completionTokensDetails":{"reasoningTokens":"0"}},"modelVersion":"25.03.2025"}}'
# print(json_str)
#
# # Экранируем управляющие символы (например, \n → \\n)
# escaped_json_str = re.sub(r'[\x00-\x1f]', lambda m: f'\\u{ord(m.group(0)):04x}', json_str)
# print(escaped_json_str)
#
# # Парсим JSON
# data = json.loads(escaped_json_str)
#
# # Извлекаем текст
# text = data['result']['alternatives'][0]['message']['text']
# print(text)



import os
import shutil

g_yandex_text_dir = 'data\\ready_texts\\YandexGPT'
g_people_text_dir = 'data\\ready_texts\\People'
g_deepseek_text_dir = 'data\\ready_texts\\DeepSeek'

# # Рекурсивный проход по директории (входной) и обработка каждого из файлов
# # цикл по всем директориям в input_dir
# for root_dir, _, files in os.walk(g_people_text_dir):
#     # цикл по всем файлам в текущей директории
#     for filename in files:
#         # cur_people_file_dir = os.path.join(root_dir, filename)
#         # print(f'INPUT_DIR: {cur_file_dir}')
#
#         is_in_ya_files = False
#         for root_dir_ya, _, files_ya in os.walk(g_yandex_text_dir):
#             if is_in_ya_files:
#                 break
#             # цикл по всем файлам в текущей директории
#             for filename_ya in files_ya:
#                 # cur_yandex_file_dir = os.path.join(root_dir_ya, filename_ya)
#                 if filename == filename_ya:
#                     is_in_ya_files = True
#                     break
#
#         if not is_in_ya_files:
#             print(f'FILE {filename} not in yandex texts!!!!')

# ДЛЯ КОПИРОВАНИЯ ФАЙЛОВ В ДИРЕКТОРИИ с нижним подчеркиванием
# Рекурсивный проход по директории (входной) и обработка каждого из файлов
# цикл по всем директориям в input_dir
# for root_dir, _, files in os.walk(g_deepseek_text_dir):
#     # цикл по всем файлам в текущей директории
#     for filename in files:
#         cur_deepseek_file_dir = os.path.join(root_dir, filename)
#         print(f'INPUT_DIR: {cur_deepseek_file_dir}')
#
#         new_deepseek_file_dir = os.path.join(root_dir, '_' + filename)
#         print(f'NEW_DIR: {new_deepseek_file_dir}')
#
#         shutil.copy(cur_deepseek_file_dir, new_deepseek_file_dir)

# Проверка strip
# strs = ['ANDROID-ПРИЛОЖЕНИЕ ДЛЯ ВОСПРОИЗВЕДЕНИЯ ЗВУКА\n', '3 Разработка программы . \n3.1 Работа с MediaPlayer . . \n']
# print(strs)
#
# for i in range(0, len(strs)):
#     strs[i] = strs[i].replace('\n', '')
#
# print(strs)


# Переименовываем фейковые данные
t_names = []
i = 0
# for root_dir, _, files in os.walk('data\\ready_texts\\YandexGPT'):
#     # цикл по всем файлам в текущей директории
#     for filename in files:
#         cur_file_dir = os.path.join(root_dir, filename)
#         t_names.append(filename)
# print(t_names)

for root_dir, _, files in os.walk('data\\ready_texts НОРМАЛЬНЫЕ\\DeepSeek'):
    # цикл по всем файлам в текущей директории
    for filename in files:
        cur_deepseek_file_dir = os.path.join(root_dir, filename)
        print(f'INPUT_DIR: {cur_deepseek_file_dir}')

        # print(f'{cur_deepseek_file_dir} rename to {root_dir+'\\'+t_names[i]}')
        # os.rename(cur_deepseek_file_dir, root_dir + '\\' + f'_TMP_name_{i}.txt')
        os.rename(cur_deepseek_file_dir, root_dir+'\\_'+filename)


# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.tokenize import sent_tokenize
#
# # Скачиваем необходимые ресурсы один раз
# nltk.download('punkt')
# nltk.download('punkt_tab')
#
# # Пример текста
# text = 'РАЗРАБОТКА АДАПТИВНОГО ВЕБ-ЧАТА'
#
# # Токенизация по словам
# words = word_tokenize(text)
#
# # Фильтруем слова: убираем знаки препинания и числа (опционально)
# filtered_words = [word for word in words if word.isalpha()]
#
# # Выводим результат
# print("Слова в тексте filtered:", filtered_words)
# print("Количество слов filtered:", len(filtered_words))
#
# # Выводим результат
# print("Слова в тексте:", words)
# print("Количество слов:", len(words))
#
# sentences_text = '''
#     Привет! Это предложение 1. А это предложение 2. Но это - третье.
# '''
# sentences = sent_tokenize(sentences_text)
#
# print(sentences)
# print(len(sentences))


# print([1,2,3])
# print(sum([1,2,3]))