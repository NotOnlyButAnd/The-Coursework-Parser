# Создадим БД с текстами для удобного анализва текстов
import os
import sqlite3


### 'Глобальные' переменные - название БД, пути к файлам с текстами
g_db_name = 'people_and_llm_texts.db'
g_people_text_dir = 'data\\ready_texts НОРМАЛЬНЫЕ\\People'
g_yandex_text_dir = 'data\\ready_texts НОРМАЛЬНЫЕ\\YandexGPT'
g_deepseek_text_dir = 'data\\ready_texts НОРМАЛЬНЫЕ\\DeepSeek'
### 'Глобальные' переменные - название БД, пути к файлам с текстами


### Функции для создания и заполнения БД
def initialize_database(db_name: str = 'people_and_llm_texts.db') -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Создаем таблицу для текстов LLM и людей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS text (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        source_type TEXT NOT NULL,
        topic       TEXT NOT NULL,
        subtopic    TEXT NOT NULL,
        content     TEXT NOT NULL,
        filename    TEXT NOT NULL,
        filepath    TEXT NOT NULL,
        UNIQUE(filename, source_type)
    )
    ''')

    # Создаем таблицу для характеристик текста
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS text_characteristic (
        id                          INTEGER PRIMARY KEY AUTOINCREMENT,
        text_id                     INTEGER NOT NULL,
        count_words                 INTEGER,
        count_sentences             INTEGER,
        count_syllables             INTEGER,
        flesch_reading_index        REAL,
        avg_punct_by_sentences      REAL,
        avg_words_by_sentences      REAL,
        count_words_by_sentences    TEXT,   /* список целых чисел в формате строки (json.dumps) */
        count_punct_by_sentences    TEXT,   /* список целых чисел в формате строки (json.dumps)*/
        words_by_sentences          TEXT,   /* список списков строк в формате строки (json.dumps)*/
        content_by_sentences        TEXT,   /* список строк в формате строки (json.dumps)*/
        morph_characteristics       TEXT,   /* объект в формате строки (json.dumps)*/
        count_unique_words          INTEGER,
        ratio_unique_words          REAL,
        FOREIGN KEY (text_id) REFERENCES text(id),
        UNIQUE(text_id)
    )
    ''')

    conn.commit()
    return conn

def add_texts_to_db():
    print(f"Начинаем добавление текстов в БД...")
    conn = initialize_database(g_db_name)
    cursor = conn.cursor()

    # t_cntr = 0
    # Проходимся по текстам людей
    # цикл по всем директориям в g_people_text_dir
    for root_dir, _, files in os.walk(g_people_text_dir):
        # цикл по всем файлам в текущей директории
        for filename in files:
            # if t_cntr > 5:
            #     break
            # t_cntr += 1

            cur_file_dir = os.path.join(root_dir, filename)

            # Добавляем человеческий текст в таблицу
            with open(cur_file_dir, 'r', encoding='utf-8') as f:
                text_by_lines = f.readlines()
                index_of_splitter = text_by_lines.index('----------\n')
                # word_count = text_by_lines[0].strip()     # DEPRECATED
                topic = text_by_lines[1]
                subtopic = ''.join(text_by_lines[2:index_of_splitter])
                content = ''.join(text_by_lines[index_of_splitter + 1:])
                try:
                    cursor.execute('''
                                INSERT INTO text (source_type, topic, subtopic, content, filename, filepath)
                                VALUES (?, ?, ?, ?, ?, ?)
                                ''', ('people', topic, subtopic, content, filename, root_dir))
                    conn.commit()
                except sqlite3.IntegrityError:
                    print(f"Файл {filename} для текстов людей уже записан в базе данных")
                except Exception as e:
                    print(f"Ошибка при сохранении файла людей {filename}: {e}")

                # Добавляем текст DeepSeek в таблицу
                with open(g_deepseek_text_dir + f'\\{filename}', 'r', encoding='utf-8') as fd:
                    file_text_d = ''.join(fd.readlines())
                    try:
                        cursor.execute('''
                                            INSERT INTO text (source_type, topic, subtopic, content, filename, filepath)
                                            VALUES (?, ?, ?, ?, ?, ?)
                                            ''', ('deepseek', topic, subtopic, file_text_d, filename, g_deepseek_text_dir))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        print(f"Файл {filename} для модели deepseek уже записан в базе данных")
                    except Exception as e:
                        print(f"Ошибка при сохранении файла DeepSeek {filename}: {e}")

                # Добавляем текст YandexGPT в таблицу
                with open(g_yandex_text_dir + f'\\{filename}', 'r', encoding='utf-8') as fy:
                    file_text_y = ''.join(fy.readlines())
                    try:
                        cursor.execute('''
                                                    INSERT INTO text (source_type, topic, subtopic, content, filename, filepath)
                                                    VALUES (?, ?, ?, ?, ?, ?)
                                                    ''',
                                       ('yandexgpt', topic, subtopic, file_text_y, filename, g_yandex_text_dir))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        print(f"Файл {filename} для модели yandexgpt уже записан в базе данных")
                    except Exception as e:
                        print(f"Ошибка при сохранении файла YandexGPT {filename}: {e}")

    conn.close()
    print(f"Добавление текстов в БД завершено!")
