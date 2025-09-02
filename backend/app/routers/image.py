# from fastapi import APIRouter
# from pydantic import BaseModel
# import os
# import base64
# import uuid

# router = APIRouter()
# OUTPUT_DIR = "generated_images"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Request/response schemas
# class ImageRequest(BaseModel):
#     prompt: str
#     n: int = 1
#     size: str = "512x512"

# class ImageResponse(BaseModel):
#     images: list  # list of file paths


# # Primary: Stable Diffusion
# def call_stable_diffusion(prompt, n=1, size="512x512"):
#     images = []
#     for _ in range(n):
#         file_path = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.png")
#         # Here you would integrate actual SD API
#         # For now, create a dummy placeholder
#         with open(file_path, "wb") as f:
#             f.write(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAqUBWbWw4ZkAAAAASUVORK5CYII="))
#         images.append(file_path)
#     return images


# # Fallback: LLaMA-4 Maverick
# def call_llama_maverick(prompt, n=1, size="512x512"):
#     images = []
#     for _ in range(n):
#         file_path = os.path.join(OUTPUT_DIR, f"fallback_{uuid.uuid4()}.png")
#         with open(file_path, "wb") as f:
#             f.write(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAqUBWbWw4ZkAAAAASUVORK5CYII="))
#         images.append(file_path)
#     return images


# @router.post("/generate_image", response_model=ImageResponse)
# def generate_image(request: ImageRequest):
#     try:
#         imgs = call_stable_diffusion(request.prompt, request.n, request.size)
#     except Exception:
#         imgs = call_llama_maverick(request.prompt, request.n, request.size)
#     return ImageResponse(images=imgs)

#=================================================================================================
# backend/app/routers/image.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.image_service import generate_images_for_prompt

router = APIRouter()

class ImageReq(BaseModel):
    prompt: str
    n: int = 1
    size: str = "512x512"

class ImageResp(BaseModel):
    images: List[str]

@router.post("/generate_image", response_model=ImageResp)
def generate_image_endpoint(req: ImageReq):
    try:
        imgs = generate_images_for_prompt(req.prompt, n=req.n, size=req.size)
        return {"images": imgs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
