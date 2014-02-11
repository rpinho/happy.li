import pandas as pd
import re
import locale
import socket
import collections
import itertools
import requests
from bs4 import BeautifulSoup

# downloaded from: https://stackoverflow.com/questions/4460921/extract-the-first-paragraph-from-a-wikipedia-article-python
from wikipedia import *
from wiki2plain import *

# my db wrappers around pandas' sql wrappers
import db_functions as db

# path to .csv, .txt and .xlsx files
PATH = 'tables/'

# IP address for API requests
IP = socket.gethostbyname(socket.gethostname())

# ZIP
ZIP_CODES = 'http://www.unitedstateszipcodes.org/zip-code-database/'

# for converting currency strings to int or float
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8' )

# MEDIAN HOUSEHOLD INCOME
def get_household_income_from_orlando_sentinel():
    name = 'city_median_income'
    url = 'http://databases.sun-sentinel.com/Orlando/ftlaudOS2011income/income2011_list.php'
    df = pd.read_html(url)[6][:-1]
    for i in range(2,28):
        print i
        df = df.append(pd.read_html(url + '?goto=%d'%i)[6][:-1])
    df.columns = ['0', 'City', 'State', 'Median_Income', '4']
    df = df[['City', 'State', 'Median_Income']]
    df.Median_Income = df.Median_Income.str.strip('$').apply(locale.atof)
    return df

#
def get_cnn_money_best_small_towns():
    name = 'cnn_money_best_small_towns_2012'
    url = 'http://money.cnn.com/magazines/moneymag/best-places/2013/full_list/'
    # NOTE: dict is not ordered..
    classes = {"rank listCol1": 'rank',
               "town listCol2": 'town',
               "population-rounded listCol3": 'population',
               "medhomeprice-visible": 'medhomeprice',
               "medfaminc-visible": 'medfaminc',
               "jobgrowth-visible": 'jobgrowth',
               "readingTestScores-visible": 'readingTestScores',
               "mathTestScores-visible": 'mathTestScores',
               "personalCrime-visible": 'personalCrime',
               "propertyCrime-visible": 'propertyCrime',
               "state": 'state',
               "region": 'region'}
    session = requests.session()
    response = session.get(url)
    soup = BeautifulSoup(response.text)
    d = {}
    for class_, column in classes.items():
        tags = soup.findAll('span', {'class':class_})
        matches = re.findall(r'"%s">(.*?)</span>'%class_, str(tags))
        d[column] = matches

    # pandas dataframe
    df = pd.DataFrame(d)

    # strip symbols
    df.jobgrowth = df.jobgrowth.str.strip('%')
    df.medfaminc = df.medfaminc.str.strip('$').str.replace(',', '')
    df.medhomeprice = df.medhomeprice.str.strip('$').str.replace(',', '')
    df.population = df.population.str.replace(',', '')
    # strip state (df already has column 'state')
    df.town = df.town.str.replace(r',(.*)', '')

    # re-order columns
    columns = ['rank','town','state','population','medhomeprice','medfaminc',
               'jobgrowth','readingTestScores','mathTestScores','personalCrime',
               'propertyCrime','region']
    df = df[columns]

    # MySQL
    db.to_sql(df, name, 'replace')

    return df

# Where are the U.S. millionaires?
# Source: Phoenix Marketing International
# google map: https://www.google.com/fusiontables/embedviz?q=select+col2%3E%3E1+from+12rTdQXpMbuOL7guVoQZwa2gCGE5nxaOHR8HZx6g&viz=MAP&h=false&lat=36.56484717808576&lng=-94.16794525&t=1&z=3&l=col2%3E%3E1&y=2&tmplt=2&hml=KML
def get_us_millionaires():
    name = 'phoenix_millionaires_2013'
    url = 'http://blogs.wsj.com/public/resources/documents/st_millionaires20140116.html'
    df = pd.read_html(url)[0]
    df.drop(5, axis=1, inplace=True)
    df.columns = ['State', 'Households', 'Millionaires', '2013 Ratio',
                  'Ratio change from 2012']

    db.to_sql(df, name, 'replace')

    return df

#
def get_cities_from_wikipedia():
    # copy-pasted in excel
    fname = 'List_of_United_States_cities_by_population.xlsx'
    df = pd.read_excel(PATH + fname, 'Sheet1', header=0, skiprows=0)

    # drop blank lines and some columns
    columns = [u'2012 rank', u'City', u'State[5]', u'2012 estimate']#,
               #u'2010 Census', u'Change']]
    df = df.dropna()[columns]

    # clean citations [*]
    df.City = df.City.str.replace(r'\[[0-9]*\]', '')
    df.columns = [u'2012 rank', u'city', u'state', u'population']#,

#
def get_state_codes_from_wikipedia():
    name = 'state_codes'
    #url = 'https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations'
    fname = 'List_of_U.S._state_abbreviations.xlsx'
    df = pd.read_excel(PATH + fname, 'Sheet1', header=0)
    # columns = name of state, code of state
    df = df[['Name', 'ANSI[2]']]
    df.columns = ['Name', 'Code']
    # MySQL
    db.to_sql(df, name, 'replace')
    return df

# from https://stackoverflow.com/questions/4460921/extract-the-first-paragraph-from-a-wikipedia-article-python
def get_Wikipedia(city, state=''):
    query = (', '.join((city, state))) if state else city
    print query

    lang = 'simple'
    wiki = Wikipedia(lang)

    try:
        raw = wiki.article(query)
    except:
        raw = None

    if raw:
        wiki2plain = Wiki2Plain(raw)
        content = wiki2plain.text
        #image = wiki2plain.image()
        return content

# descriptions = [get_first_paragraph_from_wiki(city, state_name) for city, state, state_name in cities.values]
def get_first_paragraph_from_wiki(city, state=''):
    content = get_Wikipedia(city, state)
    if content:
        first_paragraph = content.split('\n')[0]
        print first_paragraph
        return first_paragraph

params = {'v':'1.0',
          'rsz':1,
          'safe':'active',
          'userip':IP,
          'as_filetype':'jpg',
          'as_sitesearch':'',#wikimedia.org',
          'imgsz':'large'}#medium'}#small'}

# urls = [get_Google_image(city, state) for city, state in cities.values]
def get_Google_image(city, state='', params=params):
    API = 'https://ajax.googleapis.com/ajax/services/search/images?'
    query = ', '.join((city, state)) if state else city
    print query
    params['q'] = query
    session = requests.session()
    response = session.get(API, params=params)
    session.close()
    if response.ok:
        return response.json()['responseData']['results'][0]['url']

#
def save_image_locally(url, path='happy.li/static/img/'):
    print url
    session = requests.session()
    _, filename = url.rsplit('/', 1)
    with file(path + filename, 'wb') as outfile:
        response = session.get(url)
        if response.ok:
            outfile.write(response.content)
    session.close()

#
def create_top_cities_from_db(n=20):
    jobs = db.get_jobs_from_db()
    cities = []
    for job1, job2 in itertools.product(jobs.job.values, jobs.job.values):
        df = get_cities(job1, job2).head(n)
        cities.extend((df.city + ', ' + df.state).values)

    c = collections.Counter(cities)
    city = [s.split(', ')[0] for s in c.keys()]
    state = [s.split(', ')[1] for s in c.keys()]
    d = {'city':city, 'state':state, 'top20':c.values()}
    top_cities = pd.DataFrame(d)
    db.to_sql(top_cities, 'top20')
    return top_cities
