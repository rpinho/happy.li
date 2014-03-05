create view x as select zipcode from household_income order by mean_household_income desc limit 30;

select distinct(primary_city), state from zip_codes where zip in (select * from x);

select city, state, sum(salary) as salary from (select * from jobs_cities where job in ('Data Scientist', 'Psychologist')) as t group by city;

select city, cities.state, zip from cities inner join zip_codes on cities.city=zip_codes.primary_city and cities.state=zip_codes.state;

select city from cities where city not in (select city from jobs_cities2);

CREATE TABLE cities2 AS
select j.city, j.state, j.state_name, z.latitude, z.longitude,
    avg(h.mean_household_income) as mean_household_income
from zip_codes z
    inner join
    (select city, state, state_name
    from jobs_cities2
    group by city, state) as j
    on z.primary_city=j.city and z.state=j.state
    inner join household_income h
    on z.zip=h.zipcode
group by city;

CREATE TABLE cities3 AS
select c.*, url, description
from cities2 c
    inner join city_url u
    on c.city=u.city and c.state=u.state
    inner join city_description d
    on c.city=d.city and c.state=d.state
order by city;

CREATE TABLE cities4 AS
select c.city, c.state, c.state_name,
    c.median_income as mean_household_income,
    z.latitude, z.longitude,
    u.url, d.description
from city_median_income c
    inner join zip_codes z
    on c.city = z.primary_city and c.state=z.state
    inner join city_url u
    on c.city=u.city and c.state=u.state
    inner join city_description d
    on c.city=d.city and c.state=d.state
group by city, state;

select c.*, url, description
from cities2 c

order by city;

/* to create city table with mean_household_income*/
select city, cities.state, zip, avg(mean_household_income)
from cities
    inner join zip_codes
    on city=primary_city and cities.state=zip_codes.state
    inner join household_income
    on zip=zipcode
group by city;

select cities.*, latitude, longitude
from cities
    inner join
    (select city, cities.state, latitude, longitude
    from cities
        inner join zip_codes
        on city=primary_city and cities.state=zip_codes.state
    group by city) as t
    on cities.city=t.city and cities.state=t.state;


select job1.city, job2.state, job1.salary + job2.salary as salary, job1.n_postings as n1, job2.n_postings as n2 from (select * from jobs_cities where job = 'Data Scientist') as job1 inner join (select * from jobs_cities where job = 'Psychologist') as job2 on job1.city=job2.city;

select x.city, x.state, x.salary-mean_household_income as adj_salary,
    x.n1, x.n2, x.n1_f, x.n2_f, url, description
from cities3 cities
    inner join
    (select job1.city, job2.state, job1.salary + job2.salary as salary,
        job1.n_postings as n1, job2.n_postings as n2,
        job1.n_f as n1_f, job2.n_f as n2_f
    from
        (select city, state, salary, n_postings,
            n_postings/
            (select sum(n_postings)
            from jobs_cities2
            where job = 'Data Scientist') as n_f
        from jobs_cities2
        where job = 'Data Scientist') as job1
        inner join
        (select city, state, salary, n_postings,
            n_postings/
            (select sum(n_postings)
            from jobs_cities2
            where job = 'Psychologist') as n_f
        from jobs_cities2
        where job = 'Psychologist') as job2
        on job1.city = job2.city and job1.state = job2.state) as x
    on cities.city = x.city and cities.state = x.state;

select x.city, x.state, salary-mean_household_income as adj_salary from cities inner join (select city, state, sum(salary) as salary from (select * from jobs_cities where job in ('Data Scientist', 'Psychologist')) as t group by city) as x on cities.city=x.city and cities.state=x.state;


"""
select city, state,
    case when job = '%s' then n_postings end n1,
    case when job = '%s' then n_postings end n2
from jobs_cities
group by job;
"""

select mean_household_income from zip_codes inner join household_income on zip=zipcode where primary_city = 'West Hollywood' and zip_codes.state='CA';

select x.city, x.state, x.salary-mean_household_income as adj_salary,
    x.n1, x.n2, x.n1_f, x.n2_f
from cities
    inner join
    (select job1.city as city, job1.state as state,
        job1.salary + job2.salary as salary,
        job1.n_postings as n1, job2.n_postings as n2,
        job1.n_f as n1_f, job2.n_f as n2_f
    from
        (select *, n_postings/
            (select sum(n_postings)
            from jobs_cities
            where job = '%(job1)s') as n_f
        from jobs_cities
        where job = '%(job1)s') as job1
        inner join
        (select *, n_postings/
            (select sum(n_postings)
            from jobs_cities
            where job = '%(job2)s') as n_f
        from jobs_cities
        where job = '%(job2)s') as job2
        on job1.city = job2.city) as x
    on cities.city = x.city and cities.state = x.state;

ALTER TABLE jobs_cities2 CHANGE state state_name varchar(63);
ALTER TABLE jobs_cities2 ADD COLUMN state varchar(63);

UPDATE jobs_cities2 a JOIN state_codes b
    ON a.state_name = b.code
SET a.state_name = b.name;

UPDATE jobs_cities2 a JOIN state_codes b
    ON a.state_name = b.name
SET a.state = b.code;

ALTER TABLE jobs_cities2 ADD id INT(11) AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE jobs_cities2 DROP COLUMN id;
ALTER TABLE jobs_cities2 DROP PRIMARY KEY;
ALTER TABLE city_descriptions MODIFY description LONGTEXT character set utf8;

