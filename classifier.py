# -*- coding: utf-8 -*-

import sqlite3
import json
from logging import exception

import numpy as np
from sklearn.model_selection    import train_test_split
from sklearn.linear_model       import LogisticRegression
from sklearn.neighbors          import KNeighborsClassifier
from sklearn.metrics            import accuracy_score
from sklearn.preprocessing      import StandardScaler
import joblib

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import string
import pymorphy2
from itertools import chain
from collections import Counter
import re

import tkinter as tk
from tkinter import messagebox


### 'Глобальные' переменные
g_db_name = 'people_and_llm_texts.db'

g_people_text_data = []
g_llm_text_data = []

g_classifier_people_data = []
g_classifier_llm_data = []
### 'Глобальные' переменные


### Фунции для ПОЛУЧЕНИЯ ДАННЫХ (тексты + метрики)
# Получение сырых данных из БД
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

    conn.close()

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
        data_obj[i]['avg_ratio_adjf_by_sent'] = sum(ratio_adjf_by_sent) / len(ratio_adjf_by_sent)
        data_obj[i]['count_noun'] = cnt_noun
        data_obj[i]['ratio_noun_by_sent'] = ratio_noun_by_sent
        data_obj[i]['avg_ratio_noun_by_sent'] = sum(ratio_noun_by_sent) / len(ratio_noun_by_sent)
        data_obj[i]['count_npro'] = cnt_npro
        data_obj[i]['ratio_npro_by_sent'] = ratio_npro_by_sent
        data_obj[i]['avg_ratio_npro_by_sent'] = sum(ratio_npro_by_sent) / len(ratio_npro_by_sent)
        data_obj[i]['count_stop'] = cnt_stop
        data_obj[i]['ratio_stop_by_sent'] = ratio_stop_by_sent
        data_obj[i]['avg_ratio_stop_by_sent'] = sum(ratio_stop_by_sent) / len(ratio_stop_by_sent)

# Подготовка только тех признаков, которые нужны для классификаторов
def prepare_classifier_data(raw_obj, class_obj):
    for i in range(0, len(raw_obj)):
        class_obj.append({
            # Техническая информация о строках в базе данных
            "t_db_id":      raw_obj[i]['t_db_id'],
            "filename":     raw_obj[i]['filename'],
            "t_c_db_id":    raw_obj[i]['t_c_db_id'],
            "t_c_text_id":  raw_obj[i]['t_c_text_id'],
            # Контент текста
            "source_type":          'people' if raw_obj[i]['source_type'] == 'people' else 'llm',
            "topic":                raw_obj[i]['topic'],
            "subtopic":             raw_obj[i]['subtopic'],
            "content":              raw_obj[i]['content'],
            "words_by_sentences":   raw_obj[i]['words_by_sentences'],
            # Характеристики текста (здесь - в том же порядке, что описаны в тексте работы, но учтены только важные)
            "avg_words_by_sentences":   raw_obj[i]['avg_words_by_sentences'],
            "avg_punct_by_sentences":   raw_obj[i]['avg_punct_by_sentences'],
            "flesch_reading_index":     raw_obj[i]['flesch_reading_index'],
            "ratio_unique_words":       raw_obj[i]['ratio_unique_words'],
            "avg_ratio_noun_by_sent":   raw_obj[i]['avg_ratio_noun_by_sent'],
            "avg_ratio_npro_by_sent":   raw_obj[i]['avg_ratio_npro_by_sent'],
            "avg_ratio_stop_by_sent":   raw_obj[i]['avg_ratio_stop_by_sent']
        })

# Получение исходных данных для главной программы, сохранение данных для видео
def prepare_pre_data():
    global g_classifier_llm_data
    # Получаем сырые данные из БД и считаем морфологические числа (среднее, доля, кол-во)
    get_calculated_data_from_db()
    calc_morph_numbers(g_people_text_data)
    calc_morph_numbers(g_llm_text_data)

    # Создаем объекты с данными и признаками, которые нужны классификатору
    prepare_classifier_data(g_people_text_data, g_classifier_people_data)
    prepare_classifier_data(g_llm_text_data, g_classifier_llm_data)

    # Сохраним несколько текстов для показа в видео
    indexes_for_saving = [0, 35, 200, 320, 410]
    with open('for_video/saved_objects_for_video.txt', 'w', encoding='utf-8') as f_w:
        for i in indexes_for_saving:
            # Сохраняем данные объектов в файл
            f_w.write(json.dumps(g_classifier_people_data[i], ensure_ascii=False))
            f_w.write('\n')
            f_w.write(json.dumps(g_classifier_llm_data[i * 2], ensure_ascii=False))
            f_w.write('\n')
            f_w.write(json.dumps(g_classifier_llm_data[i * 2 + 1], ensure_ascii=False))
            f_w.write('\n---\n')
            # Удаляем элементы из подготовленных объектов с текстами людей и LLM
            del g_classifier_people_data[i]
            del g_classifier_llm_data[i * 2]
            del g_classifier_llm_data[i * 2 + 1]
