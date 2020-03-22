import pandas as pd
import requests
from bs4 import BeautifulSoup


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


def get_more_info(link):
    profile_page = requests.get(link)
    soup2 = BeautifulSoup(profile_page.content, 'html.parser')

    description = soup2.find(class_='companyDescription card')
    description = description.find(class_='intro') if description is not None else description
    description = description.get_text() if description is not None else description

    org_number = None
    proff_link = None
    ceo_fio = None
    revenues = None
    profitability = None
    proff_card = soup2.find(class_='Proff card full')
    if proff_card is not None:
        proff_info = proff_card.find(class_='info')
        proff_info_items = proff_info.find_all(class_='value') if proff_info is not None else None
        if len(proff_info_items) is not None:
            if len(proff_info_items) > 1:
                org_number = proff_info_items[1] if proff_info_items is not None else None
                org_number = org_number.get_text() if org_number is not None else org_number

        proff_intro = proff_card.find(class_='intro')
        proff_link = proff_intro.find('a').get('href').strip() if proff_intro is not None else proff_intro

        ceos = proff_card.find_all(class_='role')
        ceo_fio = ceos[0].find(class_='rolename e-icon-user') if len(ceos) != 0 else None
        ceo_fio = ceo_fio.get_text().strip() if ceo_fio is not None else ceo_fio

        purplebox = proff_card.find(class_='purplebox')
        purplebox_items = purplebox.find_all(class_='value') if purplebox is not None else None
        if len(purplebox_items) > 0:
            revenues = purplebox_items[0].get_text() if purplebox_items is not None else ''
        else:
            revenues = None

        if len(purplebox_items) > 1:
            profitability = purplebox_items[1].get_text() if purplebox_items is not None else ''
        else:
            profitability = None

    return description, org_number, proff_link, ceo_fio, revenues, profitability


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
revenueses = []
profitabilities = []
profile_links = []

base_url = 'https://www.gulesider.no/regnskapsbyr%C3%A5/bedrifter/{}'

for i in range(143, 160):
    next_url = base_url.format(i)
    print('scraping {} page with url {}'.format(i, next_url))

    page = requests.get(next_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    items = soup.findAll(name='article', class_='CompanyResultListItem')

    for item in items:
        name = item.find(name='h3').get_text()
        profile_link = 'https://www.gulesider.no' + item.find(name='h3').find('a').get(
            'href')

        address = item.find('address')
        if address is not None:
            address = address.get_text().strip()
            city = address[address.rfind(' ') + 1:len(address)]
        else:
            city = ' '

        url = item.find(name='a', class_='homePage')
        url = url.get('href').strip() if url is not None else url

        description, org_number, proff_profile, ceo_fio, revenue, profitability = get_more_info(profile_link)

        if proff_profile is not None:
            email, employee, ceo, url_from_proff = get_info_from_proff_profile(proff_profile)
        else:
            email = None
            employee = None
            ceo = None
            url_from_proff = None

        url = url_from_proff if url_from_proff is not None else url

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
        revenueses.append(revenue)
        profitabilities.append(profitability)
        profile_links.append(profile_link)

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
            'Выручка': revenueses,
            'Рентабельность': profitabilities,
            'Ссылка gulesider': profile_links
        })

    data_frame.to_csv('results/gulesider_search.csv', index=False)
