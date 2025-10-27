from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import obter_usuario_logado

router = APIRouter(prefix="/livros", tags=["Livros"])

@router.get("/", response_model=list[schemas.LivroOut])
def listar_livros(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return db.query(models.Livro).all()

@router.get("/{livro_id}", response_model=schemas.LivroOut)
def buscar_livro(livro_id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro

@router.post("/", response_model=schemas.LivroOut, status_code=201)
def criar_livro(livro: schemas.LivroCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    novo_livro = models.Livro(**livro.dict())
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)
    return novo_livro

@router.put("/{livro_id}", response_model=schemas.LivroOut)
def atualizar_livro(livro_id: int, livro_novo: schemas.LivroCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    for key, value in livro_novo.dict().items():
        setattr(livro, key, value)
    db.commit()
    db.refresh(livro)
    return livro

@router.patch("/{livro_id}", response_model=schemas.LivroOut)
def atualizar_livro_parcial(livro_id: int, atualizacao: schemas.LivroUpdate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    for key, value in atualizacao.dict(exclude_unset=True).items():
        setattr(livro, key, value)
    db.commit()
    db.refresh(livro)
    return livro

@router.delete("/{livro_id}", status_code=204)
def deletar_livro(livro_id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    db.delete(livro)
    db.commit()
    return None
