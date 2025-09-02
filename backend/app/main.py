
#===============================================================================================
# import json
# from fastapi import FastAPI, UploadFile, File, Form, Body
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Optional
# from routers import llm  # Import the updated llm helper
# from services import ppt_service

# app = FastAPI(title="PPTGenius API")

# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ------------------------------
# # Request model for presentation generation
# # ------------------------------
# class PresentationRequest(BaseModel):
#     prompt: str
#     temperature: float = 0.1
#     max_tokens: int = 1024
#     web_search: bool = False
#     web_depth: int = 2
#     youtube_links: Optional[List[str]] = []
#     youtube_depth: int = 2
#     audience: str = "General Public"
#     tone: str = "Formal"
#     style: str = "Corporate"
#     num_slides: int = 5
#     template: str = "Corporate"

# # ------------------------------
# # Generate Presentation Endpoint
# # ------------------------------
# @app.post("/generate_presentation")
# async def generate_presentation(
#     prompt: str = Form(...),
#     temperature: float = Form(0.1),
#     max_tokens: int = Form(1024),
#     web_search: bool = Form(False),
#     web_depth: int = Form(2),
#     youtube_links: Optional[str] = Form(""),
#     youtube_depth: int = Form(2),
#     audience: str = Form("General Public"),
#     tone: str = Form("Formal"),
#     style: str = Form("Corporate"),
#     num_slides: int = Form(5),
#     template: str = Form("Corporate"),
#     uploaded_file: Optional[UploadFile] = File(None)
# ):
#     """
#     Generate presentation with optional DDG / YouTube content and optional uploaded file.
#     """
#     # 1️⃣ Process uploaded document if present
#     if uploaded_file and uploaded_file.filename != "":
#         ext = uploaded_file.filename.split(".")[-1].lower()
#         content_bytes = await uploaded_file.read()
#         if ext in ["txt", "pdf", "docx"]:
#             document_content = await ppt_service.extract_text_from_file(uploaded_file, ext)
#         else:
#             document_content = ""
#     else:
#         document_content = ""

#     # 2️⃣ Convert youtube_links string to list if user provided
#     yt_links_list = [link.strip() for link in youtube_links.split(",") if link.strip()] if youtube_links else []

#     # 3️⃣ Prepare LLMRequest for slide generation
#     llm_request = llm.LLMRequest(
#         prompt=f"{prompt}\n{document_content}" if document_content else prompt,
#         temperature=temperature,
#         max_tokens=max_tokens,
#         web_search=web_search,
#         web_depth=web_depth,
#         youtube_links=yt_links_list,
#         youtube_depth=youtube_depth,
#         audience=audience,
#         tone=tone,
#         style=style
#     )

#     # 4️⃣ Generate slide content using llm helper
#     llm_response = llm.generate_slide_content(llm_request)
#     slides_json = llm_response.output

#     # 5️⃣ Generate actual PPTX
#     ppt_file_path = ppt_service.create_presentation(
#         slides_json=slides_json,
#         template=template,
#         num_slides=num_slides
#     )

#     return {
#         "ppt_file": ppt_file_path,
#         "llm_notes": llm_response.notes,
#         "error": llm_response.error
#     }

#==============================================================
# backend/app/main.py
# from fastapi import FastAPI, UploadFile, File, Form, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from typing import Optional
# from app.routers import llm as llm_router, image as image_router
# from app.utils import extract_text_from_file_bytes
# import os
# import logging

# # Setup logger
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# app = FastAPI(title="PPTGenius API")

# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# # include routers
# app.include_router(llm_router.router, prefix="/api/llm")
# app.include_router(image_router.router, prefix="/api/image")

# # Convenience endpoint mapping the form-based main you had
# @app.post("/generate_presentation_form")
# async def generate_presentation_form(
#     prompt: str = Form(...),
#     slides: int = Form(5),
#     template: str = Form("Professional"),
#     layout: str = Form("Mixed"),
#     images: bool = Form(True),
#     image_level: str = Form("medium"),
#     tone: str = Form("Formal"),
#     style: str = Form("Corporate"),
#     audience: str = Form("General Public"),
#     topic: str = Form(...),
#     additional_instructions: str = Form(""),
#     web_search: bool = Form(False),
#     web_depth: int = Form(None),
#     youtube_links: str = Form(""),
#     youtube_depth: int = Form(None),
#     uploaded_file: Optional[UploadFile] = File(None),
#     output_format: str = Form("pptx"),
#     temperature: float = Form(None),
#     max_tokens: int = Form(None)
# ):
#     # extract uploaded text
#     document_content = ""
#     if uploaded_file and uploaded_file.filename:
#         content_bytes = await uploaded_file.read()
#         ext = uploaded_file.filename.split(".")[-1].lower()
#         document_content = extract_text_from_file_bytes(content_bytes, ext)

