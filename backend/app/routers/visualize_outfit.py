import asyncio
import os
from pathlib import Path
from uuid import uuid4
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/visualize-outfit",
    tags=["AI Outfit Visualization"],
)

FAL_MODEL_ID = "fal-ai/flux-2/flash"
FAL_QUEUE_URL = f"https://queue.fal.run/{FAL_MODEL_ID}"


class VisualizeOutfitRequest(BaseModel):
    recommendation: dict[str, Any]
    profile: dict[str, Any] = Field(default_factory=dict)


def _piece_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return ", ".join(part for part in (_piece_text(x) for x in value) if part)
    if isinstance(value, dict):
        name = value.get("item") or value.get("name") or value.get("title") or ""
        colour = value.get("colour") or value.get("color") or ""
        if name and colour:
            return f"{colour} {name}"
        return str(name or "")
    return str(value)


def build_fashion_prompt(recommendation: dict[str, Any], profile: dict[str, Any]) -> str:
    one_piece = _piece_text(recommendation.get("one_piece"))
    top = _piece_text(recommendation.get("top"))
    bottom = _piece_text(recommendation.get("bottom"))
    outerwear = _piece_text(recommendation.get("outerwear"))
    footwear = _piece_text(recommendation.get("footwear"))
    accessories = _piece_text(recommendation.get("accessories"))
    bag = _piece_text(recommendation.get("bag"))

    garments = []
    if one_piece:
        garments.append(f"complete one-piece outfit: {one_piece}")
    else:
        if top:
            garments.append(f"top: {top}")
        if bottom:
            garments.append(f"bottom: {bottom}")
    if outerwear:
        garments.append(f"outerwear: {outerwear}")
    if footwear:
        garments.append(f"footwear: {footwear}")
    if bag:
        garments.append(f"bag: {bag}")
    if accessories:
        garments.append(f"accessories: {accessories}")

    if not garments:
        raise HTTPException(
            status_code=422,
            detail="The recommendation does not contain clothing details to visualize.",
        )

    body_type = str(profile.get("body_type") or "").strip()
    skin_tone = str(profile.get("skin_tone") or "").strip()
    height = str(profile.get("height") or "").strip()
    occasion = str(profile.get("occasion") or "everyday").strip()
    style = str(profile.get("style") or "modern").strip()
    mood = str(profile.get("mood") or "").strip()

    profile_details = []
    if body_type and body_type.lower() not in {"not specified", "your profile"}:
        profile_details.append(f"body proportions described as {body_type}")
    if skin_tone and skin_tone.lower() not in {"not specified", "your profile"}:
        profile_details.append(f"{skin_tone} skin undertone")
    if height and height.lower() not in {"not specified", "your profile"}:
        profile_details.append(f"height range {height}")

    profile_text = "; ".join(profile_details)
    garment_text = "; ".join(garments)

    return (
        "Create a photorealistic full-body fashion editorial photograph of one adult fashion model "
        "wearing this exact outfit concept: "
        f"{garment_text}. "
        f"The styling is for {occasion}, in a {style} aesthetic"
        + (f" with a {mood} mood" if mood else "")
        + (f". Model characteristics: {profile_text}" if profile_text else "")
        + ". Show the model from head to toe, centered, with the entire outfit clearly visible. "
        "Use realistic human anatomy, natural hands and face, believable fabric drape, detailed garment "
        "textures, accurate colour rendering, tasteful studio lighting, and a clean neutral studio background. "
        "The clothes must be the visual focus. Do not add text, captions, logos, watermarks, collage panels, "
        "extra people, or product labels. This is a fashion concept visualization based on the supplied "
        "text description; do not claim it is an exact photographic reproduction of a wardrobe item."
    )


@router.post("/generate")
async def generate_outfit_visualization(request: VisualizeOutfitRequest):
    api_key = os.getenv("FAL_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI image generation is not configured. Set the FAL_KEY environment "
                "variable in the backend terminal, then restart the backend."
            ),
        )

    prompt = build_fashion_prompt(request.recommendation, request.profile)
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "image_size": "portrait_4_3",
        "num_images": 1,
        "output_format": "jpeg",
        "enable_safety_checker": True,
    }

    timeout = httpx.Timeout(180.0, connect=20.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            submit = await client.post(FAL_QUEUE_URL, headers=headers, json=payload)
            if submit.status_code >= 400:
                detail = "The AI image provider rejected the request."
                try:
                    detail = submit.json().get("detail", detail)
                except Exception:
                    pass
                raise HTTPException(status_code=502, detail=str(detail))

            job = submit.json()
            status_url = job.get("status_url")
            response_url = job.get("response_url")
            if not status_url or not response_url:
                raise HTTPException(
                    status_code=502,
                    detail="The AI provider returned an incomplete generation job.",
                )

            result = None
            for _ in range(75):
                await asyncio.sleep(2)
                status_response = await client.get(status_url, headers=headers)
                if status_response.status_code >= 400:
                    raise HTTPException(
                        status_code=502,
                        detail="Could not check the AI image generation status.",
                    )
                status_data = status_response.json()
                status = status_data.get("status")

                if status == "COMPLETED":
                    if status_data.get("error"):
                        raise HTTPException(
                            status_code=502,
                            detail=f"AI image generation failed: {status_data['error']}",
                        )
                    result_response = await client.get(response_url, headers=headers)
                    if result_response.status_code >= 400:
                        raise HTTPException(
                            status_code=502,
                            detail="The AI provider could not return the generated image.",
                        )
                    result = result_response.json()
                    break

            if result is None:
                raise HTTPException(
                    status_code=504,
                    detail="AI image generation took too long. Please try again.",
                )

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="The AI image provider timed out. Please try again.",
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not connect to the AI image provider: {exc.__class__.__name__}",
        )

    images = result.get("images") or []
    provider_image_url = images[0].get("url") if images else None
    if not provider_image_url:
        raise HTTPException(
            status_code=502,
            detail="The AI provider completed the request but returned no image.",
        )

    # Copy the generated image into this backend's uploads folder so the
    # frontend does not depend on a temporary third-party CDN URL.
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
            image_response = await client.get(provider_image_url)
            image_response.raise_for_status()
        content_type = image_response.headers.get("content-type", "").split(";")[0].lower()
        extension = ".png" if content_type == "image/png" else ".webp" if content_type == "image/webp" else ".jpg"
        upload_dir = Path(__file__).resolve().parents[1] / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        filename = f"outfit_{uuid4().hex}{extension}"
        (upload_dir / filename).write_bytes(image_response.content)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"The image was generated but could not be saved by OutfitAura: {exc.__class__.__name__}",
        )

    return {
        "status": "success",
        "image_url": f"http://127.0.0.1:8000/uploads/{filename}",
        "provider": "fal.ai",
        "model": FAL_MODEL_ID,
        "visualization_type": "AI-generated fashion concept from outfit description",
    }
