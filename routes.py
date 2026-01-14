from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile,Query, Form
from sqlalchemy.orm import Session
from typing import List,Annotated
import service, models, schemas
from fastapi import Query
from database import SessionLocal, engine
from middleware.application_middleware import default_dependency
models.Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/random')
async def get_random(request: Request, query: schemas.GetRandomQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(default_dependency)):
    try:
        return await service.get_random(request, db, query.var_1, query.var_2)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/floor')
async def get_floor(request: Request, query: schemas.GetFloorQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(default_dependency)):
    try:
        return await service.get_floor(request, db, query.var_1, query.var_2)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/arithmetic')
async def get_arithmetic(request: Request, query: schemas.GetArithmeticQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(default_dependency)):
    try:
        return await service.get_arithmetic(request, db, query.var_1, query.var_2)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/round')
async def get_round(request: Request, query: schemas.GetRoundQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(default_dependency)):
    try:
        return await service.get_round(request, db, query.var_1, query.var_2)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/ceil')
async def get_ceil(request: Request, query: schemas.GetCeilQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(default_dependency)):
    try:
        return await service.get_ceil(request, db, query.var_1, query.var_2)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

