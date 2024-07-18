from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.user import UserCreate, User as UserSchema
from ..schemas.user import UserProfile as UserProfileSchema
from ..models import User, UserProfile
from ..database import get_db
from ..core.security import get_password_hash, verify_password, create_access_token, get_current_user

from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()


@router.post("/register", response_model=UserSchema)
async def create_user(
        user: UserCreate,
        db: Session = Depends(get_db)
) -> User:
    """
    Endpoint for creating users
    :param user: Create user model
    :param db: Database session object
    :return: Registered user model
    """

    # Check, if user already exists
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(status_code=400,
                                detail="Username already registered")

        # Add user to database with hashed password
        hashed_password = get_password_hash(user.password)
        db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create user profile
        user_profile = UserProfile(user_id=db_user.id)
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)

        return db_user

    except SQLAlchemyError as e:  # Handle database error
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"An database error occurred while trying to register: {e}")


@router.post("/login", response_model=dict)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
) -> dict:
    """
    Login user by getting JWT token
    :param form_data: Credentials form
    :param db: Current database session object
    :return: Dict with access token
    """
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    except SQLAlchemyError as e:  # Handle database error
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"An database error occurred while trying to login: {e}")


@router.delete("/profile", response_model=dict)
async def delete_profile(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> dict:
    """
    Delete current user profile
    :param db: Current database Session object
    :param current_user: Current user which will be deleted
    :return: Message indicating the deletion status
    """
    try:
        db.delete(current_user)
        db.commit()
        return {"message": f"User {current_user.username} was deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"An database error occurred while deleting the user profile: {e}")


@router.get("/my-profile", response_model=UserProfileSchema)
async def get_current_user_profile(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> UserProfile:
    """
    Get current authenticated user profile
    :param db: Current database Session object
    :param current_user: Current user which profile will be got
    :return: Dict with user profile info
    """
    try:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if user_profile is None:
            raise HTTPException(status_code=404,
                                detail="Current user not found")

        return user_profile

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"Database error: {e}")


@router.get("/refresh-access-token", response_model=dict)
async def refresh_access_token(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> dict:
    """
    Refresh access token endpoint for current user.
    :param db: Current database session object
    :param current_user: Current user
    :return: Dict with new access token
    """
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}

    except SQLAlchemyError as e:  # Handle database error
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"An database error occurred while trying to refresh token: {e}")
