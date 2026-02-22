"""Review/rating service layer."""
from __future__ import annotations

import logging
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.review import Review
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.review_schema import ReviewCreate


logger = logging.getLogger(__name__)


def create_or_update_review(db: Session, user: User, supplier_id: int, payload: ReviewCreate) -> Review:
    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == supplier_id, Supplier.approved.is_(True), Supplier.blocked.is_(False))
        .first()
    )
    if not supplier:
        raise NotFoundError("Supplier not found, not approved, or blocked")

    review = db.query(Review).filter(Review.user_id == user.id, Review.supplier_id == supplier_id).first()
    if review:
        review.rating = payload.rating
        review.comment = payload.comment
    else:
        review = Review(
            user_id=user.id,
            supplier_id=supplier_id,
            rating=payload.rating,
            comment=payload.comment,
        )
        db.add(review)

    db.commit()
    db.refresh(review)
    logger.info("Supplier review upserted supplier_id=%s user_id=%s review_id=%s", supplier_id, user.id, review.id)
    return review


def list_supplier_reviews(db: Session, supplier_id: int) -> list[Review]:
    return (
        db.query(Review)
        .filter(Review.supplier_id == supplier_id)
        .order_by(Review.id.desc())
        .all()
    )


def rating_summary(db: Session, supplier_id: int) -> tuple[float, int]:
    avg_rating, total_reviews = (
        db.query(func.coalesce(func.avg(Review.rating), 0.0), func.count(Review.id))
        .filter(Review.supplier_id == supplier_id)
        .first()
    )
    return float(avg_rating or 0.0), int(total_reviews or 0)