### Функции для создания и заполнения БД


### Функции для запросов к БД
def truncate_some_table(table_name):
    conn = initialize_database(g_db_name)
    cursor = conn.cursor()
    cursor.execute(f'''delete from {table_name}''')
    conn.commit()
    conn.close()

def drop_some_table(table_name):
    conn = initialize_database(g_db_name)
    cursor = conn.cursor()
    cursor.execute(f'''drop table {table_name}''')
    conn.commit()
    conn.close()

def select_count_of_texts_by_source_type():
    conn = initialize_database(g_db_name)
    cursor = conn.cursor()
    cursor.execute('''select count(1), source_type from text group by source_type order by source_type''')
    print("\nCount of texts:")
    output = cursor.fetchall()
    for row in output:
        print(row)
        # print(type(row[1]))
    conn.close()

def select_all_data_from_some_table(table_name, limit_expr=''):
    conn = initialize_database(g_db_name)
    cursor = conn.cursor()
    cursor.execute(f'''select * from {table_name} {limit_expr}''')
    print(f"\nAll the data of {table_name} table ({limit_expr}):")
    output = cursor.fetchall()
    for row in output:
        print(row)
    conn.close()

def select_some_fields_from_some_table(table_name, limit_expr='', fields='*', order_by_expr=''):
    conn = initialize_database(g_db_name)
    cursor = conn.cursor()

    if order_by_expr != '':
        order_by_expr = 'order by ' + order_by_expr

    cursor.execute(f'''select {fields} from {table_name} {order_by_expr} {limit_expr}''')

    print(f"\nFields '{fields}' of {table_name} table ({limit_expr}):")
    output = cursor.fetchall()
    for row in output:
        print(row)

    conn.close()
### Функции для запросов к БД


### Main Program
# initialize_database(g_db_name)

# drop_some_table('text_characteristic')

# truncate_some_table('text')
# truncate_some_table('text_characteristic')

# add_texts_to_db()

# select_all_data_from_some_table('text', 'limit 15')
# select_all_data_from_some_table('text_characteristic', 'limit 15')

select_count_of_texts_by_source_type()

# select_some_fields_from_some_table('text_characteristic', limit_expr='', fields='id, text_id, count_words', order_by_expr='text_id')

## Запрос к БД
conn = initialize_database(g_db_name)
cursor = conn.cursor()

