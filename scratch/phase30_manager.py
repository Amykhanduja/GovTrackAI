import os
import re

manager_path = "/mnt/c/Users/khand/GovTrackAI/scrapers/manager.py"
with open(manager_path, "r") as f:
    code = f.read()

# Replace the scraping logic inside manager.py to include confidence score checking and logging

replacement_code = """                    # --- NEW PARSER ARCHITECTURE INTEGRATION ---
                    # Only parse if we lack info or need to update
                    nlp = extract_details_from_url(job.url, org.name)
                    
                    # Log extracted fields
                    for field, conf in nlp.get('confidence_scores', {}).items():
                        logger.info(f"{field.capitalize()} extracted - Confidence {conf:.2f}")

                    existing = db.query(Job).filter_by(url=job.url).first()
                    if not existing:
                        new_job = Job(
                            organization_id=org.id,
                            title=job.title,
                            url=job.url,
                            domain=job.domain,
                            salary=nlp['salary'],
                            vacancies=nlp['vacancies'],
                            deadline=nlp['deadline'],
                            age_limit=nlp['age_limit'],
                            qualification=nlp['qualification'],
                            experience_years=nlp['experience_years'],
                            status=self.calc_status(nlp['deadline'])
                        )
                        db.add(new_job)
                        db.commit()
                        db.refresh(new_job)
                        
                        # Store AI Extract
                        doc = JobDocument(
                            job_id=new_job.id,
                            pdf_path="",
                            extracted_text="",
                            parsed_fields=json.dumps(nlp),
                            extracted_tables="[]",
                            ai_summary=generate_ai_summary("", nlp),
                            eligibility_status=calculate_eligibility(nlp)[0],
                            eligibility_reason=calculate_eligibility(nlp)[1]
                        )
                        db.add(doc)
                        self.stats['jobs_added'] += 1

                    else:
                        updated = False
                        
                        # Confidence-based overwriting
                        old_doc = db.query(JobDocument).filter_by(job_id=existing.id).first()
                        old_conf = {}
                        if old_doc and old_doc.parsed_fields:
                            try: old_conf = json.loads(old_doc.parsed_fields).get('confidence_scores', {})
                            except: pass
                            
                        new_conf = nlp.get('confidence_scores', {})
                        
                        if nlp['salary'] and (not existing.salary or new_conf.get('salary', 0) > old_conf.get('salary', 0)):
                            existing.salary = nlp['salary']
                            updated = True
                        if nlp['vacancies'] and (not existing.vacancies or new_conf.get('vacancies', 0) > old_conf.get('vacancies', 0)):
                            existing.vacancies = nlp['vacancies']
                            updated = True
                        if nlp['deadline'] and (not existing.deadline or new_conf.get('dates', 0) > old_conf.get('dates', 0)):
                            existing.deadline = nlp['deadline']
                            updated = True
                        if nlp['qualification'] and (not existing.qualification or new_conf.get('qualification', 0) > old_conf.get('qualification', 0)):
                            existing.qualification = nlp['qualification']
                            updated = True
                        if nlp['age_limit'] and (not existing.age_limit or new_conf.get('age', 0) > old_conf.get('age', 0)):
                            existing.age_limit = nlp['age_limit']
                            updated = True
                            
                        # Recalculate status
                        new_status = self.calc_status(existing.deadline)
                        if existing.status != new_status:
                            existing.status = new_status
                            updated = True
                            
                        if updated:
                            if old_doc:
                                old_doc.parsed_fields = json.dumps(nlp)
                            self.stats['jobs_updated'] += 1
"""

# We need to accurately replace the inner loop
# Looking at manager.py, it starts with:
# nlp = extract_details_from_url(job.url, org.name)
# ... down to self.stats['jobs_updated'] += 1

# I will just write a simpler patch script for manager.py
code = re.sub(r'nlp = extract_details_from_url.*?self\.stats\[\'jobs_updated\'\] \+= 1', replacement_code, code, flags=re.DOTALL)

with open(manager_path, "w") as f:
    f.write(code)
