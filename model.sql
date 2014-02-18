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
    where job in (%(job1)s, %(job2)s)
    group by formattedLocation) as p
    left outer join
    (select job, city, state, formattedLocation, count(*) as n1
    from postings
    where job = %(job1)s
    group by formattedLocation) as p1
    on p.formattedLocation = p1.formattedLocation
    left outer join
    (select job, city, state, formattedLocation, count(*) as n2
    from postings
    where job = %(job2)s
    group by formattedLocation) as p2
    on p.formattedLocation = p2.formattedLocation
    left outer join
    (select city, state, salary
    from salary
    where job = %(job1)s) as j1
    on p1.city = j1.city and p1.state = j1.state
    left outer join
    (select city, state, salary
    from salary
    where job = %(job2)s) as j2
    on p2.city = j2.city and p2.state = j2.state
    inner join cities4 c
    on p.city = c.city and p.state = c.state
group by p.city, p.state
order by adj_salary, salary_sum, n_sum, salary_diff, n_diff
