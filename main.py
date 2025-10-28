from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, database, auth
from routers import livros, autores, categorias, editoras
import os

app = FastAPI(
    title="API Livraria Digital",
    version="1.0.0",
    description="CRUD completo para gestão de livros, autores, editoras e categorias. Protegido por autenticação JWT."
)

database.init_db()
app.include_router(livros.router)
app.include_router(autores.router)
app.include_router(categorias.router)
app.include_router(editoras.router)

# Endpoint temporário para debug - REMOVER EM PRODUÇÃO
@app.get("/debug/config")
def debug_config():
    return {
        "secret_key_length": len(os.getenv("SECRET_KEY", "")),
        "algorithm": os.getenv("ALGORITHM", ""),
        "database_url_prefix": os.getenv("DATABASE_URL", "")[:20] + "..." if os.getenv("DATABASE_URL") else "Not set"
    }

@app.post("/usuarios", response_model=schemas.UsuarioOut, status_code=201)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    hashed = auth.criar_hash_senha(usuario.senha)
    novo_usuario = models.Usuario(nome=usuario.nome, email=usuario.email, senha_hash=hashed)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    usuario = auth.autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    token = auth.criar_token_acesso(data={"sub": usuario.nome})
    return {"access_token": token, "token_type": "bearer"}
