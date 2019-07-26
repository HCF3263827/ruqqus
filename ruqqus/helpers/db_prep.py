import psycopg2
from os import environ

conn = psycopg2.connect(environ.get("DATABASE_URL"))
c=conn.cursor()

'''
PostgreSQL server-side functions
For faster sorting and pagination
'''

#======= SUBMISSIONS =========

#ups
c.execute("""
CREATE OR REPLACE FUNCTION ups(submissions)
RETURNS bigint AS '
  SELECT COUNT(*)
  FROM votes
  LEFT JOIN users
  ON votes.user_id = users.id
  WHERE users.is_banned=false
    AND votes.vote_type=1
    AND votes.submission_id=$1.id
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#downs
c.execute("""
CREATE OR REPLACE FUNCTION downs(submissions)
RETURNS bigint AS '
  SELECT COUNT(*)
  FROM votes
  LEFT JOIN users
  ON votes.user_id = users.id
  WHERE users.is_banned=false
    AND votes.vote_type=-1
    AND votes.submission_id=$1.id
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#age
c.execute("""
CREATE OR REPLACE FUNCTION age(submissions)
RETURNS int AS '
  SELECT CAST( EXTRACT( EPOCH FROM CURRENT_TIMESTAMP) AS int) - $1.created_utc
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#score
c.execute("""
CREATE OR REPLACE FUNCTION score(submissions)
RETURNS bigint AS '
  SELECT ($1.ups - $1.downs)
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#rank hot
c.execute("""
CREATE OR REPLACE FUNCTION rank_hot(submissions)
RETURNS float AS '
  SELECT CAST(($1.ups - $1.downs) AS float)/((CAST(($1.age+100000) AS FLOAT)/6.0)^(1.0/3.0))
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#rank controversial
c.execute("""
CREATE OR REPLACE FUNCTION rank_fiery(submissions)
RETURNS float AS '
  SELECT SQRT(CAST(($1.ups * $1.downs) AS float))/((CAST(($1.age+100000) AS FLOAT)/6.0)^(1.0/3.0))
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#comment count
c.execute("""
CREATE OR REPLACE FUNCTION comment_count(submissions)
RETURNS bigint AS '
  SELECT COUNT(*)
  FROM comments
  WHERE is_banned=false
    AND parent_submission = $1.id
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#=========COMMENTS========

#ups
c.execute("""
CREATE OR REPLACE FUNCTION ups(comments)
RETURNS bigint AS '
  SELECT COUNT(*)
  FROM commentvotes
  LEFT JOIN users
  ON commentvotes.user_id = users.id
  WHERE users.is_banned=false
    AND commentvotes.vote_type=1
    AND commentvotes.comment_id=$1.id
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#downs
c.execute("""
CREATE OR REPLACE FUNCTION downs(comments)
RETURNS bigint AS '
  SELECT COUNT(*)
  FROM commentvotes
  LEFT JOIN users
  ON commentvotes.user_id = users.id
  WHERE users.is_banned=false
    AND commentvotes.vote_type=-1
    AND commentvotes.comment_id=$1.id
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#age
c.execute("""
CREATE OR REPLACE FUNCTION age(comments)
RETURNS int AS '
  SELECT CAST( EXTRACT( EPOCH FROM CURRENT_TIMESTAMP) AS int) - $1.created_utc
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#score
c.execute("""
CREATE OR REPLACE FUNCTION score(comments)
RETURNS bigint AS '
  SELECT ($1.ups - $1.downs)
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#rank hot
c.execute("""
CREATE OR REPLACE FUNCTION rank_hot(comments)
RETURNS float AS '
  SELECT CAST(($1.ups - $1.downs) AS float)/((CAST(($1.age+100000) AS FLOAT)/6.0)^(1.0/3.0))
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

#rank controversial
c.execute("""
CREATE OR REPLACE FUNCTION rank_fiery(comments)
RETURNS float AS '
  SELECT SQRT(CAST(($1.ups * $1.downs) AS float))/((CAST(($1.age+100000) AS FLOAT)/6.0)^(1.0/3.0))
  '
LANGUAGE SQL
IMMUTABLE
RETURNS NULL ON NULL INPUT;
""")

conn.commit()
c.close()
conn.close()