
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.outfit import CreateOutfitRequest
from app.services.outfit_recommender import create_outfit_recommendations
from app.database import get_db
from app.models import User, WardrobeItem

router = APIRouter(
    prefix="/create-outfit",
    tags=["Create My Outfit"]
)


@router.post("/generate")
def generate_outfit(
    request: CreateOutfitRequest,
    db: Session = Depends(get_db)
):
    wardrobe_items = []

    if request.user_id is not None:
        user = db.query(User).filter(
            User.id == request.user_id
        ).first()

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        wardrobe_items = db.query(WardrobeItem).filter(
            WardrobeItem.user_id == request.user_id
        ).all()

    recommendations = create_outfit_recommendations(
        request,
        wardrobe_items
    )

    return {
        "module": "Create My Outfit",
        "message": "Your personalised outfit recommendations are ready!",
        "status": "success",
        **recommendations
    }
