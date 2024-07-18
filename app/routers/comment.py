from datetime import datetime, date
from typing import Type

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.comment import CommentCreate, CommentUpdate, Comment as CommentSchema
from ..schemas.comment import BlockedComment as BlockedCommentSchema
from ..models.comment import Comment as CommentModel
from ..models.comment import BlockedComment as BlockedCommentModel
from ..models.user import User
from ..database import get_db
from ..core.security import get_current_user

from sqlalchemy.orm import Session

from ..services.llm_moderation import moderation_service

router = APIRouter()


@router.get("/posts/{post_id}/comments", response_model=list[CommentSchema])
async def list_comments(
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
        db_comments = db.query(CommentModel).filter(CommentModel.post_id == post_id).all()
        return db_comments
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred while trying to retrieve list of comments for {post_id}: {e}")


@router.post("/posts/{post_id}/comments", response_model=CommentSchema | BlockedCommentSchema, status_code=201)
async def create_comment(
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

        # Call moderation service to check for potential harmfulness of content and check moderation result
        moderation_result = await moderation_service.moderate_content(comment.content)

        if moderation_result.get("flagged"):
            # Extract blocking reasoning from moderation service response
            blocking_reasoning_string = ' '.join(
                [reason for reason in moderation_result.get("categories").keys() if moderation_result.get("categories").get(reason)])

            # Add blocked comment to table in database of blocked comments
            blocked_db_comment = BlockedCommentModel(**comment.dict(),
                                                     post_id=post_id,
                                                     owner_id=current_user.id,
                                                     blocking_reasoning=blocking_reasoning_string)
            blocked_db_comment.created_at = datetime.now()
            db.add(blocked_db_comment)
            db.commit()

            raise HTTPException(status_code=422, detail="Content is flagged by moderation")

        db_comment.created_at = datetime.now()
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred while trying to create comment for {post_id}: {e}")


@router.put("/posts/{post_id}/comments/{comment_id}", response_model=CommentSchema)
async def update_comment(
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
                                detail="Comment can be updated only by its author.")

        # Call moderation service to check for potential harmfulness of content and check moderation result
        moderation_result = await moderation_service.moderate_content(comment.content)

        if moderation_result.get("flagged"):
            raise HTTPException(status_code=422, detail="Content is flagged by moderation")

        for var, value in vars(comment).items():
            setattr(db_comment, var, value) if value else None

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred while trying to update a comment for {post_id}: {e}")


@router.delete("/posts/{post_id}/comments/{comment_id}", response_model=dict)
async def delete_comment(
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
        db_comment = db.query(CommentModel).filter(CommentModel.post_id == post_id,
                                                   CommentModel.id == comment_id).first()

        # Check if current user is comment author
        if db_comment.owner_id != current_user.id:
            raise HTTPException(status_code=403,
                                detail="Comment can be deleted only by its author.")

        db.delete(db_comment)
        db.commit()

        return {"detail": "Comment deleted successfully."}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,
                            detail=f"An error occurred while trying to delete comment: {e}")


@router.get("/comments-daily-breakdown")
def get_comments_daily_breakdown(
        date_from: str = Query(..., description="Start date for comment analytic"),
        date_to: str = Query(..., description="End date for comment analytic"),
        db: Session = Depends(get_db)
) -> dict:
    """
    Get analytics for comment between specified dates.
    :param date_from: Start date, included
    :param date_to: End date, excluded
    :param db: Current database Session object
    :return: Retrieved comments analytics
    """
    # Get comments from database
    db_comments = db.query(CommentModel).filter(
        CommentModel.created_at >= datetime.strptime(date_from, '%Y-%m-%d'),
        CommentModel.created_at <= datetime.strptime(date_to, '%Y-%m-%d')).all()

    # Get blocked comments from database
    db_blocked_comments = db.query(BlockedCommentModel).filter(
        CommentModel.created_at >= datetime.strptime(date_from, '%Y-%m-%d'),
        CommentModel.created_at <= datetime.strptime(date_to, '%Y-%m-%d')).all()

    response_dict = {
        "comments": {},
        "blocked_comments": {}
    }
    total_comments_amount = 0
    total_blocked_comments_amount = 0

    def update_response_dict_with_formatted_comments_info(
            _response_dict: dict,
            comments: list[Type[CommentModel]],
            comments_type: str,
            total_amount: int) -> tuple[dict, int]:
        """
        Parse given list of comment model from database and update current dict.
        :param _response_dict: Dict that will be returned by the endpoint
        :param comments: Retrieved comments from the database
        :param comments_type: Type of comments that will be processed. One of "comments", "blocked_comments"
        :param total_amount: Total amount of comments value
        :return:
        """
        for comment in comments:
            # Group comments by days
            comment_date = comment.created_at.date()

            if str(comment_date) not in _response_dict.get(comments_type).keys():  # Initiate list with comments for that date
                _response_dict[comments_type].update({str(comment_date): {"items": [comment.to_dict()]}})
            else:
                _response_dict[comments_type][str(comment_date)]["items"].append(comment.to_dict())

            # Add count for total comments amount
            total_amount += 1

        # Temp dict for counting comments amount for each day
        date_comments_amount_temp = {}

        # Update dict with amount of comments for each day
        for date_str in _response_dict[comments_type].keys():
            date_comments_amount_temp.update({
                date_str: {
                    "comments_amount": len(_response_dict[comments_type][date_str]["items"])
                }
            })

        resulting_dict = {k: dict(_response_dict[comments_type].get(k, {}),
                                  **date_comments_amount_temp.get(k, {}))
                          for k in set(_response_dict[comments_type]) | set(date_comments_amount_temp)}

        return resulting_dict, total_amount

    # Update resulting response dict with parsed comments according to their existence
    if db_comments:
        parsed_comments_dict, total_comments_amount = update_response_dict_with_formatted_comments_info(
            response_dict, db_comments, "comments", total_comments_amount
        )
        response_dict["comments"].update(parsed_comments_dict)

    if db_blocked_comments:
        parsed_blocked_comments_dict, total_blocked_comments_amount = update_response_dict_with_formatted_comments_info(
            response_dict, db_blocked_comments, "blocked_comments", total_blocked_comments_amount
        )
        response_dict["blocked_comments"].update(parsed_blocked_comments_dict)

    # Update dict with total amount of comments
    response_dict.update({
        "total_comments_amount": total_comments_amount,
        "total_blocked_comments_amount": total_blocked_comments_amount
    })

    return response_dict

