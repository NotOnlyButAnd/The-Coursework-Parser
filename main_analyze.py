import sqlite3
import string
import re
from collections import Counter
from itertools import chain

import matplotlib.pyplot as plt
import numpy as np
# Скачиваем необходимые ресурсы один раз
# nltk.download('punkt')
# nltk.download('punkt_tab')
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import pandas as pd
import json

import pymorphy2


### 'Глобальные' переменные
g_db_name = 'people_and_llm_texts.db'

g_people_text_data = []
g_llm_text_data = []

g_ai_color = '#e1a692'
g_people_color = '#a7d5ed'
### 'Глобальные' переменные


### ПОЛУЧЕНИЕ ДАННЫХ (тексты) ИЗ БД
def get_raw_data_from_db():
    conn = sqlite3.connect(g_db_name)
    cursor = conn.cursor()

    table_name = 'text'
    cursor.execute(f"select * FROM {table_name}")
    for row in cursor.fetchall():
        if row[1] == 'people':
            g_people_text_data.append({
                "db_id":        row[0],
                "source_type":  row[1],
                "topic":        row[2],
                "subtopic":     row[3],
                "content":      row[4],
                "filename":     row[5]
            })
        elif row[1] == 'deepseek' or row[1] == 'yandexgpt':
            g_llm_text_data.append({
                "db_id":        row[0],
                "source_type":  row[1],
                "topic":        row[2],
                "subtopic":     row[3],
                "content":      row[4],
                "filename":     row[5]
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
### ПОЛУЧЕНИЕ ДАННЫХ (тексты) ИЗ БД


### ПОЛУЧЕНИЕ ДАННЫХ (тексты + метрики) ИЗ БД
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
### ПОЛУЧЕНИЕ ДАННЫХ (тексты + метрики) ИЗ БД


### Запись данных (метрики текстов) В БД
def insert_text_characteristics_statement(cur, con, c_obj):
    try:
        cur.execute(
            '''
                INSERT INTO text_characteristic (
                    text_id, 
                    count_words, 
                    count_sentences, 
                    count_syllables, 
                    flesch_reading_index, 
                    avg_punct_by_sentences, 
                    avg_words_by_sentences, 
                    count_words_by_sentences, 
                    count_punct_by_sentences,
                    words_by_sentences, 
                    content_by_sentences, 
                    morph_characteristics,
                    count_unique_words,
                    ratio_unique_words
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                c_obj['db_id'],
                c_obj['count_words'],
                c_obj['count_sentences'],
                c_obj['count_syllables'],
                c_obj['flesch_reading_index'],
                c_obj['avg_punct_by_sentences'],
                c_obj['avg_words_by_sentences'],
                json.dumps(c_obj['count_words_by_sentences']),
                json.dumps(c_obj['count_punct_by_sentences']),
                json.dumps(c_obj['words_by_sentences']),
                json.dumps(c_obj['words_by_sentences']),
                json.dumps(c_obj['morph_characteristics']),
                c_obj['count_unique_words'],
                c_obj['ratio_unique_words']
            )
        )
        con.commit()
    except sqlite3.IntegrityError:
        print(f"Файл {c_obj['filename']} с идентификатором {c_obj['db_id']} уже записан в БД")
    except Exception as e:
        print(f"Ошибка при сохранении файла {c_obj['filename']} с идентификатором {c_obj['db_id']}: {e}")

def add_text_characteristics_to_db():
    print(f"Начинаем добавление метрик текстов в БД...")
    conn = sqlite3.connect(g_db_name)
    cursor = conn.cursor()

    # Вставляем данные для текстов людей
    for i in range(0, len(g_people_text_data)):
        c_text = g_people_text_data[i]
        insert_text_characteristics_statement(cursor, conn, c_text)

    # Вставляем данные для текстов LLM
    for i in range(0, len(g_llm_text_data)):
        c_text = g_llm_text_data[i]
        insert_text_characteristics_statement(cursor, conn, c_text)

    conn.close()
    print(f"Добавление метрик в БД завершено!")
### Запись данных (метрики текстов) В БД


# Количество всех текстов
def get_count_all():
    return len(g_people_text_data) + len(g_llm_text_data)

# Количество текстов ИИ
def get_count_ai():
    return len(g_llm_text_data)

# Количество текстов людей
def get_count_human():
    return len(g_people_text_data)

# Круговая диаграмма количества текстов в датасете
def show_count_records_pie():
    def fmt(x):
        return '{:.1f}%\n({:.0f} текстов)'.format(x, count_all * x / 100)

    count_all = get_count_all()
    count_ai = get_count_ai()
    count_human = get_count_human()

    percent_ai = (count_ai * 100) / count_all
    percent_human = (count_human * 100) / count_all

    print('Percent', percent_ai, percent_human)

    fig, ax = plt.subplots()
    labels = ['ИИ', 'Человек']

    ax.pie([percent_ai, percent_human], labels=labels, autopct=fmt, pctdistance=1.35, labeldistance=.6, colors=[g_ai_color, g_people_color])

    plt.title('Распределение текстов в наборе данных.\n Всего записей: ' + str(count_all))

    plt.show(block=False)


# Среднее количество слов в тексте ИИ
def get_avg_count_words_ai():
    s = 0
    for r in g_llm_text_data:
        s += r['count_words']

    # TODO: убрать коммент
    # return 100
    return int(s / len(g_llm_text_data))

# Среднее количество слов в тексте человека
def get_avg_count_words_human():
    s = 0
    for r in g_people_text_data:
        s += r['count_words']

    # TODO: убрать коммент
    # return 100
    return int(s / len(g_people_text_data))

# Функция для добавления меток к гистограмме
def add_labels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i], y[i], ha='center')  # Aligning text at center

# Гистограмма: сравнение среднего количества слов в тексте ИИ и человека
def show_count_words_bar():
    avg_count_words_ai = get_avg_count_words_ai()
    avg_count_words_human = get_avg_count_words_human()

    objects = ('ИИ', 'Человек')
    plt.bar(np.arange(len(objects)), [avg_count_words_ai, avg_count_words_human], align='center', alpha=0.5, color=[g_ai_color, g_people_color])
    plt.xticks(np.arange(len(objects)), objects)
    plt.ylabel('Среднее количество слов')
    plt.title('Среднее количество слов в тексте')

    add_labels(['ИИ', 'Человек'], [avg_count_words_ai, avg_count_words_human])

    plt.show(block=False)
    return


# Среднее количество предложений в тексте ИИ
def get_avg_count_sentences_ai():
    s = 0
    for r in g_llm_text_data:
        s += len(r['count_words_by_sentences'])

    # TODO: убрать коммент
    # return 100
    return int(s / len(g_llm_text_data))

# Среднее количество предложений в тексте человека
def get_avg_count_sentences_human():
    s = 0
    for r in g_people_text_data:
        s += len(r['count_words_by_sentences'])

    return int(s / len(g_people_text_data))

# Гистограмма: сравнение среднего количества предложений в тексте ИИ и человека
def show_count_sentences_bar():
    avg_count_sentences_ai = get_avg_count_sentences_ai()
    avg_count_sentences_human = get_avg_count_sentences_human()

    objects = ('ИИ', 'Человек')
    plt.bar(np.arange(len(objects)), [avg_count_sentences_ai, avg_count_sentences_human], align='center', alpha=0.5, color=[g_ai_color, g_people_color])
    plt.xticks(np.arange(len(objects)), objects)
    plt.ylabel('Среднее количество предложений')
    plt.title('Среднее количество предложений в тексте')

    add_labels(['ИИ', 'Человек'], [avg_count_sentences_ai, avg_count_sentences_human])

    plt.show(block=False)
    return


def show_count_words_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='count_words', bins=100, grid=False, color=g_people_color, zorder=1, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество слов в тексте: Человек")
        ax.set_xlabel("Количество слов")
        ax.set_ylabel("Количество текстов")
        ax.set_xticks(range(0, 1000, 100))  # Шаг 100 от 0 до 1000

def show_count_words_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='count_words', bins=100, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество слов в тексте: ИИ")
        ax.set_xlabel("Количество слов")
        ax.set_ylabel("Количество текстов")
        ax.set_xticks(range(0, 1000, 100))  # Шаг 100 от 0 до 1000

def show_words_by_sentences_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='avg_words_by_sentences', bins=100, grid=False, color=g_people_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Среднее количество слов в предложении: Человек")
        ax.set_xlabel("Среднее количество слов в предложении")
        ax.set_ylabel("Количество текстов")

def show_words_by_sentences_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='avg_words_by_sentences', bins=100, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Среднее количество слов в предложении: ИИ")
        ax.set_xlabel("Среднее количество слов в предложении")
        ax.set_ylabel("Количество текстов")


def show_punctuation_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='avg_punct_by_sentences', bins=25, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Среднее количество знаков пунктуации в предложении: ИИ")
        ax.set_xlabel("Среднее количество знаков пунктуации в предложении")
        ax.set_ylabel("Количество текстов")

def show_punctuation_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='avg_punct_by_sentences', bins=25, grid=False, color=g_people_color, zorder=1, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Среднее количество знаков пунктуации в предложении: Человек")
        ax.set_xlabel("Среднее количество знаков пунктуации в предложении")
        ax.set_ylabel("Количество текстов")


def show_flesh_readability_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='flesch_reading_index', bins=100, grid=False, color=g_people_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Удобочитаемость текстов: Человек")
        ax.set_xlabel("Удобочитаемость текстов")
        ax.set_ylabel("Количество текстов")
        ax.set_xticks(range(0, 110, 10))  # Шаг 10 от 0 до 100

def show_flesh_readability_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='flesch_reading_index', bins=100, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Удобочитаемость текстов: ИИ")
        ax.set_xlabel("Удобочитаемость текстов")
        ax.set_ylabel("Количество текстов")
        ax.set_xticks(range(0, 110, 10))  # Шаг 10 от 0 до 100


def show_unique_words_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='count_unique_words', bins=25, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество уникальных слов в тексте: ИИ")
        ax.set_xlabel("Количество уникальных слов в тексте")
        ax.set_ylabel("Количество текстов")

def show_unique_words_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='count_unique_words', bins=25, grid=False, color=g_people_color, zorder=1, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество уникальных слов в тексте: Человек")
        ax.set_xlabel("Количество уникальных слов в тексте")
        ax.set_ylabel("Количество текстов")

def show_percent_unique_words_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='ratio_unique_words', bins=50, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Доля уникальных слов в тексте: ИИ")
        ax.set_xlabel("Доля уникальных слов в тексте")
        ax.set_ylabel("Количество текстов")
        ax.set_xticks(range(0, 110, 10))  # Шаг 10 от 0 до 100

def show_percent_unique_words_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='ratio_unique_words', bins=50, grid=False, color=g_people_color, zorder=1, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Доля уникальных слов в тексте: Человек")
        ax.set_xlabel("Доля уникальных слов в тексте")
        ax.set_ylabel("Количество текстов")
        ax.set_xticks(range(0, 110, 10))  # Шаг 10 от 0 до 100


def get_avg_ratio_of_some_morph(data_obj, morph_name):
    # Собираем все значения в один список
    all_ratios = []
    # Проходимся по всем записям в объекте
    for i in range(0, len(data_obj)):
        # Проходимся по "списку долей" каждого из текстов
        for c_ratio in data_obj[i][f'ratio_{morph_name}_by_sent']:
            all_ratios.append(c_ratio)

    # Вычисляем среднее
    return sum(all_ratios) / len(all_ratios)


def show_adjective_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='count_adjf', bins=100, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество прилагательных в тексте: ИИ")
        ax.set_xlabel("Количество прилагательных в тексте")
        ax.set_ylabel("Количество текстов")

def show_adjective_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='count_adjf', bins=100, grid=False, color=g_people_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество прилагательных в тексте: Человек")
        ax.set_xlabel("Количество прилагательных в тексте")
        ax.set_ylabel("Количество текстов")

def show_adjective_by_sentences_bar():
    avg_ai = round(get_avg_ratio_of_some_morph(g_llm_text_data, 'adjf'), 2)
    print(f'\nshow_adjective_by_sentences_bar, avg_ai = {avg_ai}')
    avg_human = round(get_avg_ratio_of_some_morph(g_people_text_data, 'adjf'), 2)
    print(f'show_adjective_by_sentences_bar, avg_human = {avg_human}')

    objects = ('ИИ', 'Человек')
    plt.bar(np.arange(len(objects)), [avg_ai, avg_human], align='center',
            alpha=0.5,
            color=[g_ai_color, g_people_color])
    plt.xticks(np.arange(len(objects)), objects)
    plt.ylabel('Средняя доля прилагательных в предложении')
    plt.title('Средняя доля прилагательных в предложении')

    add_labels(['ИИ', 'Человек'], [avg_ai, avg_human])

    plt.show(block=False)


def show_noun_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='count_noun', bins=100, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество существительных в тексте: ИИ")
        ax.set_xlabel("Количество существительных в тексте")
        ax.set_ylabel("Количество текстов")

def show_noun_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='count_noun', bins=100, grid=False, color=g_people_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество существительных в тексте: Человек")
        ax.set_xlabel("Количество существительных в тексте")
        ax.set_ylabel("Количество текстов")

def show_noun_by_sentences_bar():
    avg_ai = round(get_avg_ratio_of_some_morph(g_llm_text_data, 'noun'), 2)
    avg_human = round(get_avg_ratio_of_some_morph(g_people_text_data, 'noun'), 2)

    objects = ('ИИ', 'Человек')
    plt.bar(np.arange(len(objects)), [avg_ai, avg_human], align='center',
            alpha=0.5,
            color=[g_ai_color, g_people_color])
    plt.xticks(np.arange(len(objects)), objects)
    plt.ylabel('Средняя доля существительных в предложении')
    plt.title('Средняя доля существительных в предложении')

    add_labels(['ИИ', 'Человек'], [avg_ai, avg_human])

    plt.show(block=False)


def show_npro_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='count_npro', bins=15, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество местоимений в тексте: ИИ")
        ax.set_xlabel("Количество местоимений в тексте")
        ax.set_ylabel("Количество текстов")
        ax.set_xticks(range(0, 15, 1))

def show_npro_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='count_npro', bins=15, grid=False, color=g_people_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество местоимений в тексте: Человек")
        ax.set_xlabel("Количество местоимений в тексте")
        ax.set_ylabel("Количество текстов")
        ax.set_xticks(range(0, 50, 5))

def show_npro_by_sentences_bar():
    avg_ai = round(get_avg_ratio_of_some_morph(g_llm_text_data, 'npro'), 2)
    avg_human = round(get_avg_ratio_of_some_morph(g_people_text_data, 'npro'), 2)

    objects = ('ИИ', 'Человек')
    plt.bar(np.arange(len(objects)), [avg_ai, avg_human], align='center',
            alpha=0.5,
            color=[g_ai_color, g_people_color])
    plt.xticks(np.arange(len(objects)), objects)
    plt.ylabel('Средняя доля местоимений в предложении')
    plt.title('Средняя доля местоимений в предложении')

    add_labels(['ИИ', 'Человек'], [avg_ai, avg_human])

    plt.show(block=False)


def show_stop_ai_hist():
    df = pd.DataFrame(g_llm_text_data)
    axarr = df.hist(column='count_stop', bins=100, grid=False, color=g_ai_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество стоп-слов в тексте: ИИ")
        ax.set_xlabel("Количество стоп-слов в тексте")
        ax.set_ylabel("Количество текстов")

def show_stop_human_hist():
    df = pd.DataFrame(g_people_text_data)
    axarr = df.hist(column='count_stop', bins=100, grid=False, color=g_people_color, zorder=2, rwidth=0.9)
    for ax in axarr.flatten():
        ax.set_title("Количество стоп-слов в тексте: Человек")
        ax.set_xlabel("Количество стоп-слов в тексте")
        ax.set_ylabel("Количество текстов")

def show_stop_by_sentences_bar():
    avg_ai = round(get_avg_ratio_of_some_morph(g_llm_text_data, 'stop'), 2)
    avg_human = round(get_avg_ratio_of_some_morph(g_people_text_data, 'stop'), 2)

    objects = ('ИИ', 'Человек')
    plt.bar(np.arange(len(objects)), [avg_ai, avg_human], align='center',
            alpha=0.5,
            color=[g_ai_color, g_people_color])
    plt.xticks(np.arange(len(objects)), objects)
    plt.ylabel('Средняя доля стоп-слов в предложении')
    plt.title('Средняя доля стоп-слов в предложении')

    add_labels(['ИИ', 'Человек'], [avg_ai, avg_human])

    plt.show(block=False)



### Функции для расчета метрик для каждого текста
# Подсчет количеств и долей прилагательных, существительных, местоимений, стоп-слов для каждого текста
def calc_morph_numbers(data_obj):
    # Проходимся по всем записям в объекте
    for i in range(0, len(data_obj)):
        cnt_adjf = 0
        ratio_adjf_by_sent = []
        cnt_noun = 0
        ratio_noun_by_sent = []
        cnt_npro = 0
        ratio_npro_by_sent = []
        cnt_stop = 0
        ratio_stop_by_sent = []

        # Проходимся по морфологическим характеристикам текущего объекта
        t_obj_motph_char = data_obj[i]['morph_characteristics']
        t_obj_count_words_by_sent = data_obj[i]['count_words_by_sentences']
        for j in range(0, len(t_obj_motph_char)):
            cnt_adjf += t_obj_motph_char[j]['ADJF']
            cnt_noun += t_obj_motph_char[j]['NOUN']
            cnt_npro += t_obj_motph_char[j]['NPRO']
            cnt_stop += t_obj_motph_char[j]['STOP']
            if t_obj_count_words_by_sent[j] != 0:
                # Количество "части речи" в предложении / количество слов в предложении
                ratio_adjf_by_sent.append(t_obj_motph_char[j]['ADJF'] / t_obj_count_words_by_sent[j] * 100)
                ratio_noun_by_sent.append(t_obj_motph_char[j]['NOUN'] / t_obj_count_words_by_sent[j] * 100)
                ratio_npro_by_sent.append(t_obj_motph_char[j]['NPRO'] / t_obj_count_words_by_sent[j] * 100)
                ratio_stop_by_sent.append(t_obj_motph_char[j]['STOP'] / t_obj_count_words_by_sent[j] * 100)
            else:
                ratio_adjf_by_sent.append(0.0)
                ratio_noun_by_sent.append(0.0)
                ratio_npro_by_sent.append(0.0)
                ratio_stop_by_sent.append(0.0)

        # Записываем информацию в объект
        data_obj[i]['count_adjf'] = cnt_adjf
        data_obj[i]['ratio_adjf_by_sent'] = ratio_adjf_by_sent
        data_obj[i]['count_noun'] = cnt_noun
        data_obj[i]['ratio_noun_by_sent'] = ratio_noun_by_sent
        data_obj[i]['count_npro'] = cnt_npro
        data_obj[i]['ratio_npro_by_sent'] = ratio_npro_by_sent
        data_obj[i]['count_stop'] = cnt_stop
        data_obj[i]['ratio_stop_by_sent'] = ratio_stop_by_sent

# Подсчет частей речи в предложении (морфологический анализ)
def count_pos(v_sentence):
    morph = pymorphy2.MorphAnalyzer()
    # words = v_sentence.split()
    words = word_tokenize(v_sentence)

    poses = {
        'ADJF':     0,  # прилагательное
        'ADJF_L':   [],
        'NOUN':     0,  # существительное
        'NOUN_L':   [],
        'NPRO':     0,  # местоимение
        'NPRO_L':   [],
        'STOP':     0,  # стоп-слова (предлоги, частицы и т.д.)
        'STOP_L':   [],
        'OTHR':     0,  # остальное
        'OTHR_L':   []
    }

    stop_tags = {
        'PREP',  # предлог
        'CONJ',  # союз
        'PRCL',  # частица
        'INTJ',  # междометие
        'NUMR',  # числительное
        'NUMB',  # число
        'ROMN',  # римская цифра
        'LATN',  # латиница
        'PNCT',  # пунктуация
        'UNKN',  # неизвестное
        'INIT',  # инициал
        'SYMB'  # символ
    }

    for word in words:
        # print(f'word: {word}')
        parsed = morph.parse(word)[0]
        pos = parsed.tag.POS

        if pos in ('ADJF', 'ADJS'):
            poses['ADJF'] += 1
            poses['ADJF_L'].append(word)
        elif pos == 'NOUN':
            poses['NOUN'] += 1
            poses['NOUN_L'].append(word)
        elif pos == 'NPRO':
            poses['NPRO'] += 1
            poses['NPRO_L'].append(word)
        elif pos in stop_tags:
            poses['STOP'] += 1
            poses['STOP_L'].append(word)
        else:
            poses['OTHR'] += 1  # на всякий случай, если что-то не учли
            poses['OTHR_L'].append(word)

    return poses

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

# Функция для удаления знаков пунктуации
def remove_punctuation(input_string):
    # Создаем таблицу перевода, где все знаки пунктуации заменяются на None
    translator = str.maketrans('', '', string.punctuation)
    # Удаляем пунктуацию из строки
    return input_string.translate(translator)

# Функция подсчета количества слогов
# TODO: для английских слов НЕ СЧИТАЕТСЯ КОЛИЧЕСТВО СЛОГОВ
def count_syllables(text):
    vowels = "аеёиоуыэюя"
    return sum(1 for char in text.lower() if char in vowels)

# Рассчёт нужных показателей для каждого текста из объекта data_obj
# data_obj - объект, в котором лежат тексты ИИ\людей
# content_field - название поля объекта, в котором находится непосредственно текст
def calc_measures_for_texts(data_obj, content_field):
    # Проходимся по всем записям в объекте
    for i in range(0, len(data_obj)):
        # Вычленяем текст текущей записи
        cur_text = data_obj[i][f'{content_field}']
        print(f'Обрабатываем файл {data_obj[i]["filename"]} - {content_field} - {data_obj[i]["source_type"]}')

        # Сюда будем складывать количества слов по каждому из предложений
        # => длина этого списка - количество предложений в тексте
        # => сумма элементов этого списка - количество слов в тексте
        count_words_by_sentences = []
        words_by_sentences = []
        count_punct_by_sentences = []
        morph_characteristics = []

        # Разделяем текст по предложениям (nltk)
        sentences = sent_tokenize(cur_text) # список строк, каждая строка - предложение
        data_obj[i]['content_by_sentences'] = sentences

        # Проходимся по каждому предложению
        for sentence in sentences:
            # Разделяем предожение на слова (nltk)
            # для подсчета слов очистить от знаков препинания нужно ТОЧНО, т.к. nltk выделяет их в отдельные слова
            words = word_tokenize(remove_punctuation(sentence))
            # Складываем информацию по текущему предложению в списки
            words_by_sentences.append(words)
            count_words_by_sentences.append(len(words))
            count_punct_by_sentences.append(sum(1 for char in sentence if char in string.punctuation))
            morph_characteristics.append(count_pos(sentence))


        # Записываем информацию о количествах слов, предложений, знаках пунктуации в объект с текстами
        data_obj[i]['words_by_sentences'] = words_by_sentences
        data_obj[i]['count_words_by_sentences'] = count_words_by_sentences
        data_obj[i]['count_punct_by_sentences'] = count_punct_by_sentences
        data_obj[i]['morph_characteristics'] = morph_characteristics

        # Расчёт "среднего количества слов на предложение"
        if len(count_words_by_sentences) > 0:
            average_words_per_sentence = sum(count_words_by_sentences) / len(count_words_by_sentences)
        else:
            average_words_per_sentence = 0

        # Расчёт "среднего количества знаков пунктуации на предложение"
        if len(count_punct_by_sentences) > 0:
            average_punct_per_sentence = sum(count_punct_by_sentences) / len(count_punct_by_sentences)
        else:
            average_punct_per_sentence = 0

        data_obj[i]['avg_words_by_sentences'] = average_words_per_sentence
        data_obj[i]['avg_punct_by_sentences'] = average_punct_per_sentence

        data_obj[i]['count_words'] = sum(count_words_by_sentences)

        # Индекс удобочитаемости флеша
        # 206.835 - 1.52 * (всего слов / всего предложений) - 65.14 * (всего слогов / всего слов)
        data_obj[i]['count_sentences'] = len(sentences)
        data_obj[i]['count_syllables'] = count_syllables(cur_text)
        data_obj[i]['flesch_reading_index'] = (
            206.835 -
            1.3 * (data_obj[i]['count_words'] / len(sentences)) -
            60.1 * (count_syllables(cur_text) / data_obj[i]['count_words'])
        )
        unique_words_resul = analyze_nested_word_lists(words_by_sentences)
        data_obj[i]['count_unique_words'] = unique_words_resul['unique_words']
        data_obj[i]['ratio_unique_words'] = unique_words_resul['unique_ratio']
### Функции для расчета метрик для каждого текста


#### Main program
## ПОЛУЧЕНИЕ метрик по текстам, которые не обработаны
# get_raw_data_from_db()
#
# # ВРЕМЕННО обрабатываем только некоторые файлы
# g_people_text_data = [x for x in g_people_text_data if x['db_id'] > 18]     # 15 < x['db_id'] <= 18
# g_llm_text_data = [x for x in g_llm_text_data if x['db_id'] > 18]           # 15 < x['db_id'] <= 18
#
# calc_measures_for_texts(g_people_text_data, 'content')
# calc_measures_for_texts(g_llm_text_data, 'content')
#
# print(f'\n----- people -----\n {g_people_text_data[0]} \n {g_people_text_data[0]["words_by_sentences"]} \n----- people -----\n')
# print('--')
# print(g_people_text_data[0]['content'])
# print('--')
# print(f'\n----- llm -----\n {g_llm_text_data[0]} \n {g_llm_text_data[0]["words_by_sentences"]} \n----- llm -----\n')
# print('--')
# print(g_llm_text_data[0]['content'])
# print('--')
#
# add_text_characteristics_to_db()
## ПОЛУЧЕНИЕ метрик по текстам, которые не обработаны

## Получение данных из БД: тексты и метрики
get_calculated_data_from_db()
# print('\n-----------\npeople object 0:\n-----------')
# for item, value in g_people_text_data[0].items():
#     print(f'---\n"{item}": {value}\n---')
# print('\n-----------\nllm object 0:\n-----------')
# for item, value in g_llm_text_data[0].items():
#     print(f'---\n"{item}": {value}\n---')
## Получение данных из БД: тексты и метрики

## Построение различных графиков
# show_count_records_pie()
# show_count_words_bar()
# show_count_sentences_bar()
# show_count_words_human_hist()
# show_count_words_ai_hist()
# plt.show()

# # Уберем выбросы для наглядности
# g_people_text_data = [x for x in g_people_text_data if x['avg_words_by_sentences'] < 50]
# show_words_by_sentences_human_hist()
# show_words_by_sentences_ai_hist()

# # Уберем выбросы для наглядности
# g_people_text_data = [x for x in g_people_text_data if x['avg_punct_by_sentences'] < 13]
# show_punctuation_ai_hist()
# show_punctuation_human_hist()

# show_flesh_readability_ai_hist()
# show_flesh_readability_human_hist()

# show_unique_words_ai_hist()
# show_unique_words_human_hist()
# show_percent_unique_words_ai_hist()
# show_percent_unique_words_human_hist()
# plt.show()

# ЧАСТИ РЕЧИ
calc_morph_numbers(g_people_text_data)
calc_morph_numbers(g_llm_text_data)

# show_adjective_ai_hist()
# show_adjective_human_hist()
show_adjective_by_sentences_bar()

# # Уберем выбросы для наглядности
# g_people_text_data = [x for x in g_people_text_data if x['count_noun'] < 500]
# show_noun_ai_hist()
# show_noun_human_hist()
# show_noun_by_sentences_bar()

# show_npro_ai_hist()
# show_npro_human_hist()
# show_npro_by_sentences_bar()

# # Уберем выбросы для наглядности
# g_people_text_data = [x for x in g_people_text_data if x['count_stop'] < 300]
# show_stop_ai_hist()
# show_stop_human_hist()
# show_stop_by_sentences_bar()
plt.show()
## Построение различных графиков

#### Main program