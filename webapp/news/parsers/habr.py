from datetime import datetime
from bs4 import BeautifulSoup

from webapp.db import db
from webapp.news.models import News
from webapp.news.parsers.utils import get_html, save_news


def get_news_snippets():
    html = get_html('https://habr.com/ru/search/?target_type=posts&q=python&order')
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        all_news = soup.find('div', class_='tm-articles-list').find_all('article', class_='tm-articles-list__item')
        result_news = []
        for news in all_news:
            title = news.find('a', class_='tm-title__link').text
            url = 'https://habr.com' + news.find('a', class_='tm-title__link')['href']
            published = datetime.strptime(news.find('time')['title'], '%Y-%m-%d, %H:%M')
            save_news(title, url, published)


def get_news_content():
    news_without_text = News.query.filter(News.text.is_(None))
    for news in news_without_text:
        html = get_html(news.url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            news_text = soup.find('div', xmlns='http://www.w3.org/1999/xhtml').decode_contents()
            if news_text:
                news.text = news_text
                db.session.add(news)
                db.session.commit()


