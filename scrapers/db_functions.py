import MySQLdb as mdb
import pandas.io.sql as sql

# pandas' sql wrappers defined in
# https://github.com/pydata/pandas/blob/master/pandas/io/sql.py

DB = 'demo'

#db = mdb.connect(user="root", host="localhost", port=3306, db=DB)
#cursor = db.cursor()

def read_sql(query, params=None, db=DB):
    db = mdb.connect(user="root", host="localhost", port=3306, db=db,
                     charset='utf8')
    df = sql.read_sql(query, db, params=params)
    db.close()
    return df

def to_sql(df, table_name, if_exists='append', null=mdb.NULL, db=DB):

    # replace NaNs
    df.fillna(null, inplace=True)

    # open connection to db
    db = mdb.connect(user="root", host="localhost", port=3306, db=db,
                     charset='utf8')
    # write to db
    try:
        sql.to_sql(df, table_name, db, 'mysql', if_exists)
    except AttributeError:
        sql.write_frame(df, table_name, db, 'mysql', if_exists)

    # close connection to db
    db.close()

def queryNotInDb(job, city, state, table):
    sql = 'select * from %(table)s where job="%(job)s" and city="%(city)s" and state="%(state)s"' %locals()
    return read_sql(sql).empty

def _get_cities_from_db(table='jobs_cities2'):
    sql = 'select distinct(city), state, state_name from %s'%table
    return read_sql(sql)

def get_cities_from_db():
    sql = 'select city, state from postings group by city, state'
    return read_sql(sql)

def _get_jobs_from_db(table='jobs_cities2'):
    sql = 'select distinct(job) from %s'%table
    return read_sql(sql)

def get_jobs_from_db():
    sql = 'select job from postings group by job'
    return read_sql(sql)

def get_cities_for_job(job):
    sql = 'select city, state from postings where job=%(job)s group by city, state'
    return read_sql(sql, params={'job':job})

def get_top_cities_from_db():
    sql = """
    (select city, state from top_cities order by n_postings desc limit 30)
    UNION
    (select city, state from top_cities order by top20 desc limit 20)
    """
    return read_sql(sql)

def get_country_codes_from_db():
    sql = 'select distinct(Code) from mercer_quality_of_living_2012 as mercer inner join country_codes as country on country.Country = mercer.Country order by mercer.Rank'
    return read_sql(sql)
