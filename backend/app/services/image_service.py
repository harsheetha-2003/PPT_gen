# # backend/app/services/image_service.py
# import os, requests, base64
# from typing import List
# from app import config
# from app.utils import save_image_from_url_or_b64, download_and_save_images
# from fastapi import HTTPException

# OUT_DIR = config.OUTPUT_IMAGE_DIR
# os.makedirs(OUT_DIR, exist_ok=True)

# def generate_images_for_prompt(prompt: str, n: int = 1, size: str = "512x512") -> List[str]:
#     if not config.STABLE_DIFFUSION_API_URL or not config.STABLE_DIFFUSION_API_KEY:
#         raise HTTPException(status_code=500, detail="Stable Diffusion API not configured")
#     headers = {"Authorization": f"Bearer {config.STABLE_DIFFUSION_API_KEY}", "Content-Type": "application/json"}
#     payload = {"prompt": prompt, "n": n, "size": size}
#     r = requests.post(config.STABLE_DIFFUSION_API_URL, headers=headers, json=payload, timeout=60)
#     if r.status_code != 200:
#         raise HTTPException(status_code=r.status_code, detail=f"Diffusion API failed: {r.text}")
#     resp = r.json()
#     saved = []
#     # handle common shapes: images as urls or base64 in artifacts
#     if isinstance(resp.get("images"), list) and len(resp.get("images"))>0:
#         items = resp.get("images")
#         # images may be urls or base64
#         urls = [it for it in items if isinstance(it, str) and it.startswith("http")]
#         if urls:
#             saved = download_and_save_images(urls, out_dir=OUT_DIR)
#         else:
#             # assume base64
#             for b64 in items:
#                 try:
#                     if "," in b64:
#                         payload = b64.split(",",1)[1]
#                     else:
#                         payload = b64
#                     img_bytes = base64.b64decode(payload)
#                     p = save_image_from_url_or_b64("data:image/png;base64,"+payload, OUT_DIR)
#                     if p:
#                         saved.append(p)
#                 except Exception:
#                     continue
#     elif isinstance(resp.get("artifacts"), list):
#         for art in resp.get("artifacts"):
#             b64 = art.get("base64") or art.get("b64_json") or art.get("b64")
#             if b64:
#                 try:
#                     if "," in b64:
#                         payload = b64.split(",",1)[1]
#                     else:
#                         payload = b64
#                     p = save_image_from_url_or_b64("data:image/png;base64,"+payload, OUT_DIR)
#                     if p:
#                         saved.append(p)
#                 except Exception:
#                     continue
#     else:
#         # try to find urls anywhere
#         urls=[]
#         for v in resp.values():
#             if isinstance(v, str) and v.startswith("http"):
#                 urls.append(v)
#             if isinstance(v, list):
#                 for item in v:
#                     if isinstance(item,str) and item.startswith("http"):
#                         urls.append(item)
#         if urls:
#             saved = download_and_save_images(urls, out_dir=OUT_DIR)
#     if not saved:
#         raise HTTPException(status_code=500, detail="No images produced by SD API")
#     return saved

#=========================================================
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.db import save_generated_file, delete_expired_files, get_db_connection
from app.services.export_service import get_file_path
from app.utils import call_primary_image_gen, call_fallback_image_gen
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Router for image operations
router = APIRouter(prefix="/image", tags=["Image Service"])

# Ensure generated images directory exists
GENERATED_IMAGES_DIR = os.path.join(os.getcwd(), "generated_images")
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)


class ImageRequest(BaseModel):
    prompt: str
    size: Optional[str] = "1024x1024"
    ttl: Optional[int] = 600  # seconds (default: 10 min)


@router.post("/generate")
async def generate_image(request: ImageRequest) -> Dict[str, Any]:
    """
    Generate an image using the primary provider, with fallback if needed.
    Stores the image file, tracks TTL in SQLite.
    """
    db = next(get_db())

    try:
        # --- Call Primary Image Gen ---
        result = call_primary_image_gen(request.prompt, request.size)

        if not result or "image_bytes" not in result:
            # --- Fallback if primary fails ---
            result = call_fallback_image_gen(request.prompt, request.size)

        if not result or "image_bytes" not in result:
            raise HTTPException(status_code=500, detail="Image generation failed")

        # --- Save image ---
        file_id = str(uuid.uuid4())
        file_name = f"{file_id}.png"
        file_path = os.path.join(GENERATED_IMAGES_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(result["image_bytes"])

        # --- Save to DB with TTL ---
        save_generated_file(
            db=db,
            file_id=file_id,
            file_type="image",
            file_path=file_path,
            ttl_seconds=request.ttl
        )

        # --- Cleanup expired files ---
        delete_expired_files(db)

        return {
            "status": "success",
            "file_id": file_id,
            "file_path": file_path,
            "download_url": f"/download/{file_id}",
            "expires_in": request.ttl
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")


@router.get("/status/{file_id}")
async def check_image_status(file_id: str) -> Dict[str, Any]:
    """
    Check if the image is still available before TTL expiry.
    """
    db = next(get_db())
    cursor = db.cursor()
    cursor.execute("SELECT file_id, file_path, expires_at FROM generated_files WHERE file_id=? AND file_type='image'", (file_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Image not found or expired")

    return {
        "file_id": row[0],
        "file_path": row[1],
        "expires_at": row[2]
    }

def generate_images_for_prompt(
    prompt: str,
    negative_prompt: Optional[str] = None,
    size: str = "1024x1024",
    n: int = 1
) -> List[str]:
    """
    Generate images for a given prompt using the primary image generation model (Stable Diffusion)
    and fallback model (LLaMA-4-Maverick) if the primary fails.

    Args:
        prompt (str): Text prompt describing the desired image.
        negative_prompt (Optional[str]): Text describing what should be avoided in the image.
        size (str): Resolution of generated images (default "1024x1024").
        n (int): Number of images to generate (default 1).

    Returns:
        List[str]: URLs of generated images.
    """
    try:
        # Attempt primary image generation
        logger.info("[ImageService] Generating images using primary model...")
        response = call_primary_image_gen(prompt, negative_prompt, size=size, n=n)
        urls = extract_image_urls(response)

        if not urls:
            # Fallback if primary fails
            logger.warning("[ImageService] Primary model failed, using fallback...")
            response = call_fallback_image_gen(prompt, negative_prompt, size=size, n=n)
            urls = extract_image_urls(response)

        if not urls:
            logger.error("[ImageService] Both primary and fallback image generation failed.")
            return []

        return urls

    except Exception as e:
        logger.error(f"[ImageService] Exception during image generation: {str(e)}")
        return []
