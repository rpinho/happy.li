query2 = """
select p1.city, p1.state,
    j1.salary as salary1, j2.salary as salary2,
    (j1.salary + j2.salary) as salary_sum,
    abs(j1.salary - j2.salary) as salary_diff,
    c.mean_household_income,
    (j1.salary + j2.salary - c.mean_household_income) as adj_salary,
    p1.n as n1, p2.n as n2,
    p1.n + p2.n as n_sum,
    abs(p1.n - p2.n) as n_diff,
    c.latitude, c.longitude, c.url, c.description
from
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = '%(job1)s'
    group by formattedLocation) as p1
    inner join
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = '%(job2)s'
    group by formattedLocation) as p2
    on p1.formattedLocation = p2.formattedLocation
    inner join
    (select city, state, salary
    from jobs_cities2
    where job = '%(job1)s') as j1
    on p1.city = j1.city and p1.state = j1.state
    inner join
    (select city, state, salary
    from jobs_cities2
    where job = '%(job2)s') as j2
    on p2.city = j2.city and p2.state = j2.state
    inner join cities4 c
    on p1.city = c.city and p1.state = c.state
order by adj_salary, salary_sum, n_sum, salary_diff, n_diff
"""

query1 = """
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
    where job = '%(job1)s'
    group by formattedLocation) as p1
    inner join
    (select city, state, formattedLocation, count(*) as n
    from postings
    where job = '%(job2)s'
    group by formattedLocation) as p2
    on p1.formattedLocation = p2.formattedLocation
    inner join city_median_income h
    on p1.city = h.city and p1.state = h.state
    inner join
    (select city, state, salary
    from jobs_cities2
    where job = '%(job1)s') as j1
    on p1.city = j1.city and p1.state = j1.state
    inner join
    (select city, state, salary
    from jobs_cities2
    where job = '%(job2)s') as j2
    on p2.city = j2.city and p2.state = j2.state
    inner join cities3 c
    on p1.city = c.city and p2.state = c.state
order by adj_salary, salary_sum, n_sum, salary_diff, n_diff;
"""

query0 = """
select x.city, x.state, latitude, longitude,
    x.salary-mean_household_income as adj_salary,
    x.n1, x.n2, x.n1_f, x.n2_f,
    url, description
from %(cities_table)s cities
    inner join
    (select job1.city as city, job1.state as state,
        job1.salary + job2.salary as salary,
        job1.n_postings as n1, job2.n_postings as n2,
        job1.n_f as n1_f, job2.n_f as n2_f
    from
        (select *, n_postings/
            (select sum(n_postings)
            from %(jobs_table)s
            where job = '%(job1)s') as n_f
        from %(jobs_table)s
        where job = '%(job1)s') as job1
        inner join
        (select *, n_postings/
            (select sum(n_postings)
            from %(jobs_table)s
            where job = '%(job2)s') as n_f
        from %(jobs_table)s
        where job = '%(job2)s') as job2
        on job1.city = job2.city) as x
    on cities.city = x.city and cities.state = x.state
"""
