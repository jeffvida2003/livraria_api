from sqlalchemy import Column, BigInteger, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(BigInteger, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    senha_hash = Column(String, nullable=False)

class Autor(Base):
    __tablename__ = "autores"
    id = Column(BigInteger, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    telefone = Column(String(20))
    bio = Column(Text)
    livros = relationship("Livro", back_populates="autor")

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(BigInteger, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True)
    livros = relationship("Livro", back_populates="categoria")

class Editora(Base):
    __tablename__ = "editoras"
    id = Column(BigInteger, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    endereco = Column(Text)
    telefone = Column(String(20))
    livros = relationship("Livro", back_populates="editora")

class Livro(Base):
    __tablename__ = "livros"
    id = Column(BigInteger, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    resumo = Column(Text)
    ano = Column(Integer)
    paginas = Column(Integer)
    isbn = Column(String)
    categoria_id = Column(BigInteger, ForeignKey("categorias.id"))
    editora_id = Column(BigInteger, ForeignKey("editoras.id"))
    autor_id = Column(BigInteger, ForeignKey("autores.id"))
    categoria = relationship("Categoria", back_populates="livros")
    editora = relationship("Editora", back_populates="livros")
    autor = relationship("Autor", back_populates="livros")
