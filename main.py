import requests
import time
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import pyexcel
import multiprocessing
import logging
import xlrd

class Company():
    def __init__(self, name = None, status = None, number = None, link = None) -> None:
        self.name = name
        self.status = status
        self.number = number
        self.link = link
    
    def __str__(self) -> str:
        return f'{self.name}, {self.status} {self.number}; {self.link}'
    
    def get_list(self) -> list:
        return [self.name, self.status, self.number, self.link]


def main():
    main_main_url = 'https://spb.hh.ru'
    main_url = f'{main_main_url}/employers_list'
    dict_area = {'Россия': 'areaId=113',
                 'Украина': 'areaId=5',
                 'Казахстан': 'areaId=40',
                 'Азербайджан': 'areaId=9',
                 'Беларусь': 'areaId=16',
                 'Грузия': 'areaId=28',
                 'Кыргызстан': 'areaId=48',
                 'Узбекистан': 'areaId=97',
                 'Другие_регионы': 'areaId=1001'}
    letters = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯABCDEFGHIJKLMNOPQRSTUVWXYZ'
    list_letter = []
    for letter in letters:
        list_letter.append(letter)
    list_letter.append('%23')

    dict_1 = dict_area['Россия']
    ua = UserAgent()
    headers = {'accept': '*/*', 'user-agent': ua.firefox}

    parse(main_main_url, main_url, list_letter, dict_1, headers)

    # for name_area in dict_area:
    #     url_area = dict_area[name_area]
    #     p = multiprocessing.Process(target=parse, name=name_area, args=(main_main_url, main_url, list_letter, url_area, headers))
    #     processes.append(p)
    
    # for p in processes:
    #     p.start()
    
    # for p in processes:
    #     p.join()

    time.sleep(10)

def parse(main_main_url, main_url, list_letter, url_area, headers):
    processes = []
    for letter in list_letter:
        url_letter = letter
        if letter == '%23':
            url_letter = '0-9'
        p = multiprocessing.Process(target=parse_page, name=letter, args=(main_main_url, main_url, url_area, headers, url_letter))
        processes.append(p)

    for p in processes:
        p.start()

    for p in processes:
        p.join()
            

def parse_page(main_main_url, main_url, url_area, headers, url_letter):
    error_urls = []
    result_list = []
    page = 0
    logging.basicConfig(filename=f'./russia2/{multiprocessing.current_process().name}.log',
                        level=logging.INFO,
                        format='(%(processName)s) %(asctime)s %(levelname)s - %(message)s')
    while True: #pages
                url = f'{main_url}?{url_area}&letter={url_letter}&page={page}'
                time_n = time.time()
                response = requests.get(url=url, headers=headers)
                logging.info(f'{time.time() - time_n}; {url}')
                soup = bs(response.text, 'html.parser')
                if response.status_code != 200:
                    error_urls.append([url])
                    logging.warning(url)
                    break
                elements = soup.find_all('div', {'class': "item--M8c5L2cxia1xqTMmWUFN"})
                if len(elements) == 0:
                    break
                logging.info(f'elements = {len(elements)}')
                for elem in elements:
                    text = elem.text
                    # elem = PageElement()
                    link = f"{main_main_url}{elem.find_next('a').attrs['href']}"
                    # text = 'АБЛ-Пласт, ООО  1'
                    name = "".join(text.split(',')[:-1])
                    status = text.split(',')[-1].split(' ')[-2].strip()
                    number = int(text.split(',')[-1].split(' ')[-1])
                    result_list.append([name, status, number, link])
                page += 1
    pyexcel.save_book_as(bookdict={"HH_Company": result_list, "Error_urls": error_urls}, dest_file_name=f"./russia2/HHCompany{multiprocessing.current_process().name}.xls")

if __name__ == "__main__":
    main()