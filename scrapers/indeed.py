import pandas as pd
import numpy as np
import re
import locale
import socket
import os
import itertools
import requests
from bs4 import BeautifulSoup

# my db wrappers around pandas' sql wrappers
import db_functions as db

# path to .csv, .txt and .xlsx files
PATH = 'tables/'

# Indeed.com
URL = 'http://www.indeed.com'
API = 'http://api.indeed.com/ads/apisearch?publisher='
API += os.environ['INDEED_API_KEY'] #os.environ.get() #os.getenv()

# IP address for API requests
IP = socket.gethostbyname(socket.gethostname())

# for converting currency strings to int or float
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8' )

# pre-process job query
def format_jobQuery(jobQuery):
    jobQuery.query = jobQuery.query.strip().lower().replace(' ','+')

# beautiful soup
def get_soup(jobQuery):
    session = requests.session()
    format_jobQuery(jobQuery)
    jobQuery.full_url = jobQuery.url + jobQuery.route + jobQuery.query
    jobQuery.response = session.get(jobQuery.full_url)
    jobQuery.soup = BeautifulSoup(jobQuery.response.text)

# auxiliary class
class JobQuery:
    def __repr__(self):
        return str(self.__dict__)
    def __init__(self):
        keys = ['salary', 'city',
                'trend_last2first', 'url', 'route', 'salaries',
                'full_url', 'soup', 'job', 'trend_median', 'n_postings',
                'trend_string', 'query', 'trend_array', 'response',
                'relative_salary', 'salaries_max', 'salaries_median',
                'trend_max']
        for key in keys:
            setattr(self, key, None)

# salary
def get_salaries(jobQuery):
    tags = jobQuery.soup.findAll('span', {'class':'salary'})
    if any(tags):
        matches = [re.findall(r'>\$(.*?)?<', str(tag)) for tag in tags]
        if any(matches):
            jobQuery.salaries = [locale.atoi(match[0]) for match in matches]

# stats
def eval_salaries(jobQuery):
    jobQuery.salary = jobQuery.salaries[0]
    jobQuery.salaries_max = np.max(jobQuery.salaries)
    jobQuery.salaries_median = np.median(jobQuery.salaries)

# salary relative to other cities
def get_relative_salary(jobQuery):
    tags = jobQuery.soup.findAll('p', {'class':'caption'})
    if tags:
        matches = re.findall(r'are (..?)% higher', str(tags[0]))
        if matches:
            jobQuery.relative_salary = int(matches[0])/100.
        else:
            matches = re.findall(r'are (..?)% lower', str(tags[0]))
            if matches:
                jobQuery.relative_salary = -int(matches[0])/100.

#
def get_salary_trend(jobQuery):
    tags = jobQuery.soup.findAll('div', {'class':'salary_trends'})
    if tags:
        matches = re.findall(r'0,(.*?)"', str(tags[0]))
        if matches:
            jobQuery.trend_string = matches[0]

#
def eval_salary_trend(jobQuery):
    # split string and map to int
    trend = map(int, jobQuery.trend_string.split(","))
    # cast to array and keep only non zero
    jobQuery.trend_array = np.array(trend)[np.nonzero(trend)]
    trend = jobQuery.trend_array
    # last/first (or second, to correct for outliers - see response.headers
    jobQuery.trend_last2first = trend[-1]/float(trend[0])
    # mean trend (median actually, to correct for outliers)
    jobQuery.trend_median = np.median(trend[1:] / trend[:-1].astype(float))
    jobQuery.trend_max = np.max(trend)
    del trend

#
def scrape_indeed_salaries(jobQuery, columns):

    # get html/xml soup
    location = ' '.join((jobQuery.city, jobQuery.state))
    jobQuery.query = 'q1=%s&l1="%s"&tm=1' %(jobQuery.job, location)
    get_soup(jobQuery)

    # salary
    get_salaries(jobQuery)
    if jobQuery.salaries:
        eval_salaries(jobQuery)

    # salary relative to other cities
    if 'relative_salary' in columns:
        get_relative_salary(jobQuery)

    # trend
    if 'trend_median' in columns:
        get_salary_trend(jobQuery)
        if jobQuery.trend_string:
            eval_salary_trend(jobQuery)

#
def get_jobs(jobQuery):
    tags = jobQuery.soup.findAll('div', {'id':'searchCount'})
    if tags:
        matches = re.findall(r'of (.*?)<', str(tags[0]))
        if matches:
            jobQuery.n_postings = locale.atoi(matches[0])

#
def scrape_indeed_jobs(jobQuery):

    # get html/xml soup
    location = ' '.join((jobQuery.city, jobQuery.state))
    jobQuery.query = 'q=%s&l=%s' %(jobQuery.job, location)
    get_soup(jobQuery)

    # number of job postings
    get_jobs(jobQuery)

#
def scrape_indeed(job, city, state, df):

    jobQuery = JobQuery()
    jobQuery.job = job
    jobQuery.city = city
    jobQuery.state = state
    jobQuery.url = URL

    if 'n_postings' in df.columns:
        jobQuery.route = '/jobs?'
        scrape_indeed_jobs(jobQuery)

    if 'salary' in df.columns:
        jobQuery.route = '/salary?'
        scrape_indeed_salaries(jobQuery, df.columns)

    data = {}
    for key in df.columns:
        data[key] = getattr(jobQuery, key)

    del jobQuery
    return df.append(data, ignore_index=True)

