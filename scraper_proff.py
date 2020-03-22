import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_info_from_proff_profile(profile_url):
    page = requests.get(profile_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    email = soup.find(class_='email-link')
    email = email.find('span') if email is not None else email
    email = email.find('span') if email is not None else email
    email = email.get_text() if email is not None else email

    employee = soup.find(class_='employees-info')
    employee = employee.find('em') if employee is not None else employee
    employee = employee.get_text() if employee is not None else employee

    ceo = soup.find(name='a', class_='addax addax-cs_ip_role_roles_click')
    if ceo is not None:
        ceo = ceo.get_text().strip()
        index = ceo.index('(')
        ceo = ceo[0:index]

    url = soup.find(name='a', class_='addax-cs_ip_homepage_url_click')
    url = url.get('href').strip() if url is not None else url
    return email, employee, ceo, url


names = []
descriptions = []
org_numbers = []
addresses = []
urls = []
proff_profiles = []
ceo_fios = []
employees = []
emails = []
cities = []

next_url = 'https://proff.no/s%C3%B8k-etter-bransje/YLoFmCo_zvNZxJID58xbvLFl_00WkiF1YhtKdVP2DH7q9ML7fkP1mBywa54Z7cJoB95okX8KgB9C6JV7M14A4ii-RGvAhN412Wvp7e0TodI/?q=Regnskapstjenester'

for i in range(160):
    print('scraping {} page with url {}'.format(i + 1, next_url))
    page = requests.get(next_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    next_url = 'https://proff.no' + soup.find('li', class_='next').find('a').get('href')
    items = soup.findAll(class_='search-container')

    for item in items:
        name = item.find('h3').get_text().strip()
        description = item.find(class_='description').get_text().strip()
        org_number = item.find(class_='org-number').find('span').get_text().split(' ')
        org_number = org_number[2] + org_number[3] + org_number[4]
        address = item.find(name='div', class_='address').find('span')

        if address is not None:
            address = address.get_text().strip()
            city = address[address.rfind(' ') + 1:len(address)]
        else:
            city = ''

        url = item.find(class_='company-image-wrap')
        url = url.find('a').get('href').strip() if url is not None else url
        proff_profile = 'https://proff.no' + item.find('h3').find('a').get('href')
        email, employee, ceo, url2 = get_info_from_proff_profile(proff_profile)
        url = url2 if url is None else url

        names.append(name)
        descriptions.append(description)
        org_numbers.append(org_number)
        addresses.append(address)
        urls.append(url)
        proff_profiles.append(proff_profile)
        ceo_fios.append(ceo)
        emails.append(email)
        employees.append(employee)
        cities.append(city)

    data_frame = pd.DataFrame(
        {
            'Название': names,
            'Описание': descriptions,
            'Номер (Org nr) ': org_numbers,
            'Город': cities,
            'Адрес': addresses,
            'Сайт (URL)': urls,
            'Email': emails,
            'Профиль на Proff (URL)': proff_profiles,
            'Кол-во сотрудников': employees,
            'ФИО руководителя': ceo_fios,
        })

    data_frame.to_csv('results/proff_search.csv', index=False)
