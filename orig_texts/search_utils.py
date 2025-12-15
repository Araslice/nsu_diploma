from __future__ import annotations
import requests
import json
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
import os
from newspaper import Article
from newspaper.article import ArticleException

from typing import Literal, cast
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.search_api import (
    FamilyMode,
    FixTypoMode,
    GroupMode,
    Localization,
    SearchType,
    SortMode,
    SortOrder,
)

load_dotenv()

def get_google_results(query, page):

    API_KEY = os.getenv("GOOGLE_API_KEY")
    SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={page}"

    response = requests.get(url)
    return response.json()

def get_yandex_results(query, num_of_urls):

    USER_AGENT = "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.112 Mobile Safari/537.36"

    sdk = YCloudML(
        folder_id=os.getenv("YANDEX_FOLDER_ID"),
        auth=os.getenv("YANDEX_API_KEY"),
    )
    sdk.setup_default_logging()

    search = sdk.search_api.web(
        "RU",
        family_mode=FamilyMode.MODERATE,
    )

    search = search.configure(
        search_type="ru",
        family_mode="strict",
        fix_typo_mode="off",
        group_mode="deep",
        localization="ru",
        sort_order="desc",
        sort_mode="by_time",
        docs_in_group=None,
        groups_on_page=num_of_urls,
        max_passages=2,
        region="225",
        user_agent=USER_AGENT,
    )

    try:
        search_result = search.run(query, format='xml', page=0)
    except Exception as e:
        print(f'Ошибка: {e}')
        return None

    return search_result.decode("utf-8")

def get_tavily_results(query):

    search_tool = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))
    answers = search_tool.run(query)
    return answers

def get_list_of_urls(dicts_with_urls):
    urls = []

    for dict in dicts_with_urls:
        urls.append(dict['url'])

    return urls

def get_dicts_with_urls(list_of_urls):

    url_dicts = []

    for url in list_of_urls:
        url_dict = {}
        url_dict['url'] = url
        url_dicts.append(url_dict)
    return url_dicts

def check_url(blacklist, urls, url):

    good_item = True
    if url in urls:
        good_item = False

    for bad_url in blacklist:
        if bad_url in url:
            good_item = False
            break

    return good_item
    
def parse_article(url: str):

    try:
        # Проверим, доступен ли сайт
        response = requests.get(url, timeout=2)
        response.raise_for_status()

        # Создаём объект статьи
        article = Article(url, language='ru')
        article.download()
        article.parse()

        # Извлекаем нужные данные
        title = article.title or "no data"
        publish_date = article.publish_date.isoformat() if article.publish_date else "no data"
        text = article.text.strip() if article.text else "no data"

        return {
            "title": title,
            "publish_date": publish_date,
            "text": text
        }

    except ArticleException as e:
        # print(f"Ошибка парсинга статьи {url}: {e}")
        pass
    except requests.exceptions.RequestException as e:
        # print(f"Ошибка при запросе страницы {url}: {e}")
        pass
    except Exception as e:
        # print(f"Непредвиденная ошибка {url}: {e}")
        pass

    return {
        "title": "no data",
        "publish_date": "no data",
        "text": "no data"
    }