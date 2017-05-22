from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class Reader(Base):
  __tablename__ = 'reader'

  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  email = Column(String(250), nullable=False)
  
  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
           'name'         : self.name,
           'id'           : self.id,
           'email'        : self.email,
           }


class Bookbin(Base):
  __tablename__ = 'bookbin'

  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  reader_id = Column(Integer, ForeignKey('reader.id'))
  reader = relationship(Reader)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
           'name'         : self.name,
           'id'           : self.id,
       }
 

class Book(Base):
  __tablename__ = 'book'

  title = Column(String(250), nullable = False)
  id = Column(Integer, primary_key = True)
  author = Column(String(250))
  pub_year = Column(String(80))
  genre = Column(String(250))
  description = Column(Text)
  bookbin_id = Column(Integer, ForeignKey('bookbin.id'))
  bookbin = relationship(Bookbin)
  reader_id = Column(Integer, ForeignKey('reader.id'))
  reader = relationship(Reader)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
           'title'         : self.titlei,
           'description'  : self.description,
           'id'           : self.id,
           }


engine = create_engine('sqlite:///bookrecommendations.db')
 

Base.metadata.create_all(engine)