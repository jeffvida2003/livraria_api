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

# Configurações globais - garantir consistência
_SECRET_KEY = None
_ALGORITHM = None
_ACCESS_TOKEN_EXPIRE_MINUTES = None

def get_config():
    global _SECRET_KEY, _ALGORITHM, _ACCESS_TOKEN_EXPIRE_MINUTES
    
    if _SECRET_KEY is None:
        _SECRET_KEY = os.getenv("SECRET_KEY")
        if not _SECRET_KEY:
            print("WARNING: SECRET_KEY não está configurada! Usando chave padrão (INSEGURO)")
            _SECRET_KEY = "chave-padrao-insegura-nao-usar-em-producao"
        else:
            # Remover aspas duplas se existirem
            _SECRET_KEY = _SECRET_KEY.strip().strip('"').strip("'")
        print(f"DEBUG AUTH - SECRET_KEY configurada: {_SECRET_KEY[:8]}...{_SECRET_KEY[-4:]}")
    
    if _ALGORITHM is None:
        _ALGORITHM = os.getenv("ALGORITHM", "HS256")
        # Remover aspas duplas se existirem
        _ALGORITHM = _ALGORITHM.strip().strip('"').strip("'")
    
    if _ACCESS_TOKEN_EXPIRE_MINUTES is None:
        _ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    
    return _SECRET_KEY, _ALGORITHM, _ACCESS_TOKEN_EXPIRE_MINUTES

# Inicializar configurações
SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES = get_config()

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
    
    # Garantir que usa as configurações atuais
    secret_key, algorithm, _ = get_config()
    
    print(f"DEBUG TOKEN - Criando token com dados: {data}")
    print(f"DEBUG TOKEN - SECRET_KEY length: {len(secret_key)}")
    print(f"DEBUG TOKEN - Algoritmo: {algorithm}")
    print(f"DEBUG TOKEN - Expira em: {ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
    
    token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    print(f"DEBUG TOKEN - Token criado com sucesso")
    return token

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
        # Garantir que usa as configurações atuais
        secret_key, algorithm, _ = get_config()
        
        # Debug: log das configurações (remover em produção)
        print(f"DEBUG - SECRET_KEY existe: {bool(secret_key)}")
        print(f"DEBUG - SECRET_KEY length: {len(secret_key) if secret_key else 0}")
        print(f"DEBUG - ALGORITHM: {algorithm}")
        
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
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