### Фунции для ПОЛУЧЕНИЯ ДАННЫХ (тексты + метрики)


### Функции для классификатора на основе лингвистических метрик
# Функция для подготовки данных к обучению модели
def prepare_data(llm_data, people_data):
    # Создаем признаки и метки
    X = []
    y = []

    # Добавляем данные LLM
    for item in llm_data:
        features = [
            item['avg_words_by_sentences'],
            item['avg_punct_by_sentences'],
            item['flesch_reading_index'],
            item['ratio_unique_words'],
            item['avg_ratio_noun_by_sent'],
            item['avg_ratio_npro_by_sent'],
            item['avg_ratio_stop_by_sent']
        ]
        X.append(features)
        y.append(1)  # 1 для текстов LLM

    # Добавляем данные людей
    for item in people_data:
        features = [
            item['avg_words_by_sentences'],
            item['avg_punct_by_sentences'],
            item['flesch_reading_index'],
            item['ratio_unique_words'],
            item['avg_ratio_noun_by_sent'],
            item['avg_ratio_npro_by_sent'],
            item['avg_ratio_stop_by_sent']
        ]
        X.append(features)
        y.append(0)  # 0 для текстов людей

    return np.array(X), np.array(y)

# Функция для обучения модели
def train_model(X, y):
    # Разделяем данные на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Масштабируем признаки
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Обучаем модель логистической регрессии
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)

    # Оцениваем качество модели
    y_pred = model.predict(X_test)
    print("\n---LogisticRegression\nAccuracy:", accuracy_score(y_test, y_pred))

    return model, scaler

def train_knn_classifier(X, y, test_size=0.2, random_state=1, n_neighbors=7):
    # Разделяем данные на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Масштабируем данные
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Создаем и обучаем модель KNN
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train, y_train)

    # Оцениваем модель
    y_pred = knn.predict(X_test)
    print(f"\n---KNN\nAccuracy: {accuracy_score(y_test, y_pred)}")

    return knn, scaler

# Функция для предсказания вероятности принадлежности текста к LLM-генерации
def predict_probability(model, scaler, text_features):
    # Подготовка признаков
    features = np.array([
        text_features['avg_words_by_sentences'],
        text_features['avg_punct_by_sentences'],
        text_features['flesch_reading_index'],
        text_features['ratio_unique_words'],
        text_features['avg_ratio_noun_by_sent'],
        text_features['avg_ratio_npro_by_sent'],
        text_features['avg_ratio_stop_by_sent']
    ]).reshape(1, -1)

    # Масштабирование
    features_scaled = scaler.transform(features)

    # Предсказание вероятности
    proba = model.predict_proba(features_scaled)
    return proba[0][1]  # Вероятность принадлежности к классу LLM

# Функция с подготовкой, обучением и сохранением модели
def prepare_train_save_model():
    # Подготовка данных
    g_X, g_y = prepare_data(g_classifier_llm_data, g_classifier_people_data)

    # Обучение модели
    g_model, g_scaler = train_model(g_X, g_y)

    # Сохранение модели
    joblib.dump(g_model, 'llm_classifier_model.pkl')
    joblib.dump(g_scaler, 'llm_classifier_scaler.pkl')

    # Обучение модели
    g_knn_model, g_knn_scaler = train_knn_classifier(g_X, g_y)

    # Сохранение модели
    joblib.dump(g_knn_model, 'llm_knn_classifier_model.pkl')
    joblib.dump(g_knn_scaler, 'llm_knn_classifier_scaler.pkl')

# Загрузка сохраненных модели и scaler
def load_model_and_scaler():
    # model = joblib.load('llm_knn_classifier_model.pkl')
    # scaler = joblib.load('llm_knn_classifier_scaler.pkl')
    model = joblib.load('llm_classifier_model.pkl')
    scaler = joblib.load('llm_classifier_scaler.pkl')
    return model, scaler

