from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
from pprint import pprint
import requests
import re

i = 38
next = 'дальше'
while next == 'дальше':


    main_link = 'https://kazan.hh.ru/search/vacancy'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
    params = {'text':'python', 'page': i}
    html = requests.get(main_link, params=params, headers=header).text
    soup = bs(html, 'lxml')
    try:
        next = soup.find('a',{'class':'bloko-button HH-Pager-Controls-Next HH-Pager-Control'}).getText()
        next_href = soup.find('a',{'class':'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})['href']
        print(next_href)
        i += 1

        vacancy_block = soup.find('div', {'class': 'vacancy-serp'})
        vacancy_list = vacancy_block('div', {'class': 'vacancy-serp-item'})

        vacancies = []
        for vacancy in vacancy_list:
            vacancy_data = {}
            vacancy_data['vacancy_link'] = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'})['href']
            vacancy_data['vacancy_name'] = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'}).getText()
            vacancy_data['vacancy_compensation'] = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'}).getText()

            for j, k in vacancy_data.items():
                if j == 'vacancy_compensation':
                    if 'до' in k:
                        min = None
                        max = re.findall('\d*\d', k)
                        max = int(''.join(map(str, max)))
                        money= re.findall('[а-яA-z]..', k)[-1]
                    elif '-' in k:
                        min = re.findall('\d*\d', k)
                        min = int(''.join(map(str, min[:2])))
                        max = re.findall('\d*\d', k)
                        max = int(''.join(map(str, max[2:])))
                        money = re.findall('[а-яA-z]..', k)[-1]
                    elif 'от' in k:
                        min = re.findall('\d*\d', k)
                        min = int(''.join(map(str, min)))
                        max = None
                        money = re.findall('[а-яA-z]..', k)[-1]
                    else:
                        min = None
                        max = None
                        money = None
            vacancy_data['min'] = min
            vacancy_data['max'] = max
            vacancy_data['money'] = money

            vacancies.append(vacancy_data)
    except:
        break


client = MongoClient('localhost',27017)
db = client['hh']
parsing = db.parsing
parsing.delete_many({})
parsing.insert_many(vacancies)

for i in parsing.find({'max':{'$gte': 100000}},{'vacancy_name':1, 'vacancy_link':1, 'max':1, '_id':0}):
    pprint(i)