from pydantic import BaseModel
from typing import Optional

# Usuários
class UsuarioBase(BaseModel):
    nome: str
    email: str

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioOut(UsuarioBase):
    id: int
    class Config:
        orm_mode = True

# Editoras
class EditoraBase(BaseModel):
    nome: str
    endereco: Optional[str] = None
    telefone: Optional[str] = None

class EditoraCreate(EditoraBase):
    pass

class EditoraUpdate(EditoraBase):
    pass

class EditoraOut(EditoraBase):
    id: int
    class Config:
        orm_mode = True

# Categorias
class CategoriaBase(BaseModel):
    nome: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(CategoriaBase):
    pass

class CategoriaOut(CategoriaBase):
    id: int
    class Config:
        orm_mode = True

# ---- AUTOR ----

class AutorBase(BaseModel):
    nome: str
    email: str
    telefone: Optional[str] = None
    bio: Optional[str] = None

class AutorCreate(AutorBase):
    pass

class AutorUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    bio: Optional[str] = None

class AutorOut(AutorBase):
    id: int

    class Config:
        orm_mode = True

# ---- LIVRO ----

class LivroBase(BaseModel):
    titulo: str
    resumo: Optional[str] = None
    ano: int
    paginas: int
    isbn: str
    categoria_id: int
    editora_id: int
    autor_id: int

class LivroCreate(LivroBase):
    pass

class LivroUpdate(BaseModel):
    titulo: Optional[str] = None
    resumo: Optional[str] = None
    ano: Optional[int] = None
    paginas: Optional[int] = None
    isbn: Optional[str] = None
    categoria_id: Optional[int] = None
    editora_id: Optional[int] = None
    autor_id: Optional[int] = None

class LivroOut(LivroBase):
    id: int

    class Config:
        orm_mode = True
