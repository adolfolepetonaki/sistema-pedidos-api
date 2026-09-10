import os
from datetime import date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuração do Banco de Dados PostgreSQL (Neon)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo da Tabela no Banco
class PedidoDB(Base):
    __tablename__ = "pedidos"

    id_pedido = Column(String, primary_key=True, index=True)
    cliente_nome = Column(String)
    descricao_itens = Column(String)
    prazo_entrega = Column(Date)
    status = Column(String, default="FECHADO")
    data_entrega_real = Column(Date, nullable=True)

if engine:
    Base.metadata.create_all(bind=engine)

# Esquemas Pydantic
class PedidoCreate(BaseModel):
    id_pedido: str
    cliente_nome: str
    descricao_itens: str
    prazo_entrega: date

class PedidoResponse(BaseModel):
    id_pedido: str
    cliente_nome: str
    descricao_itens: str
    prazo_entrega: date
    status: str
    data_entrega_real: Optional[date] = None

    class Config:
        from_attributes = True

# Inicialização do FastAPI
app = FastAPI(title="Sistema de Produção e SLA")

# LIBERAR CORS (Permite que o painel HTML faça requisições à API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    if not engine:
        raise HTTPException(status_code=500, detail="DATABASE_URL não configurada.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"mensagem": "API de Produção e SLA ativa! Acesse /docs para a documentação."}

@app.post("/pedidos")
def criar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    db_pedido = db.query(PedidoDB).filter(PedidoDB.id_pedido == pedido.id_pedido).first()
    if db_pedido:
        raise HTTPException(status_code=400, detail="Pedido com este ID já existe.")
    
    novo_pedido = PedidoDB(
        id_pedido=pedido.id_pedido,
        cliente_nome=pedido.cliente_nome,
        descricao_itens=pedido.descricao_itens,
        prazo_entrega=pedido.prazo_entrega,
        status="FECHADO"
    )
    db.add(novo_pedido)
    db.commit()
    return {"mensagem": "Pedido registrado!", "id_pedido": pedido.id_pedido}

@app.put("/pedidos/{id_pedido}/producao")
def mover_para_producao(id_pedido: str, db: Session = Depends(get_db)):
    pedido = db.query(PedidoDB).filter(PedidoDB.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    
    pedido.status = "EM_PRODUCAO"
    db.commit()
    return {"mensagem": f"Pedido {id_pedido} movido para EM_PRODUCAO."}

@app.get("/relatorio/fila-producao")
def fila_producao(db: Session = Depends(get_db)):
    pedidos = db.query(PedidoDB).filter(PedidoDB.status.in_(["FECHADO", "EM_PRODUCAO"])).all()
    hoje = date.today()
    
    resultado = []
    for p in pedidos:
        dias_restantes = (p.prazo_entrega - hoje).days
        if dias_restantes < 0:
            alerta = "ATRASADO"
        elif dias_restantes <= 2:
            alerta = "URGENTE"
        else:
            alerta = "OK"
            
        resultado.append({
            "id_pedido": p.id_pedido,
            "cliente_nome": p.cliente_nome,
            "descricao_itens": p.descricao_itens,
            "status": p.status,
            "prazo_entrega": str(p.prazo_entrega),
            "dias_restantes": dias_restantes,
            "alerta_sla": alerta
        })
    return resultado

@app.put("/pedidos/{id_pedido}/entregar")
def entregar_pedido(id_pedido: str, db: Session = Depends(get_db)):
    pedido = db.query(PedidoDB).filter(PedidoDB.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    
    hoje = date.today()
    pedido.status = "ENTREGUE"
    pedido.data_entrega_real = hoje
    db.commit()
    
    no_prazo = hoje <= pedido.prazo_entrega
    return {
        "mensagem": f"Pedido {id_pedido} entregue!",
        "data_entrega": str(hoje),
        "no_prazo": no_prazo
    }
