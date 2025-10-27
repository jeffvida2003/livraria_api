from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import schemas, models
from auth import obter_usuario_logado

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.get("/", response_model=list[schemas.CategoriaOut])
def listar_categorias(db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    return db.query(models.Categoria).all()

@router.get("/{categoria_id}", response_model=schemas.CategoriaOut)
def buscar_categoria(categoria_id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria

@router.post("/", response_model=schemas.CategoriaOut, status_code=201)
def criar_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    nova_categoria = models.Categoria(**categoria.dict())
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return nova_categoria

@router.put("/{categoria_id}", response_model=schemas.CategoriaOut)
def atualizar_categoria(categoria_id: int, dados: schemas.CategoriaCreate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    for key, value in dados.dict().items():
        setattr(categoria, key, value)
    db.commit()
    db.refresh(categoria)
    return categoria

@router.patch("/{categoria_id}", response_model=schemas.CategoriaOut)
def atualizar_parcial_categoria(categoria_id: int, dados: schemas.CategoriaUpdate, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    for key, value in dados.dict(exclude_unset=True).items():
        setattr(categoria, key, value)
    db.commit()
    db.refresh(categoria)
    return categoria

@router.delete("/{categoria_id}", status_code=204)
def deletar_categoria(categoria_id: int, db: Session = Depends(get_db), usuario=Depends(obter_usuario_logado)):
    categoria = db.query(models.Categoria).filter(models.Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    db.delete(categoria)
    db.commit()
    return
