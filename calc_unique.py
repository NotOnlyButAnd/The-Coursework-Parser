import sqlite3
import json
import re
from collections import Counter
from itertools import chain


def get_calculated_data_from_db():
    conn = sqlite3.connect(g_db_name)
    cursor = conn.cursor()

    cursor.execute(f'''
        select
             t.id as t_id, t.source_type, t.topic, t.subtopic, t.content, t.filename,
             t_c.id as t_c_id, t_c.text_id as t_c_text_id,
             t_c.count_words, t_c.count_sentences, t_c.count_syllables, t_c.flesch_reading_index, 
             t_c.avg_punct_by_sentences, t_c.avg_words_by_sentences, t_c.count_words_by_sentences, 
             t_c.count_punct_by_sentences, t_c.words_by_sentences, t_c.content_by_sentences, t_c.morph_characteristics,
             t_c.count_unique_words, t_c.ratio_unique_words
        from 
            text t 
            join text_characteristic t_c on t.id = t_c.text_id
    ''')
    for row in cursor.fetchall():
        if row[1] == 'people':
            g_people_text_data.append({
                "t_db_id":          row[0],
                "source_type":      row[1],
                "topic":            row[2],
                "subtopic":         row[3],
                "content":          row[4],
                "filename":         row[5],
                "t_c_db_id":        row[6],
                "t_c_text_id":      row[7],
                "count_words":              row[8],
                "count_sentences":          row[9],
                "count_syllables":          row[10],
                "flesch_reading_index":     row[11],
                "avg_punct_by_sentences":   row[12],
                "avg_words_by_sentences":   row[13],
                "count_words_by_sentences": json.loads(row[14]),
                "count_punct_by_sentences": json.loads(row[15]),
                "words_by_sentences":       json.loads(row[16]),
                "content_by_sentences":     json.loads(row[17]),
                "morph_characteristics":    json.loads(row[18]),
                "count_unique_words":       row[19],
                "ratio_unique_words":       row[20]
            })
        elif row[1] == 'deepseek' or row[1] == 'yandexgpt':
            g_llm_text_data.append({
                "t_db_id":          row[0],
                "source_type":      row[1],
                "topic":            row[2],
                "subtopic":         row[3],
                "content":          row[4],
                "filename":         row[5],
                "t_c_db_id":        row[6],
                "t_c_text_id":      row[7],
                "count_words":              row[8],
                "count_sentences":          row[9],
                "count_syllables":          row[10],
                "flesch_reading_index":     row[11],
                "avg_punct_by_sentences":   row[12],
                "avg_words_by_sentences":   row[13],
                "count_words_by_sentences": json.loads(row[14]),
                "count_punct_by_sentences": json.loads(row[15]),
                "words_by_sentences":       json.loads(row[16]),
                "content_by_sentences":     json.loads(row[17]),
                "morph_characteristics":    json.loads(row[18]),
                "count_unique_words":       row[19],
                "ratio_unique_words":       row[20]
            })

    print('\npeople data:')
    for i in range(0, len(g_people_text_data)):
        if i == 5:
            break
        print(g_people_text_data[i])

    print('\nllm data:')
    for i in range(0, len(g_llm_text_data)):
        if i == 10:
            break
        print(g_llm_text_data[i])

    conn.close()


# Подсчет уникальных слов в тексте
def analyze_nested_word_lists(word_lists):
    # Объединяем все слова из всех списков в один плоский список
    all_words = list(chain.from_iterable(word_lists))

    # Приводим слова к нижнему регистру и удаляем лишние символы
    processed_words = [re.sub(r'[^а-яёa-z\-]', '', word.lower()) for word in all_words]
    processed_words = [word for word in processed_words if word]  # Удаляем пустые строки

    if not processed_words:
        return 0, 0.0, [], []

    # Подсчитываем общее количество слов
    total_words = len(processed_words)

    # Подсчитываем уникальные слова и их частотность
    word_counts = Counter(processed_words)
    num_unique = len(word_counts)

    # Вычисляем долю уникальных слов
    unique_ratio = num_unique / total_words

    # Получаем самые частые и самые редкие слова
    most_common = word_counts.most_common(10)
    least_common = word_counts.most_common()[-10:]

    return {
        'total_words': total_words,
        'unique_words': num_unique,
        'unique_ratio': unique_ratio * 100,
        'most_common_words': most_common,
        'least_common_words': least_common
    }


g_db_name = 'people_and_llm_texts.db'
g_people_text_data = []
g_llm_text_data = []

## Получение данных из БД: тексты и метрики
get_calculated_data_from_db()

conn = sqlite3.connect(g_db_name)
for o in g_people_text_data:
    t_uni = analyze_nested_word_lists(o['words_by_sentences'])
    o['count_unique_words'] = t_uni['unique_words']
    o['ratio_unique_words'] = t_uni['unique_ratio']
    # обновляем данные в таблице
    cursor = conn.cursor()
    cursor.execute(f'''
        update text_characteristic
        set count_unique_words = {o['count_unique_words']}
        where id = {o['t_c_db_id']}
    ''')
    cursor.execute(f'''
        update text_characteristic
        set ratio_unique_words = {o['ratio_unique_words']}
        where id = {o['t_c_db_id']}
    ''')

conn.commit()


for o in g_llm_text_data:
    t_uni = analyze_nested_word_lists(o['words_by_sentences'])
    o['count_unique_words'] = t_uni['unique_words']
    o['ratio_unique_words'] = t_uni['unique_ratio']
    cursor = conn.cursor()
    cursor.execute(f'''
        update text_characteristic
        set count_unique_words = {o['count_unique_words']}
        where id = {o['t_c_db_id']}
    ''')
    cursor.execute(f'''
        update text_characteristic
        set ratio_unique_words = {o['ratio_unique_words']}
        where id = {o['t_c_db_id']}
    ''')

conn.commit()
conn.close()

print('\n-----------\npeople object 0:\n-----------')
for item, value in g_people_text_data[0].items():
    print(f'---\n"{item}": {value}\n---')
print('\n-----------\nllm object 0:\n-----------')
for item, value in g_llm_text_data[0].items():
    print(f'---\n"{item}": {value}\n---')
## Получение данных из БД: тексты и метрики

