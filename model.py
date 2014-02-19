import locale
import itertools
from pandas.compat.scipy import percentileofscore

# my db wrappers around pandas' sql wrappers
import scrapers.db_functions as db

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8' )

job1 = 'Data Scientist'
job2 = 'Piping Engineer'
columns = [u'salary_sum', u'salary_diff', u'adj_salary',
           #u'mean_household_income',
           u'n_sum', u'n_diff']
weights = [0, 0, 0.4, 0.6, -0.3]
weights = dict(zip(columns, weights))
nan_values = {'job1':'', 'job2':'',
              'n1':0, 'n2':0, 'n_sum':0, 'n_diff':0,
              'salary1':0, 'salary2':0,
              'salary_sum':0, 'salary_diff':0, 'adj_salary':0,
              'description':'', 'image_url':''}

#
def get_cities(job1=job1, job2=job2, weights=weights):

    print job1, job2

    with open('model.sql', 'r') as f:
        sql = f.read()

    # query db
    df = db.read_sql(sql, params={'job1':job1, 'job2': job2})

    # NaN
    df.fillna(nan_values, inplace=True)

    # some more transformations I could not implement in mySQL
    #df['salary_f'] = df.adj_salary - df.adj_salary.min()
    #df['salary_f'] = df.salary_f / df.salary_f.sum()

    # normalize between 0 and 1 with percentile rank
    for name in weights.keys():
        df[name] = df[name].apply(lambda x: percentileofscore(df[name], x)/100)

    # compute weighted average
    score = 0
    for key, value in weights.items():
        score += df[key]*value
    df['score'] = score

    df.job1 = job1
    df.job2 = job2
    df = format_output_columns(df)
    df = get_query_url(df)

    return df.sort('score', ascending=False)

def format_output_columns(df):
    # ints
    columns = ['salary1', 'salary2', 'mean_household_income', 'n1', 'n2']
    df[columns] = df[columns].astype(int)
    # currency
    columns = ['salary1', 'salary2', 'mean_household_income']
    def moneyfmt(x): return locale.currency(x, True, True) if x else ''
    df['salary1_$'] = df.salary1.apply(moneyfmt)
    df['salary2_$'] = df.salary2.apply(moneyfmt)
    df['mean_household_income_$'] = df.mean_household_income.apply(moneyfmt)
    return df

def get_query_url(df):
    API = 'http://www.indeed.com/jobs?'
    query1 = 'q=' + df.job1 + '&l=' + df.city + ' ' + df.state
    #query1 = query1.strip().lower().replace(' ','+')
    df['query_url1'] = API + query1
    query2 = 'q=' + df.job2 + '&l=' + df.city + ' ' + df.state
    df['query_url2'] = API + query2
    return df