# Интерпретация вероятности по пороговому значению
def threshold_interpretation(probabil, threshold=0.5):
    if probabil >= threshold:
        return {
            "prediction": "LLM",
            "probability": probabil,
            "confidence": "high" if probabil >= 0.7 else "medium",
            "explanation": f"Текст, скорее всего, создан ИИ (вероятность {probabil:.2%})"
        }
    else:
        return {
            "prediction": "Human",
            "probability": 1 - probabil,
            "confidence": "high" if probabil <= 0.3 else "medium",
            "explanation": f"Текст, скорее всего, написан человеком (вероятность {1 - probabil:.1%})"
        }

# Интерпретация вероятности с градациями уверенности и рекомендациями
def advanced_interpretation(probabil):
    result = {
        "raw_probability": probabil,
        "human_probability": 1 - probabil,
        "llm_probability": probabil
    }

    if probabil >= 0.85:
        result.update({
            "prediction": "LLM",
            "confidence": "очень высокая",
            "explanation": "Четкие признаки машинной генерации"
        })
    elif probabil >= 0.7:
        result.update({
            "prediction": "Скорее всего LLM",
            "confidence": "высокая",
            "explanation": "Большинство признаков указывают на ИИ"
        })
    elif probabil >= 0.6:
        result.update({
            "prediction": "Вероятно LLM",
            "confidence": "средняя",
            "explanation": "Есть заметные признаки ИИ-генерации"
        })
    elif probabil >= 0.4:
        result.update({
            "prediction": "Неопределенно",
            "confidence": "низкая",
            "explanation": "Неоднозначный случай, требует дополнительной проверки"
        })
    elif probabil >= 0.3:
        result.update({
            "prediction": "Вероятно человек",
            "confidence": "средняя",
            "explanation": "Большинство признаков указывают на человека"
        })
    else:
        result.update({
            "prediction": "Человек",
            "confidence": "высокая",
            "explanation": "Явные признаки человеческого авторства"
        })

    return result

# Полный цикл классификации объекта текста по лингвистическим метрикам
def classification_by_lingv_metrics(text_obj):
    # 1. Загрузка модели
    g_model, g_scaler = load_model_and_scaler()

    if g_model is None:
        print("Model not loaded")
        exception('Model not loaded')

    # 2. Предсказание вероятности
    proba = -1
    try:
        proba = predict_probability(g_model, g_scaler, text_obj)
    except Exception as e:
        print("Prediction failed")
        exception(f'Prediction failed: \n{e}')

    # 3. Интерпретация
    adv_interpretation = advanced_interpretation(proba)
    thresh_interpretation = threshold_interpretation(proba, threshold=0.5)

    result = {
        "probabilities": {
            "human": adv_interpretation["human_probability"],
            "llm": adv_interpretation["llm_probability"]
        },
        "adv_prediction": adv_interpretation["prediction"],
        "adv_confidence": adv_interpretation["confidence"],
        "adv_explanation": adv_interpretation["explanation"],
        "thresh_prediction": thresh_interpretation["prediction"],
        "thresh_confidence": thresh_interpretation["confidence"],
        "thresh_explanation": thresh_interpretation["explanation"],
    }

    return result

# Функция для удаления знаков пунктуации
def remove_punctuation(input_string):
    # Создаем таблицу перевода, где все знаки пунктуации заменяются на None
    translator = str.maketrans('', '', string.punctuation)
    # Удаляем пунктуацию из строки
    return input_string.translate(translator)

# Подсчет частей речи в предложении (морфологический анализ)
def count_pos(v_sentence):
    morph = pymorphy2.MorphAnalyzer()
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

# Функция подсчета количества слогов
def count_syllables(text):
    vowels = "аеёиоуыэюя"
    return sum(1 for char in text.lower() if char in vowels)

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

def calc_morph_numbers_for_1_obj(data_obj):
    cnt_adjf = 0
    ratio_adjf_by_sent = []
    cnt_noun = 0
    ratio_noun_by_sent = []
    cnt_npro = 0
    ratio_npro_by_sent = []
    cnt_stop = 0
    ratio_stop_by_sent = []

    # Проходимся по морфологическим характеристикам текущего объекта
    t_obj_motph_char = data_obj['morph_characteristics']
    t_obj_count_words_by_sent = data_obj['count_words_by_sentences']
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
    data_obj['avg_ratio_noun_by_sent'] = sum(ratio_noun_by_sent) / len(ratio_noun_by_sent)
    data_obj['avg_ratio_npro_by_sent'] = sum(ratio_npro_by_sent) / len(ratio_npro_by_sent)
    data_obj['avg_ratio_stop_by_sent'] = sum(ratio_stop_by_sent) / len(ratio_stop_by_sent)

