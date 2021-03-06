---
title: Ruqqus Design Doc
---

# Design

The purpose of this document is to clearly identify:

* Project goals
* Project requirements to meet those goals
* Project specifications to meet those requirements

## Goals

1. Provide a place where users deplatformed from other sites can share news, meme, and otherwise interact.

## Requirements

### General

1. To the greatest extent possible, mimic reddit functionality as it applies to /r/the_donald (Quarantine/ban status notwithstanding)
2. Use reddit oauth to verify reddit name if desired
3. Use email verification to increase account permissions
4. No advertising, donations only (to avoid contractual obligations to advertisers)

### UX

1. Allow submission of links and text
2. Allow commenting on submissions
3. Allow commenting on comments
4. Allow up/down voting on submissions and comments
5. Sort submissions by new, hot, etc
6. Allow users to delete their own content
7. Allow users to report rule-breaking submissions and comments

### Administration

Several layers of administrative privilege will be implemented

Integer|Name|Suggested permissions|Type of user
-|-|-|-
0|User|None|Everyone and anyone
1|Junior Mod|Remove content. Flag accounts for higher review.|Helpful users
2|Senior Mod|Issue 24hr bans|Particularly helpful users with a good track record 
3|Junior Admin|Issue permanent bans. Promote/demote users up to level 2 | New admins. Signed volunteer agreement required.
4|Senior Admin|See IP/tech info not visible to lower ranks.|Trust+Safety
5|Deputy Owner|Promote/demote users up to level 4|Active contributors and developers
6|Owner|Direct Heroku/database access|captainmeta4. Maybe a select few others.

## Specifications

### Stack 

Layer|Tech
-|-
Host|Heroku
WSGI|Gunicorn
Server|Python Flask
ORM|SQLalchemy
Database|PostgreSQL

### Security

1. Password column is salted and hashed - no plaintext
2. Failure to login error does not specify if username or password is incorrect
3. Industry standard cryptography (or better, where possible) used everywhere appropriate
4. Form tokens used to prevent CSRF

### Budget

During development, free resources are used. As the platform is launched, resources will be upgraded/migrated to paid variants

Service|Plan|Function|Justification|Upgrade Timing|$/month
-|-|-|-|-|-
Heroku PostgreSQL|Standard 0|Database|Rollbacks, fork+follow, no row limit, 64GB storage|As 10k row limit on free db is approached|$50|
Adminium|Startup|Database Administration|Removes 5 table cap|Once a 6th table is needed|$10
Heroku Dynos|Hobby|Run the server|Performance metrics, no sleeping|Already done|$7
Papertrail|Choklad|Logging|Log searching beyond 2 days not yet needed |n/a|$0
Mailgun|Concept|Email sending|Email verification and password resets |n/a|$0
**Total**|||||$67
