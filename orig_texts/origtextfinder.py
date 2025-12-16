import re
import json
from search_utils import get_dicts_with_urls, get_google_results, get_list_of_urls, get_tavily_results, get_yandex_results, check_url, parse_article
from tqdm import tqdm

class OrigTextFinder:
    def __init__(self):
        pass

    def get_quotes(self, txt_path, qm_path, re_path, rewqm_path):

        '''
        Генерирует цитаты на основе текстов по регулярным выражениям.
        На вход принимает json-файл с текстами, файл с маркерами цитат, регулярные выражения бкз маркерв цитат, регулярные выражения с маркерами цитат.
        Результат работы метода - обновлённый файл с текстами.

        '''

        with open(txt_path, 'r', encoding='utf-8') as f:
            debunk = json.load(f)

        with open(qm_path, 'r', encoding='utf-8') as f:
            quote_markers = []
            for line in f:
                quote_markers.append(line.rstrip())

        regvyrs = {}

        with open(re_path, 'r', encoding='utf-8') as f:
            regvyrs['wowords'] = []
            for line in f:
                regvyrs['wowords'].append(line.rstrip())

        with open(rewqm_path, 'r', encoding='utf-8') as f:
            regvyrs['wwords'] = []
            for line in f:
                regvyrs['wwords'].append(line.rstrip())


        for deb_text in debunk:
            txt = deb_text['text']
            reg_found = False

            for marker in quote_markers:

                if reg_found == True:
                    break

                if marker in txt:
                    for regvyr in regvyrs['wwords']:
                        regvyrwword = regvyr.replace('{}', marker)
                        try:
                            match = re.search(regvyrwword, txt)
                        except Exception as e:
                            continue
                        if match:
                            reg_found = True
                            deb_text['quote'] = match.group(0)
                            break

            if reg_found == False:
                for regvyr in regvyrs['wowords']:
                    try:
                        match = re.search(regvyr, txt)
                    except Exception as e:
                        continue
                    if match:
                        reg_found = True
                        deb_text['quote'] = match.group(0)
                        break

        with open(txt_path, 'w', encoding='utf-8') as f:
            json.dump(debunk, f, ensure_ascii=False, indent=4)

    def get_google_urls(self, txt_path, blacklist_path, pages=2):

        '''
        Ищет ссылки по цитатам в Google.
        На вход принимает json-файл с текстами, json-файл с чёрным списком ссылок, количество страниц поиска (с каждой страницы по 10 найденных ссылок).
        Результат работы метода - обновлённый файл с текстами.

        '''

        with open(txt_path, 'r', encoding='utf-8') as f:
            debunk = json.load(f)

        with open(blacklist_path, 'r', encoding='utf-8') as f:
            blacklist = json.load(f)


        num_of_links = 0
        for text in tqdm(debunk):

            if text['orig_texts'] != None:
                urls = get_list_of_urls(text['orig_texts'])
            else:
                urls = []

            for i in range(pages):
                data = get_google_results(text['quote'], i+1)

                for item in data.get('items', []):
                    good_url = check_url(blacklist, urls, item['link'])
                    if good_url == True:
                        urls.append(item['link'])
                        num_of_links += 1

            text['orig_texts'] = get_dicts_with_urls(urls)

        print(f'Всего ссылок, найденных в Google:{num_of_links}') #235
        with open(txt_path, 'w', encoding='utf-8') as f:
            json.dump(debunk, f, ensure_ascii=False, indent=4)

    def get_yandex_urls(self, txt_path, blacklist_path, num_of_urls=20):

        '''
        Ищет ссылки по цитатам в Яндекс.
        На вход принимает json-файл с текстами, json-файл с чёрным списком ссылок, количество ссылок.
        Результат работы метода - обновлённый файл с текстами.

        '''

        with open(txt_path, 'r', encoding='utf-8') as f:
            debunk = json.load(f)

        with open(blacklist_path, 'r', encoding='utf-8') as f:
            blacklist = json.load(f)


        num_of_links = 0
        for text in tqdm(debunk):

            if text['orig_texts'] != None:
                urls = get_list_of_urls(text['orig_texts'])
            else:
                urls = []

            data = get_yandex_results(text['quote'], num_of_urls)
            if data == None:
                text['orig_texts'] = get_dicts_with_urls(urls)
                continue

            new_str = data

            for i in range(num_of_urls):
                index_found_beg = new_str.find('<url>')
                index_found_end = new_str.find('</url>')

                url = new_str[index_found_beg+5:index_found_end]
                good_url = check_url(blacklist, urls, url)
                if good_url == True:
                    urls.append(url)
                    num_of_links += 1

                new_str = new_str[index_found_end+6:]

            text['orig_texts'] = get_dicts_with_urls(urls)

        print(f'Всего ссылок, найденных в Яндекс:{num_of_links}') #571
        with open(txt_path, 'w', encoding='utf-8') as f:
            json.dump(debunk, f, ensure_ascii=False, indent=4)

    def get_tavily_urls(self, txt_path, blacklist_path):

        '''
        Ищет ссылки по цитатам в Tavily.
        На вход принимает json-файл с текстами, json-файл с чёрным списком ссылок.
        Результат работы метода - обновлённый файл с текстами.

        '''

        with open(txt_path, 'r', encoding='utf-8') as f:
            debunk = json.load(f)

        with open(blacklist_path, 'r', encoding='utf-8') as f:
            blacklist = json.load(f)


        num_of_links = 0
        for text in tqdm(debunk):

            if text['orig_texts'] != None:
                urls = get_list_of_urls(text['orig_texts'])
            else:
                urls = []

            data = get_tavily_results(text['quote'][:100])

            for result in data['results']:
                good_url = check_url(blacklist, urls, result['url'])
                if good_url == True:
                    urls.append(result['url'])
                    num_of_links += 1

            text['orig_texts'] = get_dicts_with_urls(urls)

        print(f'Всего ссылок, найденных в Tavily:{num_of_links}') #141
        with open(txt_path, 'w', encoding='utf-8') as f:
            json.dump(debunk, f, ensure_ascii=False, indent=4)

    def get_content_from_urls(self, txt_path):

        '''
        Содержание статей с помощью библиотеки newspaper
        На вход принимает json-файл с текстами.
        Результат работы метода - обновлённый файл с текстами.

        '''

        with open(txt_path, 'r', encoding='utf-8') as f:
            debunk = json.load(f)

        found_titles = 0
        found_texts = 0
        found_dates = 0

        with open(txt_path, 'w', encoding='utf-8') as f:

            for text in debunk:

                orig_wcontent = []
                for orig_text in tqdm(text['orig_texts']):

                    url = orig_text['url']
                    url_data = parse_article(url)

                    if url_data['title'] != 'no data':
                        orig_text['title'] = url_data['title']
                        found_titles += 1
                    if url_data['publish_date'] != 'no data':
                        orig_text['publish_date'] = url_data['publish_date']
                        found_dates += 1
                    if url_data['text'] != 'no data':
                        orig_text['text'] = url_data['text']
                        found_texts += 1 
                        orig_wcontent.append(orig_text)

                text['orig_texts'] = orig_wcontent
                json.dump(debunk, f, ensure_ascii=False, indent=4)

                print(f'Найдено заголовков: {found_titles}') #364
                print(f'Найдено текстов: {found_texts}') #333
                print(f'Найдено дат публикаций: {found_dates}') #137

if __name__ == '__main__':

    finder = OrigTextFinder()
    finder.get_quotes('unmarked_dataset.json', 'quote_markers.txt', 'regexps.txt', 'regexps_wquotemarkers.txt')
    finder.get_google_urls('unmarked_dataset.json', 'blacklist_urls.json', 1)
    finder.get_yandex_urls('unmarked_dataset.json', 'blacklist_urls.json', 20)
    finder.get_tavily_urls('unmarked_dataset.json', 'blacklist_urls.json')
    finder.get_content_from_urls('unmarked_dataset.json')




    
        


    
                


