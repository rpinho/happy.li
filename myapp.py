import os
import logging
import json
from flask import Flask, render_template, request

# my db wrappers around pandas' sql wrappers
import scrapers.db_functions as db

# my helper functions for live scraping indeed.com
import scrapers.indeed as indeed

# my model: main sql query and weighted average
import model

# number of cities shown in results.html
n_cities = 10
# max number of indeed.com job postings for live search
maxPostings = 501
# controls the number of cities for live search (NOTE: this number is not fixed)
maxCities = 20

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/slideshow")
def slideshow():
    return render_template('slideshow.html')

@app.route("/_exp")
def exp():
    #keys = ['url', 'name', 'description', 'image_url', 'count', 'nbackers',
     #          'count', 'prediction']
    #results = [dict(zip(keys, ['%d'%i]*len(keys))) for i in range(1,4)]
    df = model.get_cities().reset_index()
    results = df.T.to_dict().values()[:n_cities]
    return render_template('exp_cards.html', results=results)
    #return render_template('exp_sliders.html', results=results)

@app.route('/maps')
def maps():
    job1 = request.args.get('job1', None, type=str)
    job2 = request.args.get('job2', None, type=str)
    return render_template('maps.html', job1=job1, job2=job2)

@app.route('/results')
def results():
    job1 = request.args.get('job1')
    job2 = request.args.get('job2')

    # print query to log file
    queryLogging(job1, job2)

    # remove leading and trailing whitespace
    job1 = job1.strip()
    job2 = job2.strip()

    # empty string
    if not job1:
        return emptyStringMessage('A')
    if not job2:
        return emptyStringMessage('B')

    # one-letter job title
    if len(job1) == 1:
        return lengthOneStringMessage(job1)
    if len(job2) == 1:
        return lengthOneStringMessage(job2)

    # title case job titles
    job1 = titlecasedJob(job1)
    job2 = titlecasedJob(job2)


    ### LIVE SEARCH #

    # job not in db: do live search
    if db.jobNotInDb(job1):
        #return jobNotInDbMessage(job1)
        indeed.get_postings_top_cities(job1, maxPostings, maxCities)

    # search did not match any jobs
    if db.jobNotInDb(job1):
        return noJobsMessage(job1)

    # salary not in db: do live search
    if db.salaryNotInDb(job1):
        indeed.get_salaries_for_job(job1)

    if db.jobNotInDb(job2):
        #return jobNotInDbMessage(job2)
        indeed.get_postings_top_cities(job2, maxPostings, maxCities)

    # search did not match any jobs
    if db.jobNotInDb(job2):
        return noJobsMessage(job2)

    # salary not in db: do live search
    if db.salaryNotInDb(job2):
        indeed.get_salaries_for_job(job2)

    # model
    df = model.get_cities(job1, job2).reset_index()
    results = df.T.to_dict().values()[:n_cities]

    return render_template('results.html', results=results)

@app.route('/waypoints')
def waypoints():
    job1 = request.args.get('job1', None, type=str)
    job2 = request.args.get('job2', None, type=str)
    df = model.get_cities(job1, job2)#, weights, jobs_table, cities_table, db)
    df = df.reset_index()#df = df[output].head(n_cities)
    cities = []
    for i in range(n_cities):
        cities.append({i: (df.ix[i, 'city'],
                           df.ix[i, 'latitude'], df.ix[i, 'longitude'],
                           df.ix[i, 'image_url'], df.ix[i, 'description'])})
    print cities
    return json.dumps(cities)
    #return cities.to_json(orient='split')#json.dumps(list(cities))#address)

def jobs(table='postings'):
    """Return list of jobs."""
    job = request.args.get('term')
    # protect from SQL injection
    if job: job = job.strip(';')
    sql = "select job from {0} where job like '%{1}%' group by job"
    df = db.read_sql(sql.format(table, job))
    return json.dumps(df.job.values.tolist())

# I have a dictionary that holds functions
# that respond to json requests
JSON = {
    'jobs': jobs,
    'job1': jobs,
    'job2': jobs
}

# jobs function is called here
@app.route("/json/<what>")
def ajson(what):

    return JSON[what]()

# return correct case if not already correctly capitalized
def titlecasedJob(job):
    s = str(job)
    # e.g. isupper() == True for s = 'CEO' or 'RN'
    if not (s.istitle() or s.isupper() or any(map(str.isupper, s.split()))):
        return s.title()
    else:
        return s

def jobNotInDbMessage(job):
    #logging.basicConfig(filename='jobNotInDb.log', format='%(message)s')
    #logging.debug('%s', job)
    return 'Sorry, "%s" not in the database yet. Live search coming soon.' %job

def emptyStringMessage(partner):
    return "Please enter job title for partner %s." %partner

def lengthOneStringMessage(job):
    return 'Sorry, "%s" is not a valid job title.' %job

def noJobsMessage(job):
    return 'Sorry, the search "%s" did not match any jobs. Is "%s" an english word? Currently we only search for jobs in the US.' %(job, job)

def queryLogging(job1, job2):
    logging.basicConfig(filename='queries.log')#, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('%s, %s', job1, job2)

    # just log jobs and nothing else
    with open('jobs.log', 'a') as f:
        print >> f, job1, '\t', job2

@app.route('/<pagename>')
def regularpage(pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    return "You've arrived at " + pagename
    #if pagename==None:
    #    raise Exception, 'page_not_found'
    #return render_template(pagename)

if __name__ == '__main__':
    print "Starting debugging server."
    app.run(debug=True, host='0.0.0.0', port=5000)
