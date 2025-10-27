from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import obter_usuario_logado

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get("/", response_model=list[schemas.AutorOut])
def listar_autores(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return db.query(models.Autor).all()


@router.get("/{autor_id}", response_model=schemas.AutorOut)
def buscar_autor(autor_id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    return autor


@router.post("/", response_model=schemas.AutorOut, status_code=201)
def criar_autor(autor: schemas.AutorCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    novo_autor = models.Autor(**autor.dict())
    db.add(novo_autor)
    db.commit()
    db.refresh(novo_autor)
    return novo_autor


@router.put("/{autor_id}", response_model=schemas.AutorOut)
def atualizar_autor(autor_id: int, autor_novo: schemas.AutorCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    for key, value in autor_novo.dict().items():
        setattr(autor, key, value)
    db.commit()
    db.refresh(autor)
    return autor


@router.patch("/{autor_id}", response_model=schemas.AutorOut)
def atualizar_autor_parcial(autor_id: int, atualizacao: schemas.AutorCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    for key, value in atualizacao.dict(exclude_unset=True).items():
        setattr(autor, key, value)
    db.commit()
    db.refresh(autor)
    return autor


@router.delete("/{autor_id}", status_code=204)
def deletar_autor(autor_id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor não encontrado")
    db.delete(autor)
    db.commit()
    return None
