from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import schemas, models
from auth import obter_usuario_logado

router = APIRouter(prefix="/editoras", tags=["Editoras"])

@router.get("/", response_model=list[schemas.EditoraOut])
def listar_editoras(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return db.query(models.Editora).all()

@router.get("/{editora_id}", response_model=schemas.EditoraOut)
def buscar_editora(editora_id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    editora = db.query(models.Editora).filter(models.Editora.id == editora_id).first()
    if not editora:
        raise HTTPException(status_code=404, detail="Editora não encontrada")
    return editora

@router.post("/", response_model=schemas.EditoraOut, status_code=201)
def criar_editora(editora: schemas.EditoraCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    nova_editora = models.Editora(**editora.dict())
    db.add(nova_editora)
    db.commit()
    db.refresh(nova_editora)
    return nova_editora

@router.put("/{editora_id}", response_model=schemas.EditoraOut)
def atualizar_editora(editora_id: int, dados: schemas.EditoraCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    editora = db.query(models.Editora).filter(models.Editora.id == editora_id).first()
    if not editora:
        raise HTTPException(status_code=404, detail="Editora não encontrada")
    for key, value in dados.dict().items():
        setattr(editora, key, value)
    db.commit()
    db.refresh(editora)
    return editora

@router.patch("/{editora_id}", response_model=schemas.EditoraOut)
def atualizar_parcial_editora(editora_id: int, dados: schemas.EditoraUpdate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    editora = db.query(models.Editora).filter(models.Editora.id == editora_id).first()
    if not editora:
        raise HTTPException(status_code=404, detail="Editora não encontrada")
    for key, value in dados.dict(exclude_unset=True).items():
        setattr(editora, key, value)
    db.commit()
    db.refresh(editora)
    return editora

@router.delete("/{editora_id}", status_code=204)
def deletar_editora(editora_id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    editora = db.query(models.Editora).filter(models.Editora.id == editora_id).first()
    if not editora:
        raise HTTPException(status_code=404, detail="Editora não encontrada")
    db.delete(editora)
    db.commit()
    return
