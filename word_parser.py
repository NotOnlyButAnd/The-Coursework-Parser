##### ПЕРВЫЙ ВАРИАНТ ПАРСИНГА
# import zipfile
# import xml.etree.ElementTree as ElemT
##### ПЕРВЫЙ ВАРИАНТ ПАРСИНГА

##### ВТОРОЙ ВАРИАНТ ПАРСИНГА
##### pip install Spire.Doc
from spire.doc import *
# from spire.doc.common import *
##### ВТОРОЙ ВАРИАНТ ПАРСИНГА

import re
import os


#########################################################################
#### ПАРСИНГ Word-файлов в txt-формат (без изменений, весь текст подряд)
#########################################################################
def parse_word_files_to_txt(input_dir):
    count_of_proceed_files = 0
    # Рекурсивный проход по директории (входной) и обработка каждого из файлов
    # цикл по всем директориям в input_dir
    for root_dir, _, files in os.walk(input_dir):
        # цикл по всем файлам в текущей директории
        for filename in files:
            cur_file_dir = os.path.join(root_dir, filename)
            print(f'INPUT_DIR: {cur_file_dir}')

            ##### ПЕРВЫЙ ВАРИАНТ ПАРСИНГА
            # Обрабатываем только файлы .docx
            # if cur_file_dir.count('.docx') > 0:
            #     ##### ПЕРВЫЙ ВАРИАНТ ПАРСИНГА
            #     doc = zipfile.ZipFile(cur_file_dir).read('word/document.xml')
            #     root = ElemT.fromstring(doc)
            #
            #     # Подключаем пространство имен XML
            #     ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            #     body = root.find('w:body', ns)  # находим тег "body"
            #     p_sections = body.findall('w:p', ns)  # внутри тега body, находим все разделы абзацев
            #
            #     output_dir = cur_file_dir.replace('input', 'output').replace('.docx','.txt')
            #     print(f'OUTPUT_DIR: {output_dir}\n')
            #
            #     # Создание директории для output, если ее не существует (структура аналогично input)
            #     hier_output_dir = output_dir.split('\\')
            #     t_dir = ''
            #     for i in range(len(hier_output_dir)-1):
            #         t_dir += f'{hier_output_dir[i]}\\'
            #         try:
            #             os.mkdir(t_dir)
            #         except FileExistsError:
            #             continue
            #
            #     # Запись в файлы текстов после парсинга
            #     with open(output_dir, 'w', encoding='utf-8') as f:
            #         for p in p_sections:
            #             text_elems = p.findall('.//w:t', ns)
            #             f.write(str(''.join([t.text for t in text_elems])))
            #             f.write('\n')
            # else:
            #     print('\tFile type is not supported yet!\n')
            ##### ПЕРВЫЙ ВАРИАНТ ПАРСИНГА

            ##### ВТОРОЙ ВАРИАНТ ПАРСИНГА
            if cur_file_dir.count('.docx') > 0 or cur_file_dir.count('.doc') > 0:
                doc = Document()
                doc.LoadFromFile(str(cur_file_dir))
                text = doc.GetText()

                output_dir = cur_file_dir.replace('input', 'output')
                replacements = {'.docx': '.txt', '.doc': '.txt'}
                for original, replacement in replacements.items():
                    output_dir = output_dir.replace(original, replacement)
                print(f'OUTPUT_DIR: {output_dir}\n')

                # Создание директории для output, если ее не существует (структура аналогично input)
                hier_output_dir = output_dir.split('\\')
                t_dir = ''
                for i in range(len(hier_output_dir) - 1):
                    t_dir += f'{hier_output_dir[i]}\\'
                    try:
                        os.mkdir(t_dir)
                    except FileExistsError:
                        continue

                # Запись в файлы текстов после парсинга
                with open(output_dir, 'w', encoding='utf-8') as f:
                    f.write(text)

                count_of_proceed_files += 1
            else:
                print('\tFile type is not supported!\n')
            ##### ВТОРОЙ ВАРИАНТ ПАРСИНГА

    print(f'\n----------\nОбработка "docx -> txt" ({count_of_proceed_files} файлов) завершена...\n----------\n')


