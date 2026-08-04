import pytest
from parsers.text_parser import TextParser

def test_salary_parser():
    parser = TextParser()
    text = [
        (1, "Rs. 56100 - 177500"),
        (2, "Level 10")
    ]
    res = parser.salary_parser(text)
    assert res['value'] in [56100, 100000] # Should prefer the Rs. string if confidence is higher
    assert res['confidence'] >= 0.8

def test_salary_parser_level():
    parser = TextParser()
    text = [(1, "Pay Level 10")]
    res = parser.salary_parser(text)
    assert res['value'] == 100000

def test_salary_parser_ctc():
    parser = TextParser()
    text = [(1, "Remuneration 45,000 - 60,000")]
    res = parser.salary_parser(text)
    assert res['value'] == 45000

def test_age_parser():
    parser = TextParser()
    text = [(1, "Maximum Age Limit 30 years. Age Relaxation up to 5 years for SC/ST.")]
    res = parser.age_parser(text)
    assert res['value']['max_age'] == 30
    assert res['value']['age_relaxation'] == "up to 5 years for SC/ST"

def test_experience_parser():
    parser = TextParser()
    text = [(1, "Minimum 5 years of post qualification experience in Python.")]
    res = parser.experience_parser(text)
    assert res['value'] == 5

def test_qualification_parser():
    parser = TextParser()
    text = [(1, "Essential Qualification: B.Tech in Computer Science from a recognized University. Desirable: M.Tech in AI.")]
    res = parser.qualification_parser(text)
    assert "B.Tech" in res['value']['essential_qual']
    assert "M.Tech" in res['value']['desirable_qual']

def test_vacancies_parser():
    parser = TextParser()
    text = [(1, "Total Vacancies: 25 UR-10 SC-5")]
    res = parser.vacancy_parser(text)
    assert res['value'] == 25

def test_important_dates_parser():
    parser = TextParser()
    text = [(1, "Opening Date: 01-Jan-2027. Closing Date: 31-Jan-2027. Exam Date: 15-Feb-2027")]
    res = parser.important_dates_parser(text)
    assert res['value']['app_start'].year == 2027
    assert res['value']['app_end'].month == 1
    assert res['value']['exam_date'].day == 15

def test_selection_process_parser():
    parser = TextParser()
    text = [(1, "The selection will be based on a Written Test followed by a Personal Interview and Document Verification.")]
    res = parser.selection_process_parser(text)
    val = res['value']
    assert "Written Test" in val or "CBT" in val
    assert "Interview" in val
    assert "Document Verification" in val

def test_mock_government_pdf_integrations():
    """Simulates multi-page extraction on Government org formats"""
    parser = TextParser()
    
    # 1. ISRO format
    isro_text = [(1, "ISRO Recruitment. Total Posts: 10"), (2, "Pay Level 10. Age limit 28 years.")]
    res = parser.parse_all(isro_text)
    assert res['vacancies']['value'] == 10
    assert res['salary']['value'] == 100000
    assert res['age']['value']['age_limit'] == 28
    
    # 2. RBI format
    rbi_text = [(1, "Reserve Bank of India. 5 years experience required. Closing Date 15-08-2026.")]
    res = parser.parse_all(rbi_text)
    assert res['experience']['value'] == 5
    assert res['dates']['value']['app_end'].year == 2026
