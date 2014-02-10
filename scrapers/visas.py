import re
import pandas as pd

# my db wrappers around pandas' sql wrappers
import db_functions as db

# VISA
VISA = 'http://www.visasquare.com/top-h1b-visa-sponsors'
TABLES = ['jobs']#'cities']
ROUTES = ['job-titles']#'cities']
YEARS = range(2001, 2014)

def get_visa_jobs_not_in_table(table='jobs_cities2'):
    sql = 'select distinct(name) as job from visa_jobs where name not in (select distinct(job) from %s)'%table
    return db.read_sql(sql)

# VISA
def scrape_and_write_visa_table(route, table, year=2013, url=VISA, write_=True):
    url = '-'.join((url, str(year)))
    url = '/'.join((url, route))
    df = pd.read_html(url, header=0, infer_types=False)[0]
    df.iloc[:,0] = df.iloc[:,0].astype(str)
    df.iloc[:,1] = df.iloc[:,1].apply(mk_int)
    #jobs.iloc[:,1] = jobs.iloc[:,1].astype(int)

    # clean data
    if 'jobs' in table:
        df = clean_visa_jobs_names(df)

    df['Year'] = year
    if write_:
        db.to_sql(df, table, 'replace')

    return df

# some parsing, cleaning
def clean_visa_jobs_names(jobs):

    #jobs.Name[jobs.Name.str.contains(' I|Ii ')]
    parser_dict = {' - Us': '',
                   '-Us': '',
                   'Programmeranalyst': 'Programmer Analyst',
                   'Analystdeveloper': 'Analyst Developer',
                   'Analystconsultant': 'Analyst Consultant',
                   'Managerconsultant': 'Manager Consultant',
                   'Consultantsoftware': 'Consultant Software',
                   'Engineerconsultant': 'Engineer Consultant',
                   'Engineerdeveloper': 'Engineer Developer',
                   'Designerdeveloper': 'Designer Developer',
                   'Programmerdeveloper': 'Programmer Developer',
                   'Developerengineer': 'Developer Engineer',
                   'Testeranalyst': 'Tester Analyst',
                   'Analystsenior': 'Analyst Senior',
                   'Analystsap': 'Analyst SAP',
                   'Analystsupport': 'Analyst Support',
                   'Analystsystems': 'Analyst Systems',
                   'Analystspecialist': 'Analyst Specialist',
                   'Analysttester': 'Analyst Tester',
                   'Engineerarchitect': 'Engineerarchitect',
                   'Engineertester': ' Engineer Tester',
                   'Systems Engineer (15-1199.02)':
                   'Systems Engineer (15-1199.02)'}

    for key, value in parser_dict.items():
        jobs.Name = jobs.Name.str.replace(key, value)

    #jobs.Name = jobs.Name.replace(r' Jc.*', r'', regex=True)
    # regex not implemented in my pandas version yet!
    x = jobs.Name[jobs.Name.str.contains('Jc')]
    jobs.Name[jobs.Name.str.contains('Jc')] = [
        re.sub(r' Jc.*', '', name) for name in x]

    return jobs

# VISA - all years/all tables
def main():
    for year in YEARS:
        for route, table in zip(ROUTES, TABLES):
            scrape_and_write_visa_table(route, table, year)
