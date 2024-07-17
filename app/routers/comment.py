from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.comment import CommentCreate, CommentUpdate, Comment as CommentSchema
from ..models.comment import Comment as CommentModel
from ..models.user import User
from ..database import get_db
from ..core.security import get_current_user

from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/posts/{post_id}/comments", response_model=list[CommentSchema])
def get_comments(
        post_id: int,
        db: Session = Depends(get_db)
):
    """
    Endpoint for retrieving comments for specific post
    :param post_id: Post id to retrieve comments for
    :param db: Current database Session object
    :return: Retrieved comments list
    """
    try:
        db_comments = db.query(CommentModel).filter(post_id=post_id).all()
        return db_comments
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred when trying to retrieve list of comments for {post_id}: {e}")


@router.post("posts/{post_id}/comments", response_model=CommentSchema)
def create_comment(
        comment: CommentCreate,
        post_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Endpoint for creating comment to specific post
    :param comment: Create comment model
    :param post_id: Post id to create comment for
    :param db: Current database Session object
    :param current_user: Comment author
    :return: Created comment
    """
    try:
        db_comment = CommentModel(**comment.dict(), post_id=post_id, owner_id=current_user.id)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred when trying to create comment for {post_id}: {e}")


@router.put("/posts/{post_id}/comments/{comment_id}", response_model=CommentSchema)
def update_comment(
        post_id: int,
        comment_id: int,
        comment: CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Endpoint for updating comment by its author
    :param post_id: Post id to update comment for
    :param comment_id: Comment id to update
    :param comment: Update comment model
    :param db: Current database Session object
    :param current_user: Current user to check author
    :return: Updated comment
    """
    try:
        db_comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()

        if db_comment is None:
            raise HTTPException(status_code=404,
                                detail="Comment not found")

        # Check, if current user is comment author
        if db_comment.owner_id != current_user.id:
            raise HTTPException(status_code=403,
                                detail="Comment can be updated only by its author")

        for var, value in vars(comment).items():
            setattr(db_comment, var, value) if value else None

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred when trying to update a comment for {post_id}: {e}")


@router.delete("/posts/{post_id}/comments/{comment_id}", response_model=dict)
def delete_comment(
        post_id: int,
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)) -> dict:
    """
    Endpoint for deleting comment by its author
    :param post_id: Post id to delete comment for
    :param db: Current database Session object
    :param current_user: Current user to verify that it is comment author
    :return: Message indicating deletion status
    """

    try:
        db_comment = db.query(CommentModel).filter(CommentModel.id == post_id).first()

        # Check if current user is comment author
        if db_comment.owner_id != current_user.id:
            raise HTTPException(status_code=403,
                                detail="Comment can be deleted only by its author.")

        db.delete(db_comment)
        db.commit()

        return {"message": "Comment deleted successfully."}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred when trying to delete comment: {e}")

