from flask import *
from sqlalchemy import *
from ruqqus.__main__ import Base, db

class IP(Base):

    __tablename__="ips"

    id=Column(Integer, primary_key=True)
    addr=Column(String(64))
    reason=Column(String(256), default="")
    banned_by=Column(Boolean, ForeignKey("users.id"), default=True)

class Agent(Base):

    __tablename__="useragents"

    id=Column(Integer, primary_key=True)
    kwd=Column(String(64))
    reason=Column(String(256), default="")
    banned_by=Column(Boolean, ForeignKey("users.id"), default=True)
