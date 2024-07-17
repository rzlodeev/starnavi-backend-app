from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.post import PostCreate, PostUpdate, Post as PostSchema
from ..models.post import Post as PostModel
from ..models.user import User
from ..database import get_db
from ..core.security import get_current_user

from sqlalchemy.orm import Session


router = APIRouter()


@router.get("/posts", response_model=list[PostSchema])
def list_posts(db: Session = Depends(get_db)) -> list:
    """
    Endpoint for retrieving all posts
    :param db: Current db Session object
    :return: Dict with all posts from database
    """
    try:
        posts = db.query(PostModel).all()
        return posts
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred when trying to get list of posts: {e}")


@router.get("/posts/{post_id}", response_model=PostSchema)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    Endpoint for retrieving specific post by id
    :param post_id: Post ID
    :param db: Current database Session object
    :return: Retrieved ost model
    """
    try:
        post = db.query(PostModel).filter(PostModel.id == post_id).first()
        return post
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred when trying to retrieve post: {e}")


@router.post("/posts", response_model=PostSchema)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> PostModel:
    """
    Endpoint for creating post
    :param post: Create post model
    :param db: Current database session object
    :param current_user: Post author
    :return: Post model
    """
    try:
        db_post = PostModel(**post.dict(), owner_id=current_user.id)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred when trying to create a post: {e}")


@router.put("/posts/{post_id}", response_model=PostSchema)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Endpoint for updating post by its author
    :param post_id: Id of the post to update
    :param post: Update post model
    :param db: Current database Session object
    :param current_user: Current user
    :return: Updated post
    """
    try:
        db_post = db.query(PostModel).filter(PostModel.id == post_id).first()

        if db_post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        # Check, if current user is author of the post
        if db_post.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Post can be updated only by its author.")

        for var, value in vars(post).items():
            setattr(db_post, var, value) if value else None
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred when trying to update post: {e}")


@router.delete("/posts/{post_id}", response_model=dict)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict:
    """
    Endpoint for deleting post by its author
    :param post_id: Post ID
    :param db: Current database Session object
    :param current_user: Current user to verify that it is post author
    :return: Message indicating deletion status
    """

    try:
        post = db.query(PostModel).filter(PostModel.id == post_id).first()

        # Check if current user is post author
        if post.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Post can be deleted only by its author.")

        # Delete the post from the database
        db.delete(post)
        db.commit()

        return {"message": "Post deleted successfully."}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred when trying to delete post: {e}")