###### ЗАПРОС НА ПОЛЯ
# c_fields = '''
#  t.id as t_id, t.filename, t.topic, t.subtopic,
#  t_c.*
# '''
# cursor.execute(f'''
#     select
#         {c_fields}
#     from
#         text t
#         join text_characteristic t_c on t.id = t_c.text_id
#     order by
#         text_id
# ''')

####### ЗАПРОС НА АГРЕГАЦИЮ
c_fields = '''
min(t_c.count_words), max(t_c.count_words), source_type
'''
cursor.execute(f'''
    select
        {c_fields}
    from
        text t
        join text_characteristic t_c on t.id = t_c.text_id
    group by source_type
    order by source_type
''')

print(f"\nData of your query:")
print(c_fields)
output = cursor.fetchall()
for row in output:
    print(row)

conn.close()

## Запрос к БД
### Main Program

### Нормализуем индекс удобочитаемости флеша
# def normalize_to_100(data):
#     if not data:
#         return []
#
#     # Извлекаем все значения из словарей
#     values = [list(item.values())[0] for item in data]
#
#     min_original = min(values)
#     max_original = max(values)
#
#     # Добавляем небольшой отступ от 0 и 100 на 4% и 3 % соответственно
#     diff_max_min = max_original - min_original
#
#     min_original -= diff_max_min / 100 * 4
#     max_original += diff_max_min / 100 * 3
#
#     # Если все значения одинаковые, нормализуем их к 50
#     if min_original == max_original:
#         return [{k: 50.0} for item in data for k in item.keys()]
#
#     normalized_data = []
#     for item in data:
#         identifier, value = list(item.items())[0]  # Получаем ключ и значение
#         normalized_value = ((value - min_original) / (max_original - min_original)) * 100
#         normalized_data.append({identifier: normalized_value})
#
#     return normalized_data
#
#
# def find_min_max_objects(data):
#     if not data:
#         return None, None
#
#     # Извлекаем первые (и единственные) значения из каждого словаря
#     values = [list(item.values())[0] for item in data]
#     min_val = min(values)
#     max_val = max(values)
#
#     # Ищем все объекты с min и max значениями
#     min_objects = [item for item in data if list(item.values())[0] == min_val]
#     max_objects = [item for item in data if list(item.values())[0] == max_val]
#
#     return min_objects, max_objects
#
# #Получаем индексы удобочитаемости из БД
# t_flesch_data = []
# conn = initialize_database(g_db_name)
# cursor = conn.cursor()
#
# c_fields = '''
# t_c.id, t_c.flesch_reading_index
# '''
# cursor.execute(f'''
#     select
#         {c_fields}
#     from
#         text_characteristic t_c
#     order by
#         t_c.id
# ''')
#
# print(f"\nData of your query:")
# print(c_fields)
# output = cursor.fetchall()
# for row in output:
#     t_flesch_data.append({f"{row[0]}": row[1]})
#
# conn.close()
#
# # Нормализуем значения
# print(t_flesch_data)
# normalized_flesch_data = normalize_to_100(t_flesch_data)
# print(normalized_flesch_data)
#
# # Проверяем минимумы и максимумы из нормализованных объектов
# # min_objs, max_objs = find_min_max_objects(normalized_flesch_data)
# #
# # print("Объекты с минимальным значением:")
# # for obj in min_objs:
# #     print(obj)
# #
# # print("\nОбъекты с максимальным значением:")
# # for obj in max_objs:
# #     print(obj)
#
# # Записываем нормализованные индексы в БД
# conn = initialize_database(g_db_name)
# cursor = conn.cursor()
# for o in normalized_flesch_data:
#     value = list(o.values())[0]  # Получаем первое (и единственное) значение
#     key = list(o.keys())[0]  # Получаем первый (и единственный) ключ
#     print(f"Идентификатор: {key}, Значение: {value}")
#     cursor.execute(f'''
#         update text_characteristic
#         set flesch_reading_index = {value}
#         where id = {key}
#     ''')
# conn.commit()
# conn.close()
