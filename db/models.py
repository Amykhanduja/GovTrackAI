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

class RecruitmentHistory(Base):
    __tablename__ = 'recruitment_history'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'))
    department = Column(String)
    recruitment_name = Column(String)
    advt_no = Column(String)
    notification_date = Column(DateTime)
    app_start = Column(DateTime)
    app_end = Column(DateTime)
    exam_date = Column(DateTime)
    interview_date = Column(DateTime)
    joining_date = Column(DateTime)
    post_name = Column(String)
    vacancies = Column(Integer)
    salary = Column(String)
    qualification = Column(String)
    experience = Column(Integer)
    age_limit = Column(Integer)
    official_pdf = Column(String)
    official_link = Column(String)
    status = Column(String)  # Active, Expired, Cancelled, Superseded, Archived
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=True)

class RecruitmentCycle(Base):
    __tablename__ = 'recruitment_cycles'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'))
    post_name = Column(String)
    cycle_year = Column(Integer)
    month = Column(Integer)
    vacancies = Column(Integer)
    frequency_months = Column(Integer)

class HistoricalVacancy(Base):
    __tablename__ = 'historical_vacancies'
    id = Column(Integer, primary_key=True)
    history_id = Column(Integer, ForeignKey('recruitment_history.id'))
    vacancies = Column(Integer)

class HistoricalSalary(Base):
    __tablename__ = 'historical_salaries'
    id = Column(Integer, primary_key=True)
    history_id = Column(Integer, ForeignKey('recruitment_history.id'))
    salary_text = Column(String)
    pay_level = Column(String)

class HistoricalEligibility(Base):
    __tablename__ = 'historical_eligibilities'
    id = Column(Integer, primary_key=True)
    history_id = Column(Integer, ForeignKey('recruitment_history.id'))
    qualification = Column(String)
    experience = Column(Integer)
    age_limit = Column(Integer)

class HistoricalDeadline(Base):
    __tablename__ = 'historical_deadlines'
    id = Column(Integer, primary_key=True)
    history_id = Column(Integer, ForeignKey('recruitment_history.id'))
    app_end = Column(DateTime)

class RecruitmentTrend(Base):
    __tablename__ = 'recruitment_trends'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'))
    avg_vacancies = Column(Integer)
    avg_salary_growth = Column(String)
    recruitment_frequency = Column(String)
    trend_analysis = Column(Text)

class NotificationArchive(Base):
    __tablename__ = 'notification_archives'
    id = Column(Integer, primary_key=True)
    history_id = Column(Integer, ForeignKey('recruitment_history.id'))
    document_path = Column(String)
    archive_date = Column(DateTime)

class PredictionCache(Base):
    __tablename__ = 'prediction_cache'
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'))
    likely_month = Column(String)
    likely_year = Column(Integer)
    expected_vacancies = Column(Integer)
    expected_eligibility = Column(String)
    confidence_score = Column(Integer)
    generated_at = Column(DateTime)