#     youtube_list = [s.strip() for s in youtube_links.split(",") if s.strip()] if youtube_links else []

#     # prepare request for the LLM router
#     from app.routers.llm import GeneratePPTRequest
#     req = GeneratePPTRequest(
#         slides=slides,
#         template=template,
#         layout=layout,
#         images=images,
#         image_level=image_level,
#         tone=tone,
#         style=style,
#         audience=audience,
#         topic=topic,
#         additional_instructions=additional_instructions,
#         web_search=web_search,
#         web_depth=web_depth,
#         youtube_links=youtube_list,
#         youtube_depth=youtube_depth,
#         document_content=document_content,
#         temperature=temperature or None,
#         max_tokens=max_tokens or None,
#         output_format=output_format
#     )

#     logger.info(f"Generating PPT for topic: {topic}, output_format: {output_format}")\
#     # call router function directly
#     # return llm_router.generate_ppt(req)
#       # Call your LLM router function to generate the PPT
#     ppt_file_path = llm_router.generate_ppt(req)  # Should return absolute path of the generated file
#     if not os.path.exists(ppt_file_path):
#         logger.error("PPT generation failed, file not created.")
#         return {"error": "PPT generation failed."}

#     # Save PPT in database and get download link
#     record = save_and_record_export(
#         file_path=ppt_file_path,
#         topic=topic,
#         audience=audience,
#         output_format=output_format
#     )

#     logger.info(f"PPT saved and recorded with record_id: {record['record_id']}")

#     return {
#         "message": "PPT generated successfully.",
#         "download_url": record["download_url"],
#         "record_id": record["record_id"],
#         "file_path": ppt_file_path
#     }
# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from app.routers.llm import GeneratePPTRequest
from app.services.llm_service import generate_presentation_from_request
from app.utils import extract_text_from_file_bytes

app = FastAPI(title="PPTGenius API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/generate_presentation_form")
async def generate_presentation_form(
    prompt: str = Form(...),
    slides: int = Form(5),
    template: str = Form("Professional"),
    layout: str = Form("Mixed"),
    images: bool = Form(True),
    image_level: str = Form("medium"),
    tone: str = Form("Formal"),
    style: str = Form("Corporate"),
    audience: str = Form("General Public"),
    topic: str = Form(...),
    additional_instructions: str = Form(""),
    web_search: bool = Form(False),
    web_depth: int = Form(None),
    youtube_links: str = Form(""),
    youtube_depth: int = Form(None),
    uploaded_file: Optional[UploadFile] = File(None),
    output_format: str = Form("pptx"),
    temperature: float = Form(None),
    max_tokens: int = Form(None)
):
    # 1. Extract uploaded document content if provided
    document_content = ""
    if uploaded_file and uploaded_file.filename:
        content_bytes = await uploaded_file.read()
        ext = uploaded_file.filename.split(".")[-1].lower()
        document_content = extract_text_from_file_bytes(content_bytes, ext)

    # 2. Parse YouTube links as list
    youtube_list = [s.strip() for s in youtube_links.split(",") if s.strip()] if youtube_links else []

    # 3. Build request object
    req = GeneratePPTRequest(
        slides=slides,
        template=template,
        layout=layout,
        images=images,
        image_level=image_level,
        tone=tone,
        style=style,
        audience=audience,
        topic=topic,
        additional_instructions=additional_instructions,
        web_search=web_search,
        web_depth=web_depth,
        youtube_links=youtube_list,
        youtube_depth=youtube_depth,
        document_content=document_content,
        temperature=temperature or None,
        max_tokens=max_tokens or None,
        output_format=output_format
    )

    # 4. Call the unified PPT generation function
    result = generate_presentation_from_request(req)

    # 5. Return JSON with download URL
    return {
        "download_url": result.get("download_url"),
        "llm_notes": result.get("llm_notes"),
        "error": result.get("error")
    }
