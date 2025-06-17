from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from database import get_db
from schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema
from database.models import MovieModel

router = APIRouter()


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")
    return movie


@router.get("/movies/", response_model=MovieListResponseSchema)
def get_movies(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=20)
):
    total_items_result = db.execute(select(func.count(MovieModel.id)))
    total_items = total_items_result.scalar_one()

    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 0

    offset = (page - 1) * per_page
    result = db.execute(select(MovieModel).offset(offset).limit(per_page))
    movies = result.scalars().all()

    return {
        "movies": movies,
        "prev_page": f"/theater/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        "next_page": f"/theater/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        "total_pages": total_pages,
        "total_items": total_items
    }
