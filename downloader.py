import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
BASE_FILENAME = "temp_music"
def search_track(a):
    encoded_query = quote(a, safe='')
    url = f'https://rus.hitmotop.com/search?q={encoded_query}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # Устанавливаем правильную кодировку, так как сайт может отдавать в latin-1
        response.encoding = 'utf-8'
        print("✅ Страница успешно загружена!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при загрузке: {e}")
        return None

    # --- 2. Создаем "суп" и находим все книги ---
    soup = BeautifulSoup(response.text, 'html.parser')
    # Находим все элементы, содержащие информацию о книге
    links = soup.find_all(attrs={'data-nopjax': True, 'href': True})[1:]

    print(f"🔍 Найдено книг на странице: {len(links)}\n")

    print(links)
    return [item['href'] for item in links]


def simple_download(url, filename=None):
    """
    Максимально простая функция скачивания

    Args:
        url (str): URL для скачивания
        filename (str, optional): Имя файла для сохранения

    Returns:
        bool: True если успешно, False если ошибка
    """
    try:
        # Если имя не указано, берем из URL
        if not filename:
            filename = url.split('/')[-1].split('?')[0]
            if not filename:
                filename = 'downloaded_file'

        # Скачиваем
        filename = f'{BASE_FILENAME}\\{filename}'
        response = requests.get(url)
        response.raise_for_status()

        # Сохраняем
        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f"Сохранено в {filename}")
        return filename

    except Exception as e:
        print(f"Ошибка: {e}")
        return None
