# # app/routers/routing.py
# from fastapi import APIRouter

# router = APIRouter()

# @router.get("/")
# def route_document():
#     return {"message": "Routing endpoint placeholder"}

# app/routers/router.py
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from app.services.export_service import export_presentation
import os

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/")
def export_file(
    export_id: str = Query(..., description="Unique export job ID"),
    format: str = Query(..., description="Export format (pptx or pdf only)"),
):
    # ✅ Strictly enforce PPTX/PDF only
    allowed_formats = ["pptx", "pdf"]
    if format.lower() not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid export format '{format}'. Only {allowed_formats} are supported."
        )

    # ✅ Call the service
    file_path = export_presentation(export_id, format.lower())

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Export failed: File not found for export_id={export_id}, format={format}"
        )

    # ✅ Return the file response
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        if format.lower() == "pptx"
        else "application/pdf"
    )
