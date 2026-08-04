from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text

Base = declarative_base()

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    website = Column(String)
    ministry = Column(String)

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'))
    title = Column(String, nullable=False)
    description = Column(Text)
    salary = Column(Integer, default=0)
    vacancies = Column(Integer, default=0)
    deadline = Column(DateTime)
    created_at = Column(DateTime)
    skills = Column(Text)
    url = Column(String)
    domain = Column(String)
    
    qualification = Column(String)
    age_limit = Column(Integer)
    experience_years = Column(Integer)
    
    status = Column(String, default="New")
    priority = Column(Integer, default=0)
    is_hidden = Column(Boolean, default=False)
    is_trashed = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_applied = Column(Boolean, default=False)

class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    status = Column(String)
    applied_at = Column(DateTime)

class Exam(Base):
    __tablename__ = 'exams'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    exam_date = Column(DateTime)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    published_at = Column(DateTime)

class AISummary(Base):
    __tablename__ = 'ai_summaries'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    summary_text = Column(Text)
    generated_at = Column(DateTime)

class JobDocument(Base):
    __tablename__ = 'job_documents'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    pdf_path = Column(String)
    extracted_text = Column(Text)
    parsed_fields = Column(Text)
    extracted_tables = Column(Text)
    ai_summary = Column(Text)
    eligibility_status = Column(String)
    eligibility_reason = Column(Text)
    version = Column(Integer, default=1)
