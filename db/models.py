from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text

Base = declarative_base()

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    website = Column(String)

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'))
    title = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime)

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

class DownloadedFile(Base):
    __tablename__ = 'downloaded_files'
    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    downloaded_at = Column(DateTime)

class AISummary(Base):
    __tablename__ = 'ai_summaries'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    summary_text = Column(Text)
    generated_at = Column(DateTime)

class SchedulerHistory(Base):
    __tablename__ = 'scheduler_history'
    id = Column(Integer, primary_key=True)
    job_name = Column(String)
    executed_at = Column(DateTime)
    status = Column(String)

class NotificationHistory(Base):
    __tablename__ = 'notification_history'
    id = Column(Integer, primary_key=True)
    channel = Column(String)
    sent_at = Column(DateTime)

class UserSettings(Base):
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True)
    setting_key = Column(String)
    setting_value = Column(String)

class SystemMetadata(Base):
    __tablename__ = 'system_metadata'
    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
