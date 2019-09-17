import requests
import re
from multiprocessing import Pool
from bs4 import BeautifulSoup
from lib.parser import parse
from lib.writer import write
import pdb

TMP_DIR = './raw/'

def mep_profile_url(id):
    return 'https://www.europarl.europa.eu/meps/en/' + str(id) + '/slug/declarations'

def meps_index_url():
    return 'https://www.europarl.europa.eu/meps/en/full-list/all'

def get_html_page(url):
    res = requests.get(url)
    return BeautifulSoup(res.text, 'html.parser')

def declarations_url(doc):
    # print(doc)
    elements = doc.find_all('span', class_='ep_name')
    span = next((x for x in elements if x.text.startswith('Original declaration')), None)

    if(not span):
        return

    return span.find_parent('a', title='Read the document')['href']

def download_declaration(id, url):
    res = requests.get(url)
    path = TMP_DIR + str(id) + '.pdf'

    with open(path, 'wb+') as file:
        file.write(res.content)

    return path

def mep_id_from_url(url):
    return re.search(r'\d+$', url).group()

def mep_data(item):
    return {
        'id': mep_id_from_url(item.find('a')['href']),
        'fullName': item.find('span', class_='member-name').text,
        'group': item.find('div', class_='ep-layout_group').text,
        'country': item.find('div', class_='ep-layout_country').text,
        'party': item.find('div', class_='ep-layout_party').text,
    }

def get_meps(doc):
    items = doc.find_all('li', class_='single-member-container')
    return [mep_data(x) for x in items]

def scrape_meps_index():
    doc = get_html_page(meps_index_url())
    return get_meps(doc)

def scrape_mep_declaration(id):
    doc = get_html_page(mep_profile_url(id))
    url = declarations_url(doc)

    if(not url):
        return None

    pdf = download_declaration(id, url)
    data = parse(pdf)
    return data

def scrape():
    print('Downloading MEPs index...')
    meps = scrape_meps_index()

    print('Downloading and processing MEPs\' financial declarations...')
    for mep in meps[80:]:
        mep['declaration'] = scrape_mep_declaration(mep['id'])
        write(mep['id'], mep)
        print(u'\u2713 ' + mep['fullName'])

    write('_index', meps)