# Функция для расчета необходимых метрик по введенному тексту (строка текста)
def calc_needed_metrics(text_content):
    t_obj = {}

    count_words_by_sentences = []
    words_by_sentences = []
    count_punct_by_sentences = []
    morph_characteristics = []

    # Разделяем текст по предложениям (nltk)
    sentences = sent_tokenize(text_content)  # список строк, каждая строка - предложение
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

    # Расчет индекса удобочитаемости Флеша
    count_words = sum(count_words_by_sentences)
    flesch_reading_index = (
        206.835 -
        1.3 * (count_words / len(sentences)) -
        60.1 * (count_syllables(text_content) / count_words)
    )
    flesch_reading_index = ((flesch_reading_index - (-65)) / (64 - (-65))) * 100

    # Расчёт доли уникальных слов
    unique_words_result = analyze_nested_word_lists(words_by_sentences)

    t_obj['count_words_by_sentences'] = count_words_by_sentences
    t_obj['morph_characteristics'] = morph_characteristics
    t_obj['avg_words_by_sentences'] = average_words_per_sentence
    t_obj['avg_punct_by_sentences'] = average_punct_per_sentence
    t_obj['flesch_reading_index'] = flesch_reading_index
    t_obj['ratio_unique_words'] = unique_words_result['unique_ratio']

    calc_morph_numbers_for_1_obj(t_obj)

    return t_obj
### Функции для классификатора на основе лингвистических метрик


### Функции для создания Окна программы
# Функция для показа сообщений с увеличенным шрифтом
def show_custom_message(title, message):
    msg_window = tk.Toplevel()
    msg_window.title(title)
    msg_window.geometry("700x500")

    # Центрирование окна
    window_width = 700
    window_height = 500
    screen_width = msg_window.winfo_screenwidth()
    screen_height = msg_window.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    msg_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Большой шрифт
    # large_font = ('Arial', 14)

    # Текст сообщения
    label = tk.Label(msg_window, text=message, font=large_font, wraplength=660)
    label.pack(pady=5, padx=10)

    # Кнопка OK
    ok_button = tk.Button(msg_window, text="OK", font=large_font,
                          command=msg_window.destroy, width=10)
    ok_button.pack(pady=5)

    # Делаем окно модальным
    msg_window.grab_set()
    msg_window.wait_window()

# Проверка текста на написание LLM
def check_text():
    text = text_entry.get("1.0", tk.END).strip()  # Получаем текст из поля ввода
    if text:  # Проверяем, что текст не пустой
        # Рассчитываем нужные метрики для введенного текста
        current_metrics = calc_needed_metrics(text)
        # messagebox.showinfo("current_metrics", f"current_metrics: \n{current_metrics}")

        # Проводим классификацию
        current_result = classification_by_lingv_metrics(current_metrics)

        # messagebox.showinfo("Результат проверки", f"current_restult: \n{current_restult}")
        message_text = f'''
Пороговая проверка: 
{current_result['thresh_explanation']}

Расширенная проверка (по уровням):
{current_result['adv_explanation']}
Вероятности: LLM - {current_result['probabilities']['llm']:.2%}; Человек - {current_result['probabilities']['human']:.2%}
Предсказание: {current_result['adv_prediction']}
Уверенность: {current_result['adv_confidence']}
        '''
        show_custom_message("Результат проверки", message_text)
    else:
        messagebox.showwarning("Пустой текст", "Введите текст перед сохранением")

# Настройка горячих клавиш для копирования/вставки
def copy_text(event=None):
    text_entry.event_generate("<<Copy>>")

def paste_text(event=None):
    text_entry.event_generate("<<Paste>>")

def cut_text(event=None):
    text_entry.event_generate("<<Cut>>")

def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)
### Функции для создания Окна программы


###### MAIN PROGRAM
# Готовим все данные
prepare_pre_data()

print(f'g_classifier_people_data: {len(g_classifier_people_data)}')
print(f'g_classifier_llm_data: {len(g_classifier_llm_data)}')

# Подготоваливаем, обучаем, сохраняем модель
prepare_train_save_model()