# jobs and cities are pd.DataFrames
def update_salaries(jobs=[], cities=[], df=[], skiprows=0,
                    table='salary', verbose_=True):

    columns = ['job', 'city', 'state', 'salary']
    #columns += ['n_postings', 'state_name']
    #columns += ['relative_salary', 'salaries_max', 'salaries_median',
    #            'trend_last2first', 'trend_median', 'trend_max']

    # get jobs from text file
    if not any(jobs):
        jobs = pd.read_csv(PATH + 'jobs.txt')[skiprows:]
        #jobs.job = jobs.job.str.title()

    # get unique cities from postings
    if not any(cities):
        cities = db.get_cities_from_db()

    if not any(df):
        df = pd.DataFrame(columns=columns)

    for job, location in itertools.product(jobs.job.values, cities.values):
        city, state = location
        if db.queryNotInDb(job, city, state, table):
            df = scrape_indeed(job, city, state, df)
            if verbose_:
                print df.tail(1)
            db.to_sql(df.tail(1), table, 'append', null=0)

    return df


params = {'country':'US',
          'radius':0,
          'limit':25,
          'latlong':1,
          'format':'json',
          'userip':IP,
          'useragent':'Mozilla/%2F4.0%28Firefox%29',
          'v':2,
          'sort':None,
          'st':None,
          'fromage':None,
          'filter':1,
          'chnl':None}

# from https://ads.indeed.com/jobroll/xmlfeed
# state is 2-letter code
def indeed_api(job, city, state, table='postings', maxResults=1001,
               source='backend',  params=params, save_=True):

    # columns to keep
    columns = [u'jobkey', u'job', u'jobtitle', u'company',
               u'city', u'state', u'formattedLocation', u'country',
               u'date', u'formattedRelativeTime',
               u'latitude', u'longitude', u'url']

    # columns to add
    columns += ['indeed_city', 'source', 'timestamp']

    # query
    location = ', '.join((city, state))
    params['l'] = location
    params['q'] = job

    # first page of results (n=25)
    params['start'] = 0
    session = requests.session()
    response = session.get(API, params=params)
    df = pd.DataFrame(response.json()['results'])

    if df.empty:
        return None

    df['job'] = job
    df['indeed_city'] = df['city']
    df['city'] = city
    df['source'] = source
    df['timestamp'] = pd.tslib.Timestamp.utcnow()

    df.formattedRelativeTime = map(
        lambda x: int(x[0]), df.formattedRelativeTime.str.findall(r'[0-9].'))

    if save_:
        db.to_sql(df[columns], table, 'append')

    totalResults = response.json()['totalResults']
    print totalResults

    print map(response.json().get, [u'start', u'end', u'pageNumber'])

    # next pages of results
    limit = params['limit']
    if totalResults <= limit:
        return None

    for start in range(limit, totalResults+limit+1, limit):

        if start > maxResults:
            return None

        params['start'] = start
        response = session.get(API, params=params)
        df = pd.DataFrame(response.json()['results'])

        if df.empty:
            return None

        df['job'] = job
        df['indeed_city'] = df['city']
        df['city'] = city
        df['source'] = source
        df['timestamp'] = pd.tslib.Timestamp.utcnow()

        df.formattedRelativeTime = map(
            lambda x: int(x[0]),
            df.formattedRelativeTime.str.findall(r'[0-9].'))

        if save_:
            db.to_sql(df[columns], table, 'append')

        print map(response.json().get, [u'start', u'end', u'pageNumber'])

#
def update_postings(jobs=[], cities=[], skiprows=0, force=False,
                    table='postings'):

    # get jobs from text file
    if not any(jobs):
        jobs = pd.read_csv(PATH + 'jobs.txt')[skiprows:]
        #jobs.job = jobs.job.str.title()

    # get unique cities from postings
    if not any(cities):
        cities = db.get_cities_from_db()

    for job, location in itertools.product(jobs.job.values, cities.values):
        city, state = location
        print job, city, state
        if db.queryNotInDb(job, city, state, table) or force:
            indeed_api(job, city, state, table)

# for frontend only. less cities. one job.
def get_postings_top_cities(job, maxResults=1001, n_cities=30,
                            table='postings', save_=True):

    with open(PATH + 'jobs.txt', 'a') as f:
        print >> f, job

    # get top cities only for faster search
    cities = db.get_top_cities_from_db(n_cities)

    for city, state in cities.values:
        print city, state
        if db.queryNotInDb(job, city, state, table):
            indeed_api(job, city, state, table, maxResults, 'frontend',
                       save_=save_)

# for frontend only. less cities. one job.
def get_salaries_for_job(job, table='salary', verbose_=True, save_=True):

    columns = ['job', 'city', 'state', 'salary']
    df = pd.DataFrame(columns=columns)

    # get only the cities that actually have postings for the job
    cities = db.get_cities_for_job(job)

    for city, state in cities.values:
        if verbose_: print city, state
        if db.queryNotInDb(job, city, state, table):
            df = scrape_indeed(job, city, state, df)
            if verbose_: print df.tail(1)
            if save_: db.to_sql(df.tail(1), table, 'append', null=0)

    return df
