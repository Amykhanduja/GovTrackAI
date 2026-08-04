from parsers.base_parser import BaseParser
import re
import dateparser
import logging

logger = logging.getLogger(__name__)

class TextParser(BaseParser):
    def _create_result(self, value, confidence, page, text_snippet):
        return {
            "value": value,
            "confidence": confidence,
            "source_page": page,
            "source_text": text_snippet.strip()
        }

    def salary_parser(self, pages_text: list) -> dict:
        best_match = None
        highest_conf = 0
        for page_num, text in pages_text:
            match = re.search(r'((?:Rs\.?|₹|INR|Salary|Pay Scale|Remuneration)[\s]*[0-9,]{4,}(?:\s*-\s*[0-9,]{4,})?)/?|-?\s*(?:Pay\s*)?Level\s*[0-9]{1,2}', text, re.IGNORECASE)
            if match:
                snippet = match.group(0)
                val_str = match.group(1)
                conf = 0.85
                if '₹' in snippet or 'Rs' in snippet: conf = 0.96
                
                parsed_val = 0
                if val_str:
                    try:
                        clean = re.sub(r'[^0-9-]', '', val_str)
                        parsed_val = int(clean.split('-')[0])
                    except Exception as e: logger.debug(f'Parsing error: {e}')
                else:
                    level_match = re.search(r'Level\s*([0-9]{1,2})', snippet, re.IGNORECASE)
                    if level_match:
                        parsed_val = int(level_match.group(1)) * 10000
                
                if parsed_val > 0 and conf > highest_conf:
                    highest_conf = conf
                    best_match = self._create_result(parsed_val, conf, page_num, snippet)
                    
            match2 = re.search(r'([0-9]{2,3},[0-9]{3})\s*-\s*([0-9]{2,3},[0-9]{3})', text)
            if match2:
                try: 
                    parsed_val = int(match2.group(1).replace(',', ''))
                    conf = 0.70
                    if parsed_val > 0 and conf > highest_conf:
                        highest_conf = conf
                        best_match = self._create_result(parsed_val, conf, page_num, match2.group(0))
                except Exception as e: logger.debug(f'Parsing error: {e}')
        return best_match or self._create_result(0, 0.0, None, "")

    def vacancy_parser(self, pages_text: list) -> dict:
        best_match = None
        highest_conf = 0
        for page_num, text in pages_text:
            match = re.search(r'((?:Total|No\.\s*of|Number of)?\s*(?:Vacancies|Posts|Positions|Post)[\s:-]*(\d{1,4}))', text, re.IGNORECASE)
            if match:
                try: 
                    val = int(match.group(2))
                    conf = 0.92
                    if conf > highest_conf:
                        highest_conf = conf
                        best_match = self._create_result(val, conf, page_num, match.group(1))
                except Exception as e: logger.debug(f'Parsing error: {e}')
            
            match2 = re.search(r'((\d{1,4})\s*(?:vacancies|posts|positions))', text, re.IGNORECASE)
            if match2:
                try:
                    val = int(match2.group(2))
                    conf = 0.75
                    if conf > highest_conf:
                        highest_conf = conf
                        best_match = self._create_result(val, conf, page_num, match2.group(1))
                except Exception as e: logger.debug(f'Parsing error: {e}')
        return best_match or self._create_result(0, 0.0, None, "")

    def age_parser(self, pages_text: list) -> dict:
        age_limit, min_age, max_age, age_relax = None, None, None, None
        best_page, best_snippet, highest_conf = None, "", 0
        for page_num, text in pages_text:
            match_max = re.search(r'((?:Upper|Maximum) Age(?: Limit)?[\s:-]*(\d{2})\s*(?:years|yrs)?)', text, re.IGNORECASE)
            if match_max: 
                max_age = int(match_max.group(2))
                highest_conf, best_page, best_snippet = 0.95, page_num, match_max.group(1)
            
            match_min = re.search(r'((?:Lower|Minimum) Age(?: Limit)?[\s:-]*(\d{2})\s*(?:years|yrs)?)', text, re.IGNORECASE)
            if match_min: 
                min_age = int(match_min.group(2))
                if highest_conf < 0.95: highest_conf, best_page, best_snippet = 0.90, page_num, match_min.group(1)
            
            match_gen = re.search(r'((?:Age Limit)[\s:-]*(?:up to\s*|Not exceeding\s*)?(\d{2})\s*(?:years|yrs))', text, re.IGNORECASE)
            if match_gen: 
                age_limit = int(match_gen.group(2))
                if highest_conf < 0.90: highest_conf, best_page, best_snippet = 0.85, page_num, match_gen.group(1)
            
            match_relax = re.search(r'((?:Age Relaxation)[\s:-]*(.+?)(?:\.|\n))', text, re.IGNORECASE)
            if match_relax: 
                age_relax = match_relax.group(2).strip()
        
        if max_age and not age_limit: age_limit = max_age
        
        val = {
            "age_limit": age_limit,
            "min_age": min_age,
            "max_age": max_age,
            "age_relaxation": age_relax
        }
        return self._create_result(val, highest_conf, best_page, best_snippet)

    def experience_parser(self, pages_text: list) -> dict:
        best_match = None
        highest_conf = 0
        for page_num, text in pages_text:
            match = re.search(r'((\d+)\s*(?:years|yrs)[\s]*(?:experience|of post qualification))', text, re.IGNORECASE)
            if match:
                try: 
                    val = int(match.group(2))
                    conf = 0.90
                    if conf > highest_conf:
                        highest_conf = conf
                        best_match = self._create_result(val, conf, page_num, match.group(1))
                except Exception as e: logger.debug(f'Parsing error: {e}')
            
            match2 = re.search(r'((?:Experience)[\s:-]*(\d+)\s*(?:years|yrs))', text, re.IGNORECASE)
            if match2:
                try: 
                    val = int(match2.group(2))
                    conf = 0.85
                    if conf > highest_conf:
                        highest_conf = conf
                        best_match = self._create_result(val, conf, page_num, match2.group(1))
                except Exception as e: logger.debug(f'Parsing error: {e}')
        return best_match or self._create_result(None, 0.0, None, "")

    def qualification_parser(self, pages_text: list) -> dict:
        qual, ess, des = None, None, None
        highest_conf = 0
        best_page, best_snippet = None, ""
        for page_num, text in pages_text:
            match_ess = re.search(r'((?:Essential|Minimum) Qualification[\s:-]*(.+?))(?:Desirable|\Z)', text, re.IGNORECASE | re.DOTALL)
            if match_ess: 
                ess = match_ess.group(2).strip()[:200].replace('\n', ' ')
                highest_conf, best_page, best_snippet = 0.95, page_num, match_ess.group(1)[:100]
            
            match_des = re.search(r'((?:Desirable)(?:\s*Qualification)?[\s:-]*(.+?))(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
            if match_des: des = match_des.group(2).strip()[:200].replace('\n', ' ')
            
            match = re.search(r'((?:Qualification|Eligibility|Education)[\s:-]*([A-Za-z\s,.\/]+(?:Degree|Diploma|B\.E|B\.Tech|M\.Tech|Ph\.D|B\.Sc|M\.Sc|M\.A|B\.A|Masters|Bachelors|10th|12th|Graduation)))', text, re.IGNORECASE)
            if match: 
                qual = match.group(2).strip()[:100]
                if highest_conf < 0.90: highest_conf, best_page, best_snippet = 0.85, page_num, match.group(1)
        
        if ess and not qual: qual = ess[:100]
        val = {"qualification": qual, "essential_qual": ess, "desirable_qual": des}
        return self._create_result(val, highest_conf, best_page, best_snippet)

    def important_dates_parser(self, pages_text: list) -> dict:
        app_start, app_end, exam, interview = None, None, None, None
        highest_conf = 0
        best_page, best_snippet = None, ""
        for page_num, text in pages_text:
            match_start = re.search(r'((?:Opening Date|Start Date|Commencement)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4}))', text, re.IGNORECASE)
            if match_start:
                dt = dateparser.parse(match_start.group(2))
                if dt: 
                    app_start = dt
                    highest_conf, best_page, best_snippet = 0.95, page_num, match_start.group(1)
                
            match_end = re.search(r'((?:Last Date|Closing Date|Deadline|Apply till)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4}))', text, re.IGNORECASE)
            if match_end:
                dt = dateparser.parse(match_end.group(2))
                if dt: 
                    app_end = dt
                    if highest_conf < 0.95: highest_conf, best_page, best_snippet = 0.95, page_num, match_end.group(1)
                
            match_exam = re.search(r'((?:Exam Date|Date of CBT|Written Test)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4}))', text, re.IGNORECASE)
            if match_exam:
                dt = dateparser.parse(match_exam.group(2))
                if dt: exam = dt
                
            match_int = re.search(r'((?:Interview Date|Date of Interview)[\s:-]*([0-9]{1,2}[\s\-/A-Za-z]+[0-9]{2,4}))', text, re.IGNORECASE)
            if match_int:
                dt = dateparser.parse(match_int.group(2))
                if dt: interview = dt
                
        val = {"app_start": app_start, "app_end": app_end, "exam_date": exam, "interview_date": interview}
        return self._create_result(val, highest_conf, best_page, best_snippet)

    def selection_process_parser(self, pages_text: list) -> dict:
        processes = []
        highest_conf = 0
        best_page, best_snippet = None, ""
        for page_num, text in pages_text:
            t = text.lower()
            found = False
            if 'written test' in t or 'cbt' in t or 'computer based test' in t: processes.append("Written Test / CBT"); found = True
            if 'interview' in t or 'personal interview' in t: processes.append("Interview"); found = True
            if 'skill test' in t or 'trade test' in t or 'typing test' in t: processes.append("Skill/Trade Test"); found = True
            if 'document verification' in t or 'dv' in t: processes.append("Document Verification"); found = True
            if 'medical examination' in t: processes.append("Medical Examination"); found = True
            
            if found and highest_conf == 0:
                highest_conf, best_page, best_snippet = 0.85, page_num, "Matched keywords for selection process"
        
        return self._create_result(", ".join(set(processes)) if processes else None, highest_conf, best_page, best_snippet)

    def parse_all(self, pages_text: list) -> dict:
        return {
            "salary": self.salary_parser(pages_text),
            "vacancies": self.vacancy_parser(pages_text),
            "age": self.age_parser(pages_text),
            "experience": self.experience_parser(pages_text),
            "qualification": self.qualification_parser(pages_text),
            "dates": self.important_dates_parser(pages_text),
            "selection_process": self.selection_process_parser(pages_text)
        }

    def parse(self, source: str, **kwargs) -> dict:
        # source here is expected to be a list of pages [(page_num, text)] or plain text
        if isinstance(source, str):
            source = [(1, source)]
        try:
            structured = self.parse_all(source)
            text_combined = "\n".join([p[1] for p in source])
            return self._standard_response(
                parser_name="text_field_extractor",
                success=True,
                text=text_combined,
                structured_data=structured,
                confidence=0.9
            )
        except Exception as e:
            logger.error(f"TextParser parse failed: {e}")
            return self._standard_response(parser_name="text_field_extractor", success=False, confidence=0.0)