###########################################################################################
#### Анализ полученных текстовых файлов и выделение СЫРЫХ тем и содержаний (по возможности)
###########################################################################################
def set_themes_and_table_of_contents_raw(raw_text_dir):
    global parsed_files_properties
    file_idx = 0

    # Рекурсивный проход по директории (с txt-файлами) и обработка каждого из файлов
    # цикл по всем директориям в raw_text_dir
    for root_dir, _, files in os.walk(raw_text_dir):
        # цикл по всем файлам в текущей директории
        for filename in files:
            cur_file_dir = os.path.join(root_dir, filename)
            print(f'Рассматриваем txt-файл по пути: {cur_file_dir}')
            parsed_files_properties[f'file{file_idx}'] = {}
            parsed_files_properties[f'file{file_idx}']['path_to_file'] = cur_file_dir

            with open(cur_file_dir, 'r', encoding='utf-8') as f:
                ###### Построчное считывание
                # while True:
                #     # считываем строку
                #     line = f.readline()
                #     # прерываем цикл, если строка пустая
                #     if not line:
                #         break
                #     print(line.strip())
                ###### Построчное считывание

                ###### Считывание всех строк в список
                text_file = f.readlines()
                text_file_lower = [item.lower().strip().replace('\t', '').replace('\n', '') for item in text_file]
                good_flag = True
                #print(text_file_lower)
                # print()
                #### Получаем название работы
                #### (если есть между строками "КУРСОВАЯ РАБОТА" и ("РАБОТУ ВЫПОЛНИЛ" или "ВЫПОЛНИЛ"); и если меньше 200 строк от начала)
                try:
                    index_of_kurs_rab = text_file_lower.index('курсовая работа')
                except ValueError:
                    index_of_kurs_rab = -1

                try:
                    index_of_vkr = text_file_lower.index('выпускная квалификационная работа бакалавра')
                except ValueError:
                    index_of_vkr = -1

                index_of_kurs_rab = index_of_kurs_rab if index_of_kurs_rab != -1 else index_of_vkr


                index_of_rab_vyp = -1
                for i in range(len(text_file_lower)):
                    if text_file_lower[i].count('работу выполнил') > 0:
                        index_of_rab_vyp = i
                        break
                    if text_file_lower[i].count('выполнил') > 0:
                        index_of_rab_vyp = i
                        break
                    if i >= 200:
                        break

                if index_of_kurs_rab != -1 and index_of_rab_vyp != -1:
                    parsed_files_properties[f'file{file_idx}']['theme_raw'] = {}
                    parsed_files_properties[f'file{file_idx}']['theme_raw']['index_start'] = index_of_kurs_rab + 1
                    parsed_files_properties[f'file{file_idx}']['theme_raw']['index_end'] = index_of_rab_vyp - 1
                    parsed_files_properties[f'file{file_idx}']['theme_raw']['text'] = text_file[
                                                                                      index_of_kurs_rab + 1: index_of_rab_vyp]
                else:
                    parsed_files_properties[f'file{file_idx}']['theme_raw'] = {}
                    good_flag = False
                    # if index_of_kurs_rab == -1:
                    #     print('Здесь нет "курсовая работа"!')
                    # if index_of_rab_vyp == -1:
                    #     print('Здесь нет "работу выполнил"!')

                ##### Получение нормального текста темы работы. Удаляем лишние пустые строки, объединяем все оставшиеся строки в 1.
                theme_result = ""
                try:
                    for theme_line in parsed_files_properties[f'file{file_idx}']['theme_raw']['text']:
                        clear_theme_line = theme_line.strip()

                        if clear_theme_line != '':
                            theme_result += re.sub(' +', ' ', clear_theme_line) + ' '
                except KeyError:
                    theme_result = 'NO THEME!'
                parsed_files_properties[f'file{file_idx}']['theme_clear'] = theme_result
                # print(f'file{file_idx} theme: {theme_result}')

                #### Получаем Оглавление - "подтемы" темы курсовой
                #### (если есть - находится между строками ("ОГЛАВЛЕНИЕ" или "СОДЕРЖАНИЕ") и вторым следующим словом "ВВЕДЕНИЕ" без цифр)
                try:
                    index_of_soderzh = text_file_lower.index('содержание')
                except ValueError:
                    index_of_soderzh = -1
                try:
                    index_of_oglavl = text_file_lower.index('оглавление')
                except ValueError:
                    index_of_oglavl = -1
                try:
                    index_of_vvedenye = text_file_lower.index('введение')
                except ValueError:
                    index_of_vvedenye = -1

                index_of_soderzh_main = -1
                if (index_of_soderzh != -1 or index_of_oglavl != -1) and index_of_vvedenye != -1:
                    index_of_soderzh_main = index_of_soderzh if index_of_soderzh != -1 else index_of_oglavl
                    if index_of_vvedenye - index_of_soderzh_main >= 4:
                        parsed_files_properties[f'file{file_idx}']['table_of_contents_raw'] = {}
                        parsed_files_properties[f'file{file_idx}']['table_of_contents_raw'][
                            'index_start'] = index_of_soderzh_main
                        parsed_files_properties[f'file{file_idx}']['table_of_contents_raw'][
                            'index_end'] = index_of_vvedenye - 1
                        parsed_files_properties[f'file{file_idx}']['table_of_contents_raw']['text'] = text_file[
                                                                                                      index_of_soderzh_main: index_of_vvedenye]
                    else:
                        parsed_files_properties[f'file{file_idx}']['table_of_contents_raw'] = {}
                        good_flag = False
                        # print('Здесь НЕКОРРЕКТНО оформлено содержание и заголовок введения!')
                if index_of_soderzh_main == -1:
                    parsed_files_properties[f'file{file_idx}']['table_of_contents_raw'] = {}
                    good_flag = False
                    # print('Здесь нет ("содержание" или "оглавление") и "введение"!')

                ##### Получение чистых названий глав и подглав из содержания.

                table_of_contents_result = []
                try:
                    for toc_line in parsed_files_properties[f'file{file_idx}']['table_of_contents_raw']['text']:
                        clear_toc_line = toc_line.strip()
                        # Замена точек
                        clear_toc_line = re.sub('(\\.\\.)+', ' ', clear_toc_line)
                        # Замена символов из списка
                        replacements = {'…': ' ', '\t': ' '}
                        for original, replacement in replacements.items():
                            clear_toc_line = clear_toc_line.replace(original, replacement)
                        # Замена нескольких пробелов одним
                        clear_toc_line = re.sub(' +', ' ', clear_toc_line)
                        # Отсечение номеров страниц (если есть) в конце строк
                        if clear_toc_line != '':
                            is_digit_in_end = True if clear_toc_line[-1].isdigit() else False

                            while is_digit_in_end:
                                clear_toc_line = clear_toc_line[0:-1]
                                is_digit_in_end = True if clear_toc_line[-1].isdigit() else False

                            # ### UPD: удаляем все главы без цифр в начале, помимо "введение" и "заключение"
                            # pattern_rus_letters = re.compile('^[а-я]*')
                            # clear_toc_line_regexped = pattern_rus_letters.findall(clear_toc_line.lower())
                            #
                            # if clear_toc_line_regexped[0] == 'введение' or clear_toc_line_regexped[0] == 'заключение' or clear_toc_line[0].isdigit():
                            #     table_of_contents_result.append(clear_toc_line)
                            table_of_contents_result.append(clear_toc_line)
                except KeyError:
                    table_of_contents_result = []
                parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'] = table_of_contents_result
                # print(f'file{file_idx} TABLE OF CONTENTS: {table_of_contents_result}')

                #### Создаем цифровое представление иерархии (в массиве)
                table_of_contents_hierarchy = []
                try:
                    curr_not_numbered_chapter_index = 0
                    curr_not_numbered_chapter_subindex = 0
                    for toc_clr_line in parsed_files_properties[f'file{file_idx}']['table_of_contents_clear']:
                        # Если первый символ текущей главы не цифра - то добавляем индекс для ненумерованной главы
                        if not toc_clr_line[0].isdigit():
                            table_of_contents_hierarchy.append(
                                f'{curr_not_numbered_chapter_index}.{curr_not_numbered_chapter_subindex}')
                            curr_not_numbered_chapter_subindex += 1
                        else:
                            # считываем все цифры с точками, пока не закончатся
                            t_str = ''
                            for symbol in toc_clr_line:
                                if symbol.isdigit() or symbol == '.':
                                    t_str += symbol
                                else:
                                    table_of_contents_hierarchy.append(t_str if t_str[-1] != '.' else t_str[0:-1])
                                    break
                except KeyError:
                    table_of_contents_hierarchy = []
                #print(f'    file{file_idx} TABLE OF CONTENTS HIERARCHY before fix: {table_of_contents_hierarchy}')

                # tmp_toc_hier = table_of_contents_hierarchy.copy()
                #### Проверяем, нет ли "разделенных" текстов глав (когда текст нумерованной главы разделен по строкам) и исправляем
                # print(f'--- file{file_idx} TABLE OF CONTENTS : {parsed_files_properties[f'file{file_idx}']['table_of_contents_clear']}')
                # print(f'--- file{file_idx} TABLE OF CONTENTS HIERARCHY before  fix: {table_of_contents_hierarchy}')
                for i in range(1, len(table_of_contents_hierarchy)):
                    if table_of_contents_hierarchy[i][0] == '0' and table_of_contents_hierarchy[i - 1][0] != '0':
                        # Если нашли разделенную строку, надо дойти до конца списка глав. Т.к. если после этого будут только
                        # главы "0"-го уровня, то это конец работы, а не разделенная строка
                        is_end_chapters = True
                        for j in range(i, len(table_of_contents_hierarchy)):
                            if table_of_contents_hierarchy[j][0] != '0':
                                is_end_chapters = False
                                break
                        # Если это все-таки разделенная строка, надо заменить текущую цифру нулевого уровня на предыдущую
                        # главу - чтобы потом эти две части склеить в одну
                        if not is_end_chapters:
                            table_of_contents_hierarchy[i] = table_of_contents_hierarchy[i - 1]
                # print(f'--- file{file_idx} TABLE OF CONTENTS HIERARCHY after  fix: {table_of_contents_hierarchy}')
                # if set(tmp_toc_hier) != set(table_of_contents_hierarchy):
                #     print('------ NOT SAME!!!')

                #### Объединяем разделенные строки в одну В ОБОИХ МАССИВАХ (если есть)
                if len(set(table_of_contents_hierarchy)) != len(table_of_contents_hierarchy):
                    # print(f'------ NOT SAME!!! - {table_of_contents_hierarchy}')
                    t_len = len(table_of_contents_hierarchy)
                    for i in range(1, t_len):
                        # print(f'-{i}- t_len: {t_len}')
                        if i >= t_len:
                            break
                        if table_of_contents_hierarchy[i] == table_of_contents_hierarchy[i - 1]:
                            del table_of_contents_hierarchy[i]
                            parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'][i - 1] += ' ' + \
                                                                      parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'][i]
                            del parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'][i]
                            t_len -= 1
                    # print(f'--- file{file_idx} TABLE OF CONTENTS HIERARCHY after  del: {table_of_contents_hierarchy}')
                    # print(f'--- file{file_idx} TABLE OF CONTENTS clear after  del: {parsed_files_properties[f'file{file_idx}']['table_of_contents_clear']}')
                parsed_files_properties[f'file{file_idx}']['table_of_contents_hier'] = table_of_contents_hierarchy

                ### UPD: удаляем все главы без цифр в начале, помимо "введение" и "заключение"
                #### НАДО также сохранить главу, которая идет после "заключение" - чтобы было удобно вытащить часть текста заключения
                # print(f'table_of_contents_clear BEFORE: {parsed_files_properties[f'file{file_idx}']['table_of_contents_clear']}')
                # print(
                #     f'table_of_contents_hier BEFORE: {parsed_files_properties[f'file{file_idx}']['table_of_contents_hier']}')
                tmp_cleared_toc = []
                chapter_after_zakluchenie = ''
                tmp_cleared_hier = []
                for k in range(len(parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'])):
                    pattern_rus_letters = re.compile('^[а-я]*')
                    clear_line_regexped = pattern_rus_letters.findall(parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'][k].lower())

                    if clear_line_regexped[0] == 'введение' or clear_line_regexped[0] == 'заключение' or parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'][k][0].isdigit():
                        tmp_cleared_toc.append(parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'][k])
                        tmp_cleared_hier.append(parsed_files_properties[f'file{file_idx}']['table_of_contents_hier'][k])
                        # Если добавляем заключение, то для построения текстов людей запоминаем главу, которая идет после заключения (если есть)
                        if clear_line_regexped[0] == 'заключение' and parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'][k+1]:
                            chapter_after_zakluchenie = parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'][k+1]
                parsed_files_properties[f'file{file_idx}']['table_of_contents_clear'] = tmp_cleared_toc
                parsed_files_properties[f'file{file_idx}']['table_of_contents_hier'] = tmp_cleared_hier
                parsed_files_properties[f'file{file_idx}']['table_of_contents_clear_for_people_text'] = tmp_cleared_toc.copy()
                if chapter_after_zakluchenie != '':
                    parsed_files_properties[f'file{file_idx}']['table_of_contents_clear_for_people_text'].append(chapter_after_zakluchenie)
                # print(f'table_of_contents_clear after: {parsed_files_properties[f'file{file_idx}']['table_of_contents_clear']}')
                # print(
                #     f'table_of_contents_hier BEFORE: {parsed_files_properties[f'file{file_idx}']['table_of_contents_hier']}')

                parsed_files_properties[f'file{file_idx}']['is_good_doc'] = 1 if good_flag else 0

            file_idx += 1
            # print()


###########################################################################################
#### Получаем наборы названий глав для построения запросов
###########################################################################################
def set_queries_data_raw():
    global parsed_files_properties
    for item, value in parsed_files_properties.items():
        # НЕ обрабатываем тексты, у которых не определена тема или нет содержания
        if value['theme_clear'] == 'NO THEME!' or value['theme_clear'] == '' or value['table_of_contents_hier'] == []:
            continue
        # "Тема работы; Глава; Подглава; Под-подглава; ..."
        result_queries = []
        result_queries_indexes = []
        for i in range(len(value['table_of_contents_hier'])):
            t_hier_arr = value['table_of_contents_hier'][i].split('.')
            # Если это нулевой уровень или уровень без подглав - добавляем в список "Тема работы; Глава;"
            if t_hier_arr[0] == '0' or len(t_hier_arr) == 1:
                result_queries.append([value['theme_clear'], value['table_of_contents_clear'][i]])
                result_queries_indexes.append([i])
            # В другом случае, добавляем "Тема работы; Глава; Подглава; Под-подглава; ..."
            else:
                t_parts = [value['theme_clear']]
                t_parts_indexes = []
                t_str = ''
                for indx in t_hier_arr:
                    t_str += indx
                    t_parts.append(value['table_of_contents_clear'][value['table_of_contents_hier'].index(t_str)])
                    t_parts_indexes.append(value['table_of_contents_hier'].index(t_str))
                    t_str += '.'
                result_queries.append(t_parts)
                result_queries_indexes.append(t_parts_indexes)
        value['queries'] = result_queries
        value['queries_indexes_from_tocc'] = result_queries_indexes
        # print(f'{item}: result_queries = {result_queries}\n       result_queries_indexes = {result_queries_indexes}')


###########################################################################################
#### Вывод в консоль данных из распарсенного словаря
###########################################################################################
def print_parsed_dictionary(subitems=None, perfect_or_bad=None):
    global parsed_files_properties
    ##### Вывод полученных данных по каждому из файлов и подсчет кол-ва идеально подходящих нам файлов
    ##### (чтобы была тема курсовой и четко определенное содержание)
    if subitems is None:
        subitems = []
    if not subitems:
        count_of_good_docs = 0
        count_of_docs = 0
        for item, value in parsed_files_properties.items():
            ### Проверка, что выводим: только плохие, только хорошие, или все записи
            if perfect_or_bad is not None:
                if perfect_or_bad == 'perfect':
                    if value['is_good_doc'] != 1 or value['is_all_indexes_of_chapters_founded'] != 1:
                        continue
                elif perfect_or_bad == 'bad':
                    if value['is_good_doc'] == 1 and value['is_all_indexes_of_chapters_founded'] == 1:
                        continue
                else:
                    print('Not allowed parameter "perfect_or_bad"!')
                    break
            print(item)
            for inner_item, inner_value in value.items():
                print(f'\t{inner_item}: {inner_value}')
                if inner_item == 'is_good_doc' and inner_value == 1:
                    count_of_good_docs += 1
            print()
            count_of_docs += 1

        print(f'\nКол-во обработанных файлов: {count_of_docs}')
    else:
        for item, value in parsed_files_properties.items():
            ### Проверка, что выводим: только плохие, только хорошие, или все записи
            if perfect_or_bad is not None:
                if perfect_or_bad == 'perfect':
                    if value['is_good_doc'] != 1 or value['is_all_indexes_of_chapters_founded'] != 1:
                        continue
                elif perfect_or_bad == 'bad':
                    if value['is_good_doc'] == 1 and value['is_all_indexes_of_chapters_founded'] == 1:
                        continue
                else:
                    print('Not allowed parameter "perfect_or_bad"!')
                    break
            print(item)
            for subitem in subitems:
                try:
                    if isinstance(value[subitem], list):
                        print(f'\t{subitem}: ')
                        for j in range(len(value[subitem])):
                            print(f'\t\t{j}: {value[subitem][j]}')
                    else:
                        print(f'\t{subitem}: {value[subitem]}')
                except KeyError:
                    print(f'--- No such key {subitem}!')
            print()


### Получение индексов глав текстов ЛЮДЕЙ для каждой из глав содержания
def set_indexes_of_chapters_from_text():
    global parsed_files_properties
    for item, value in parsed_files_properties.items():
        curr_chapter_index = 0
        indexes_of_chapters = []
        # is_first_match = True

        if value['table_of_contents_clear_for_people_text']:
            # Очищаем текущую строку содержания от шелухи
            #### TODO: Возможно, можно оптимизировать регулярку для выбора всех букв и цифр
            pattern_rus_letters_and_spaces = re.compile('[а-я0-9]*')
            clear_toc_line_regexped = ''.join(list(filter(None, pattern_rus_letters_and_spaces.findall(value['table_of_contents_clear_for_people_text'][curr_chapter_index].lower()))))

            with open(value['path_to_file'], 'r', encoding='utf-8') as f:
                ###### Считывание всех строк файла в список
                text_file = f.readlines()
                text_file_lower = [f_str.lower().strip().replace('\t', '').replace('\n', '') for f_str in text_file]

                # print()
                # print(value['path_to_file'])

                # Проходимся по всем строкам файла и ищем совпадения с текущим названием главы (очищаем также)
                for i in range(len(text_file_lower)):
                    curr_file_line_regexped = ''.join(list(filter(None, pattern_rus_letters_and_spaces.findall(text_file_lower[i].lower()))))
                    # if 305 <= i <= 311:
                        # print(f'curr_file_line_regexped: {curr_file_line_regexped}')
                        # print('---!!!---')
                        # print(f'clear_toc_line_regexped: {clear_toc_line_regexped}')
                    if curr_file_line_regexped == clear_toc_line_regexped:
                        indexes_of_chapters.append(i)
                        curr_chapter_index += 1
                        if curr_chapter_index >= len(value['table_of_contents_clear_for_people_text']):
                            break
                        else:
                            clear_toc_line_regexped = ''.join(list(filter(None, pattern_rus_letters_and_spaces.findall(value['table_of_contents_clear_for_people_text'][curr_chapter_index].lower()))))

        value['indexes_of_chapters_from_text'] = indexes_of_chapters
        value['is_all_indexes_of_chapters_founded'] = 1 if len(indexes_of_chapters) == len(value['table_of_contents_clear_for_people_text']) else 0


#### Структура выходных файлов с текстами людей:
# кол-во слов в тексте
# тема работы
# глава 0 уровня
# глава 1 уровня [если есть]
# глава 2 уровня [если есть]
# ...
# глава n уровня [если есть]
# "----------"
# ТЕКСТ ...
def make_people_texts(people_text_dir):
    global parsed_files_properties
    for item, value in parsed_files_properties.items():
        # НЕ обрабатываем тексты, у которых не определена тема или нет содержания
        if value['theme_clear'] == 'NO THEME!' or value['theme_clear'] == '' or value['table_of_contents_hier'] == []:
            continue
        if value['indexes_of_chapters_from_text']:
            with open(value['path_to_file'], 'r', encoding='utf-8') as f_r:
                text_file = f_r.readlines()
                for i in range(len(value['indexes_of_chapters_from_text'])-1):
                    curr_people_text = [value['theme_clear']]
                    for chapter_index in value['queries_indexes_from_tocc'][i]:
                        curr_people_text.append(f'\n{value['table_of_contents_clear'][chapter_index]}')
                    curr_people_text.append('\n----------')
                    cnt_of_words = 0
                    for line in text_file[value['indexes_of_chapters_from_text'][i]+1:value['indexes_of_chapters_from_text'][i+1]]:
                        stripped_line = line.strip()
                        if stripped_line != '':
                            cnt_of_words += len(stripped_line.split())
                            curr_people_text.append(f'\n{stripped_line}')
                    curr_people_text = [f'{cnt_of_words}\n'] + curr_people_text

                    if cnt_of_words >= 150:
                        with open(f'{people_text_dir}\\{item}_{f'0{i}' if i<10 else i}.txt', 'w', encoding='utf-8') as f_w:
                            f_w.writelines(curr_people_text)


# TODO: Доработать - пока просто сырой вывод в текстовые файлы запросов
# TODO: Также при отправке запросов на LLM надо посылать их все в одной теме в рамках одного контекста
#       Чтобы было более точное написание глав и подглав относительно друг друга
def make_queries_for_llm_from_people_text(people_text_dir, llm_text_dir):
    ### Пробуем составлять запросы для LLM (одиночные)
    welcome_str = 'Привет! Я студент университета и я пишу курсовую работу по теме: '
    theme_str = ''
    chapter_str_1 = 'Помоги мне написать текст главы "'
    chapter_str_2 = '"'
    chapter_name_str = ''
    requirement_str_1 = '\nСделай так, чтобы текст содержал от '
    requirement_str_2 = ' до '
    requirement_str_3 = ''' слов. 
        Можешь использовать нумерованные списки, разделять текст на абзацы по смыслу.
        Можешь предлагать места для вставки рисунков и помечать их надписями такого типа: "рисунок n - название рисунка".
        Также можешь по необходимости вставлять места для формул (помечай их так: "формула n - название формулы"), но не приводи сами формулы в текстовом формате.
        '''
    queries_counter = 0

    # Рекурсивный проход по директории (входной) и обработка каждого из файлов
    # цикл по всем директориям в input_dir
    for root_dir, _, files in os.walk(people_text_dir):
        # цикл по всем файлам в текущей директории
        for filename in files:
            cur_file_dir = os.path.join(root_dir, filename)
            # print(f'Current file: {cur_file_dir}')

            with open(cur_file_dir, 'r', encoding='utf-8') as f_r:
                text_file = f_r.readlines()

                # Делаем количество слов от "кол-во слов человека, округленное в меньшую сторону по модулю 50"
                #                        до "кол-во слов человека, округленное в большую сторону по модулю 50"
                count_of_words = int(text_file[0])
                min_approx_count_of_words = count_of_words - count_of_words % 50
                max_approx_count_of_words = count_of_words + (50 - count_of_words % 50)

                theme_str = text_file[1]

                i = 2
                chapter_name_str = ''
                curr_chapter = text_file[i].strip()
                # print(curr_chapter)
                while curr_chapter != '----------':
                    chapter_name_str += f'{curr_chapter}; '
                    i += 1
                    curr_chapter = text_file[i].strip()
                    # print(f'in cycle: {curr_chapter}')

                curr_result_query = welcome_str + theme_str + chapter_str_1 + chapter_name_str + chapter_str_2 + \
                                    requirement_str_1 + str(min_approx_count_of_words) + \
                                    requirement_str_2 + str(max_approx_count_of_words) + \
                                    requirement_str_3
                queries_counter += 1

                with open(f'{llm_text_dir}\\{filename}', 'w', encoding='utf-8') as f_w:
                    f_w.write(curr_result_query.replace('        ', ''))


    print(f'\nИТОГО получилось {queries_counter} запросов (т.е. столько текстов от нейронки будет)')


#######################
########## MAIN PROGRAM
#######################
### Вызываем функцию, которая будет переводить документы doc[x] в txt формат
g_input_dir = 'data\\input'   # Директория с входными doc[x]-файлами
parse_word_files_to_txt(g_input_dir)

### Вызываем функцию, которая из txt файлов соберет словарь с путями к файлам, темами и оглавлениями (сырыми) и т.д.
g_raw_text_dir = 'data\\output'  # Директория с полученными txt-файлами
parsed_files_properties = {}
set_themes_and_table_of_contents_raw(g_raw_text_dir)

### Вызываем функцию, которая добавит в словарь сырые списки с данными для запросов к LLM
set_queries_data_raw()

### Вызываем функцию поиска индексов строк файлов, содержащих заголовки глав из содержания
set_indexes_of_chapters_from_text()

g_people_text_dir = 'data\\output_people' # Директория с человеческими текстовыми файлами ПО ТЕМАМ
make_people_texts(g_people_text_dir)

# Вывод словаря в консоль
print_parsed_dictionary()

# print_parsed_dictionary(perfect_or_bad='perfect')
# print_parsed_dictionary(perfect_or_bad='bad')
# print_parsed_dictionary(subitems=['path_to_file', 'theme_clear', 'table_of_contents_clear_for_people_text', 'queries', 'indexes_of_chapters_from_text'], perfect_or_bad='bad')

# print_parsed_dictionary(['path_to_file', 'table_of_contents_clear', 'table_of_contents_clear_for_people_text'])

g_llm_text_dir = 'data\\output_llm'
make_queries_for_llm_from_people_text(g_people_text_dir, g_llm_text_dir)

# TODO: ОБЩИЕ МОМЕНТЫ
#   1) Провести проверку текстов людей на нормальность (всех!)
#   2) Подумать: как исключать текстовые коды программ из текстов людей: программно / вручную / просто удалять текст полностью (+ нейро-текст)
#   3) Сделать нормальную обработку текстов ВКР: чтобы делались нормальные запросы к LLM