# # Проверка расчета метрик для введенного текста
# input_text = "Мобильные приложения, специально разработанные для различных мобильных устройств, также решают проблему с удобством просмотра сайта, но имеют некоторые недостатки:\nа) Под каждый тип операционной системы нужно своё приложение.\nб) Необходимость загрузки.\nДля того, чтобы пользоваться приложением, пользователям необходимо его загрузить. Это требует каких-то дополнительных усилий от пользователей, и многие не будут этого делать, если точно не уверены, что приложение им очень нужно и они планируют регулярно его использовать.\nПроектирование было начато с адаптивной версии веб-чата для мобильных устройств. На этом этапе нужно было правильно передать смысл и основные идеи с использованием небольшого экрана и всего одной колонки.\nБыли рассмотрены основные типы адаптивных макетов.\n1.1  Резиновый\nДанный макет простой в реализации и очевидный для пользователя тип представления веб-страницы. Основные блоки сжимаются до ширины экрана мобильного устройства, где такое невозможно— перестраиваются в одну длинную ленту.\nРисунок 1. Резиновый адаптивный макет.\n1.2   Перенос блоков\nЭтот тип подходит для многоколоночной веб-страницы: при уменьшении ширины экрана дополнительные блоки переносятся в нижнюю часть макета.\nРисунок 2. Перенос блоков.\n1.3   Переключение макетов\nЭтот способ наиболее удобен при чтении сайта с различных устройств: под каждое разрешение экрана разрабатывается отдельный макет. Способ трудоемок, поэтому менее популярен, чем предыдущие два.\nРисунок 3. Переключение макетов\n1.4 Адаптивность масштабированием\nОчень простой способ, который подходит для несложных веб-страниц. Достигается элементарным масштабированием изображений. Не очень популярный способ, так как не обладает гибкостью.\nРисунок 4. Адаптивность масштабированием\nПри проектировании веб-дизайна для чата был выбран способ переключения макетов. Благодаря данному способу имеется возможность сохранить доступ ко всем функциям чата, независимо от того с какого устройства был выполнен вход."
# result_metrics = calc_needed_metrics(input_text)

#### ОКОННАЯ ПРОГРАММА ДЛЯ ПРОВЕРКИ ТЕКСТОВ
# Создание главного окна
root = tk.Tk()
root.title("Система идентификации авторства текстов: БЯМ или человек")
root.geometry("1600x800")

# Увеличенные размеры шрифтов
large_font = ('Arial', 22)
huge_font = ('Arial', 26)
button_font = ('Arial', 22, 'bold')

# Метка над полем ввода
text_label = tk.Label(root, text="Введите текст для проверки:", font=huge_font)
text_label.pack(pady=(5, 5))

# Создаем фрейм для текстового поля и скроллбара
text_frame = tk.Frame(root)
text_frame.pack(pady=5, padx=15, fill=tk.BOTH, expand=True)

# Вертикальный скроллбар
scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Поле для ввода текста с привязанным скроллбаром
text_entry = tk.Text(text_frame, height=15, width=100, wrap=tk.WORD,
                    undo=True, font=large_font, yscrollcommand=scrollbar.set)
text_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Настройка скроллбара
scrollbar.config(command=text_entry.yview)

# Контекстное меню (ПКМ)
context_menu = tk.Menu(root, tearoff=0, font=large_font)
context_menu.add_command(label="Копировать", command=copy_text, accelerator="Ctrl+C")
context_menu.add_command(label="Вставить", command=paste_text, accelerator="Ctrl+V")
context_menu.add_command(label="Вырезать", command=cut_text, accelerator="Ctrl+X")
context_menu.add_separator()
context_menu.add_command(label="Очистить", command=lambda: text_entry.delete("1.0", tk.END))

# Привязка горячих клавиш
text_entry.bind("<Control-c>", copy_text)
text_entry.bind("<Control-v>", paste_text)
text_entry.bind("<Control-x>", cut_text)
text_entry.bind("<Button-3>", show_context_menu)  # Для Windows/Linux
text_entry.bind("<Button-2>", show_context_menu)  # Для Mac (если не работает ПКМ)

# Кнопка сохранения (увеличенная)
save_button = tk.Button(root, text="Проверить текст", command=check_text, font=button_font, height=1, width=20)
save_button.pack(pady=5)

root.mainloop()
#### ОКОННАЯ ПРОГРАММА ДЛЯ ПРОВЕРКИ ТЕКСТОВ
###### MAIN PROGRAM