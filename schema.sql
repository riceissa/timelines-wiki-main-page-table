drop table if exists t;

create table t (
        id integer primary key autoincrement,
        pagename text unique not null,
        topic text,
        creation_month text,
        last_modified_month text,
        number_of_rows integer,
        payment real,
        monthly_pageviews integer,
        monthly_wikipedia_pageviews integer,
        principal_contributors_by_amount text,
        principal_contributors_alphabetical text,
        principal_contributors_by_amount_html text
);
