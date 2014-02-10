import pandas as pd
import re
import locale
import time
import requests
from bs4 import BeautifulSoup

# my db wrappers around pandas' sql wrappers
import db_functions as db

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8' )

# sheetname='city_infrastructure':
def get_mercer_quality_of_living(sheetname='quality_of_living'):
    # url = 'http://www.mercer.com/press-releases/quality-of-living-report-2012'
    fname = 'mercer-quality-of-living-report-2012.xlsx'
    name = '_'.join(('mercer', sheetname, '2012'))
    df = pd.read_excel(fname, sheetname, header=1, skiprows=1)
    # create new column 'State'
    df['State'] = pd.Series([mdb.NULL]*len(df), index=df.index)
    # get american states and split city, state
    us_i = df.query('Country == "United States"').index
    states = list(df.City[us_i].str.split(', ').apply(lambda x: x[1]).values)
    #states = ['HI', 'CA', 'MA', 'IL', 'DC', 'NY', 'WA', 'PA', 'MI']
    df.State[us_i] = states
    df.City[us_i] = df.City[us_i].str.replace(r', (..)', '')
    # replace NaN with MySQL NULL
    #mdb.FIELD_TYPE.NULL
    #df.State.fillna(mdb.NULL, inplace=True)

    # MySQL
    db.to_sql(df, name, 'replace')

    return df

#
def get_data_scientist_salary_world_from_kd():
    name = 'data_scientist_salary_world'
    url = 'http://www.kdnuggets.com/2013/02/salary-analytics-data-mining-data-science-professionals.html'
    df = pd.read_html(url)[3]
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    df = df.fillna(mdb.NULL)
    db.to_sql(df, name, 'replace')
    return df

#
def get_country_codes_from_wiki():
    name = 'country_codes'
    #url = 'https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2'
    fname = 'ISO_3166.xlsx'
    df = pd.read_excel(fname, 'Sheet1', header=0, skiprows=0)
    # select columns
    df = df[['Code', 'Country name', 'ccTLD']]
    df.columns = [u'Code', u'Country', u'ccTLD']
    # replace 'GB' with 'UK'
    df.Code[81] = u'UK'#df.ccTLD[82]
    # replace '.gb' with '.uk'
    df.ccTLD[81] = u'.co.uk'#df.ccTLD[82]
    df = df[~df.Country.isnull()]
    df.iloc[159].Code = 'NA'

    db.to_sql(df, name, 'replace')

    return df

# INTERNATIONAL SALARIES
def scrape_payscale_for_salary(url, save_=False):
    session = requests.session()
    response = session.get(url)

    # TODO: solve 'latin' to utf problems
    if save_:
        d = {'url':[url],
             'text':[response.text],
             'date':[time.strftime('%Y-%m-%d %H:%M:%S')]}
        db.to_sql(pd.DataFrame(d), 'payscale', 'append')

    soup = BeautifulSoup(response.text)
    attrs = ["you_label", "median_only_you_label"]
    tags = soup.findAll('div', attrs) ;print tags
    if tags:
        matches = re.findall(r'([0-9]*,*[0-9]*)\r', str(tags))[1::2]
        return [locale.atoi(match) for match in matches]

# INTERNATIONAL SALARIES
def get_country_salaries_from_payscale(country, job):
    API = 'http://www.payscale.com'
    routes = ('/research/%s/Job=%s/Salary' %(country, job.replace(' ', '_')),
              '/rcsearch.aspx?str=%s&country=%s&category=Job' %(job, country))
    salaries = [scrape_payscale_for_salary(API + route) for route in routes]
    return salaries
