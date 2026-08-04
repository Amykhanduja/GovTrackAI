from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from excel.generator import ExcelGenerator
from excel.importer import ExcelImporter
import os
import shutil
import logging

logger = logging.getLogger('app.excel_sync')
router = APIRouter(prefix="/excel", tags=["Excel"])

@router.get("/export")
def export_excel(domain: str = Query(None)):
    generator = ExcelGenerator()
    path = generator.generate_dashboard(domain=domain)
    dl_name = f"GovTrackAI_{domain or 'Tracker'}.xlsx"
    return FileResponse(path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=dl_name)

@router.post("/import")
def import_excel(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(400, "Only .xlsx files are supported")
        
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        importer = ExcelImporter()
        updated = importer.import_data(temp_path)
        
        return {"status": "success", "updated_count": updated}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/backup")
def force_backup(domain: str = Query(None)):
    generator = ExcelGenerator()
    path = generator.generate_dashboard(domain=domain)
    return {"status": "success", "message": "Backup created successfully"}
