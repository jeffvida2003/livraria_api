import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import Usuario
from database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY não está configurada nas variáveis de ambiente")
    
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def criar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)

def criar_token_acesso(data: dict, expira: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expira or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def autenticar_usuario(db: Session, nome: str, senha: str) -> Optional[Usuario]:
    usuario = db.query(Usuario).filter(Usuario.nome == nome).first()
    if usuario and verificar_senha(senha, usuario.senha_hash):
        return usuario
    return None

def obter_usuario_logado(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autorizado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Debug: log das configurações (remover em produção)
        print(f"DEBUG - SECRET_KEY existe: {bool(SECRET_KEY)}")
        print(f"DEBUG - SECRET_KEY length: {len(SECRET_KEY) if SECRET_KEY else 0}")
        print(f"DEBUG - ALGORITHM: {ALGORITHM}")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nome_usuario: str = payload.get("sub")
        if nome_usuario is None:
            print("DEBUG - Nome de usuário não encontrado no token")
            raise cred_exc
        print(f"DEBUG - Usuário do token: {nome_usuario}")
    except JWTError as e:
        print(f"DEBUG - Erro JWT: {str(e)}")
        raise cred_exc
    usuario = db.query(Usuario).filter(Usuario.nome == nome_usuario).first()
    if usuario is None:
        print(f"DEBUG - Usuário {nome_usuario} não encontrado no banco")
        raise cred_exc
    return usuario
