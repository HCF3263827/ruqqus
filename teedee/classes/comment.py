from flask import render_template
from teedee.helpers.base36 import *
from teedee.__main__ import Base, db
from time import strftime
from sqlalchemy import *
from .user import User
from .submission import Submission

class Comment(Base):

    __tablename__="Comments"

    id = Column(BigInteger, primary_key=True)
    author_id = Column(BigInteger, ForeignKey(User.id))
    body = Column(String(2000), default=None)
    parent_submission = Column(BigInteger, ForeignKey(Submission.id))
    parent_comment = Column(BigInteger) #this column is foreignkeyed to comment(id) but we can't do that yet as "comment" class isn't yet defined
    created_utc = Column(BigInteger, default=0)
    is_banned = Column(Boolean, default=False)

    def __repr__(self):
        return "<Comment(id=%s, author_id=%s, body=%s, parent_submission=%s, " \
               "parent_comment=%s, created_utc=%s, is_banned=%s)>" \
               "" % (self.id, self.author_id, self.body, self.parent_submission,
                   self.parent_comment, self.created_utc, self.is_banned)
 
    
    @property
    def base36id(self):
        return base36encode(self.id)
