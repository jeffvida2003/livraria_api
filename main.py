from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database, auth
from routers import livros, autores, categorias, editoras
import os

app = FastAPI(
    title="API Livraria Digital",
    version="1.0.0",
    description="CRUD completo para gestão de livros, autores, editoras e categorias. Protegido por autenticação JWT."
)

# Configuração do CORS para o Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()
app.include_router(livros.router)
app.include_router(autores.router)
app.include_router(categorias.router)
app.include_router(editoras.router)

@app.get("/")
def root():
    return {"message": "API Livraria funcionando!", "status": "online"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2024-10-28"}

# Endpoint temporário para debug - REMOVER EM PRODUÇÃO
@app.get("/debug/config")
def debug_config():
    return {
        "secret_key_length": len(os.getenv("SECRET_KEY", "")),
        "secret_key_set": bool(os.getenv("SECRET_KEY")),
        "algorithm": os.getenv("ALGORITHM", ""),
        "token_expire": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", ""),
        "token_expire_int": auth.ACCESS_TOKEN_EXPIRE_MINUTES,
        "database_url_prefix": os.getenv("DATABASE_URL", "")[:20] + "..." if os.getenv("DATABASE_URL") else "Not set",
        "all_env_vars": list(os.environ.keys())[:10]  # Primeiras 10 variáveis para debug
    }

@app.get("/debug/test-token")
def test_token_creation():
    """Endpoint para testar criação de token"""
    try:
        test_data = {"sub": "test_user"}
        token = auth.criar_token_acesso(test_data)
        return {
            "success": True,
            "token_created": bool(token),
            "token_length": len(token) if token else 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/debug/test-login")
def test_login_flow():
    """Endpoint para testar fluxo completo de autenticação"""
    try:
        # Mostrar configurações atuais
        import auth as auth_module
        secret_key, algorithm, expire_min = auth_module.get_config()
        
        # Criar token de teste
        test_data = {"sub": "usuario_teste"}
        token = auth.criar_token_acesso(test_data)
        
        # Tentar decodificar o token usando a MESMA instância
        from jose import jwt
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        
        return {
            "success": True,
            "token_created": True,
            "token_decoded": True,
            "payload": payload,
            "user_from_token": payload.get("sub"),
            "secret_key_repr": repr(secret_key[:10]) if secret_key else "None",
            "secret_length": len(secret_key) if secret_key else 0,
            "algorithm": algorithm
        }
    except Exception as e:
        import auth as auth_module
        secret_key, algorithm, _ = auth_module.get_config()
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "secret_key_repr": repr(secret_key[:10]) if secret_key else "None",
            "secret_length": len(secret_key) if secret_key else 0,
            "algorithm": algorithm
        }

@app.get("/debug/env-check")
def check_environment():
    """Verificar as variáveis de ambiente detalhadamente"""
    import os
    secret_raw = os.getenv("SECRET_KEY")
    return {
        "secret_key_raw": repr(secret_raw[:10]) if secret_raw else "None",
        "secret_key_len": len(secret_raw) if secret_raw else 0,
        "secret_key_type": type(secret_raw).__name__ if secret_raw else "None",
        "algorithm_raw": repr(os.getenv("ALGORITHM", "")),
        "has_quotes": '"' in secret_raw if secret_raw else False,
        "has_newlines": '\n' in secret_raw if secret_raw else False
    }

@app.get("/debug/users-count")
def debug_users_count(db: Session = Depends(database.get_db)):
    """Endpoint para verificar quantos usuários existem no banco"""
    try:
        total_users = db.query(models.Usuario).count()
        usuarios = db.query(models.Usuario).limit(5).all()
        usernames = [u.nome for u in usuarios]
        
        return {
            "success": True,
            "total_users": total_users,
            "sample_usernames": usernames[:5]  # Primeiros 5 usuários
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
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
    print(f"DEBUG LOGIN - Tentativa de login para usuário: {form_data.username}")
    usuario = auth.autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        print(f"DEBUG LOGIN - Falha na autenticação para: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    
    print(f"DEBUG LOGIN - Usuário autenticado: {usuario.nome}")
    token = auth.criar_token_acesso(data={"sub": usuario.nome})
    print(f"DEBUG LOGIN - Token criado com sucesso, tamanho: {len(token)}")
    return {"access_token": token, "token_type": "bearer"}