/* get cities in old list not in new jobs list */
select city, state, name as state_name from cities inner join state_codes on state=code where city not in (select city from jobs_cities2) order by city;

ALTER TABLE postings MODIFY company TEXT character set utf8;
ALTER TABLE postings MODIFY jobtitle TEXT character set utf8;
ALTER TABLE postings MODIFY url TEXT character set utf8;
ALTER TABLE shale_gas MODIFY company TEXT character set utf8;
ALTER TABLE shale_gas MODIFY jobtitle TEXT character set utf8;
ALTER TABLE shale_gas MODIFY url TEXT character set utf8;

select p1.city, p1.state,
    (j1.salary + j2.salary) as salary_sum,
    abs(j1.salary - j2.salary) as salary_diff,
    (j1.salary + j2.salary - median_income) as adj_salary,
    median_income,
    p1.n + p2.n as n_sum,
    abs(p1.n - p2.n) as n_diff,
    latitude, longitude, url, description
from
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = 'Data Scientist'
    group by formattedLocation) as p1
    inner join
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = 'Piping Engineer'
    group by formattedLocation) as p2
    on p1.formattedLocation = p2.formattedLocation
    inner join city_median_income h
    on p1.city = h.city and p1.state = h.state
    inner join
    (select city, state, salary
    from jobs_cities2
    where job = 'Data Scientist') as j1
    on p1.city = j1.city and p1.state = j1.state
    inner join
    (select city, state, salary
    from jobs_cities2
    where job = 'Piping Engineer') as j2
    on p2.city = j2.city and p2.state = j2.state
    inner join cities3 c
    on p1.city = c.city and p2.state = c.state
order by adj_salary, salary_sum, n_sum, salary_diff, n_diff;

UPDATE city_median_income SET state = (select code from city_median_income inner join state_codes on State_Name = Name);

SELECT * FROM city_median_income i
LEFT OUTER JOIN city_url u
ON i.city = i.city AND i.state = u.state
WHERE u.url IS null

/* cities not in city_url */
select city, state from city_median_income where city not in (select city from city_url) or state not in (select state from city_url) group by city, state;

/* cities not in city_descriptions */
select city, state from city_median_income where city not in (select city from city_description) or state not in (select state from city_description) group by city, state;

ALTER TABLE cities3 ADD INDEX (city);

select p1.job as job1, p2.job as job2,
    p.city, p.state,
    j1.salary as salary1, j2.salary as salary2,
    COALESCE(j1.salary + j2.salary, j1.salary, j2.salary) as salary_sum,
    COALESCE(abs(j1.salary - j2.salary), j1.salary, j2.salary) as salary_diff,
    c.mean_household_income,
    COALESCE(j1.salary + j2.salary - c.mean_household_income,
        j1.salary - c.mean_household_income,
        j2.salary - c.mean_household_income) as adj_salary,
    n1, n2, n_sum,
    COALESCE(abs(n1 - n2), n1, n2) as n_diff,
    c.latitude, c.longitude, c.url as image_url, c.description
from
    (select city, state, formattedLocation, count(*) as n_sum
    from postings
    where job in ('Data Scientist', 'Piping Engineer')
    group by formattedLocation) as p
    left outer join
    (select city, state, formattedLocation, count(*) as n1
    from postings
    where job = 'Data Scientist'
    group by formattedLocation) as p1
    on p.formattedLocation = p1.formattedLocation
    left outer join
    (select city, state, formattedLocation, count(*) as n2
    from postings
    where job = 'Piping Engineer'
    group by formattedLocation) as p2
    on p.formattedLocation = p2.formattedLocation
    left outer join
    (select city, state, salary
    from jobs_cities2
    where job = 'Data Scientist') as j1
    on p1.city = j1.city and p1.state = j1.state
    left outer join
    (select city, state, salary
    from jobs_cities2
    where job = 'Piping Engineer') as j2
    on p2.city = j2.city and p2.state = j2.state
    inner join cities4 c
    on p1.city = c.city and p1.state = c.state
order by adj_salary, salary_sum, n_sum, salary_diff, n_diff;

/* FULL OUTER JOIN equivalent to keep all cities that have at least one job */
select *
from
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = 'Data Scientist'
    group by formattedLocation) as p1
    left outer join
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = 'Piping Engineer'
    group by formattedLocation) as p2
    on p1.formattedLocation = p2.formattedLocation
UNION
select *
from
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = 'Data Scientist'
    group by formattedLocation) as p1
    right outer join
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = 'Piping Engineer'
    group by formattedLocation) as p2
    on p1.formattedLocation = p2.formattedLocation
;

/* equivalent way to keep all cities that have at least one job */
select p.city, p.state, n1, n2, n_sum
from
    (select city, state, formattedLocation, count(*) as n_sum
    from postings
    where job in ('Data Scientist', 'Piping Engineer')
    group by formattedLocation) as p
    left outer join
    (select city, state, formattedLocation, count(*) as n1
    from postings
    where job = 'Data Scientist'
    group by formattedLocation) as p1
    on p.formattedLocation = p1.formattedLocation
    left outer join
    (select city, state, formattedLocation, count(*) as n2
    from postings
    where job = 'Piping Engineer'
    group by formattedLocation) as p2
    on p.formattedLocation = p2.formattedLocation
;

(select * from top_cities order by n_postings desc limit 30)
UNION
(select * from top_cities order by top20 desc limit 20);

select job from jobs where job not in (select job from postings group by job);
