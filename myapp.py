import model
import os, json
from flask import Flask, render_template, request
import MySQLdb as mdb

app = Flask(__name__)
db = mdb.connect(user="root", host="localhost", port=3306, db="demo")
#cities_table = 'cities3'
#jobs_table = 'jobs_cities2'
#weights = {'salary_f': 0.6, 'n1_f': 0.2, 'n2_f': 0.2}
output = ['city', 'latitude', 'longitude', 'url', 'description']
n_cities = 10

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/slides")
def slides():
    return render_template('slides.html')

@app.route("/exp")
def exp():
    keys = ['url', 'name', 'description', 'image_url', 'count', 'nbackers',
               'count', 'prediction']
    result = dict(zip(keys, ['']*len(keys)))
    return render_template('exp.html', result=result)

@app.route('/maps')
def maps():
    job1 = request.args.get('job1', None, type=str)
    job2 = request.args.get('job2', None, type=str)
    return render_template('maps.html', job1=job1, job2=job2)

@app.route('/waypoints')
def waypoints():
    job1 = request.args.get('job1', None, type=str);# job1='data scientist';
    job2 = request.args.get('job2', None, type=str);# job2='psychologist';
    df = model.get_cities(job1, job2)#, weights, jobs_table, cities_table, db)
    df = df.reset_index()#df = df[output].head(n_cities)
    cities = []
    for i in range(n_cities):
        cities.append({i: (df.ix[i, 'city'],
                           df.ix[i, 'latitude'], df.ix[i, 'longitude'],
                           df.ix[i, 'url'], df.ix[i, 'description'])})
    print cities
    return json.dumps(cities)
    #return cities.to_json(orient='split')#json.dumps(list(cities))#address)

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
    app.run(debug=True, host='localhost', port=8000)
