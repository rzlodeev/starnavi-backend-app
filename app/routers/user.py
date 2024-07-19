from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError

from ..models import UserProfile
from ..database import get_db

from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


@router.get("/profile/{user_id}")
async def get_user_profile(
        user_id: int,
        db: Session = Depends(get_db)
):
    """
    Endpoint for retrieving user profile by id
    :param user_id: User id
    :param db: Current database Session object
    :return: User profile
    """
    try:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if user_profile is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user_profile
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred while trying to get user profile {user_id}: {e}")
