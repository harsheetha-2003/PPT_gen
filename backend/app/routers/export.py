# from fastapi import APIRouter

# router = APIRouter()

# @router.get("/")
# def export_document():
#     return {"message": "Export endpoint placeholder"}

# backend/app/routers/export.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.export_service import get_export_record

router = APIRouter(prefix="/api/export", tags=["export"])

@router.get("/download/{record_id}")
def download_export(record_id: int):
    rec = get_export_record(record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Export not found")
    path = rec.get("file_path")
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=os.path.basename(path))

