import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
from enum import Enum
from datetime import date

from sqlalchemy import create_engine, Column, String, Date, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Le a URL do banco da variavel de ambiente (no Render) ou usa a do Neon
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://seu_usuario:sua_senha@ep-exemplo.us-east-2.aws.neon.tech/neondb?sslmode=require")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StatusPedido(str, Enum):
    FECHADO = "FECHADO"
    EM_PRODUCAO = "EM_PRODUCAO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

class PedidoDB(Base):
    __tablename__ = "pedidos_producao"
    id_pedido = Column(String, primary_key=True, index=True)
    cliente_nome = Column(String, nullable=False)
    descricao_itens = Column(Text, nullable=False)
    status = Column(String, default=StatusPedido.FECHADO.value)
    data_criacao = Column(Date, default=date.today)
    prazo_entrega = Column(Date, nullable=False)
    data_entrega_real = Column(Date, nullable=True)
    entregue_no_prazo = Column(Boolean, nullable=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PedidoCriar(BaseModel):
    id_pedido: str
    cliente_nome: str
    descricao_itens: str
    prazo_entrega: date

app = FastAPI(title="Gestão de Pedidos, Produção e Entregas")

@app.get("/", include_in_schema=False)
def redirecionar_docs():
    return RedirectResponse(url="/docs")

@app.post("/pedidos")
def criar_pedido(dados: PedidoCriar, db: Session = Depends(get_db)):
    existente = db.query(PedidoDB).filter(PedidoDB.id_pedido == dados.id_pedido).first()
    if existente:
        raise HTTPException(status_code=400, detail="ID de pedido já existente.")
    novo_pedido = PedidoDB(
        id_pedido=dados.id_pedido,
        cliente_nome=dados.cliente_nome,
        descricao_itens=dados.descricao_itens,
        prazo_entrega=dados.prazo_entrega,
        status=StatusPedido.FECHADO.value
    )
    db.add(novo_pedido)
    db.commit()
    return {"mensagem": "Pedido registrado!", "pedido": novo_pedido}

@app.put("/pedidos/{id_pedido}/producao")
def enviar_para_producao(id_pedido: str, db: Session = Depends(get_db)):
    pedido = db.query(PedidoDB).filter(PedidoDB.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    pedido.status = StatusPedido.EM_PRODUCAO.value
    db.commit()
    return {"mensagem": f"Pedido #{id_pedido} em produção!"}

@app.put("/pedidos/{id_pedido}/entregar")
def registrar_entrega(id_pedido: str, db: Session = Depends(get_db)):
    pedido = db.query(PedidoDB).filter(PedidoDB.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    hoje = date.today()
    pedido.status = StatusPedido.ENTREGUE.value
    pedido.data_entrega_real = hoje
    pedido.entregue_no_prazo = (hoje <= pedido.prazo_entrega)
    db.commit()
    return {"mensagem": "Pedido entregue!", "no_prazo": pedido.entregue_no_prazo}

@app.get("/relatorio/fila-producao")
def ver_fila_producao(db: Session = Depends(get_db)):
    hoje = date.today()
    pedidos = db.query(PedidoDB).filter(PedidoDB.status == StatusPedido.EM_PRODUCAO.value).all()
    fila = []
    for p in pedidos:
        dias = (p.prazo_entrega - hoje).days
        fila.append({
            "id_pedido": p.id_pedido,
            "cliente": p.cliente_nome,
            "itens": p.descricao_itens,
            "prazo": p.prazo_entrega,
            "dias_restantes": dias,
            "alerta": "ATRASADO" if dias < 0 else ("URGENTE" if dias <= 2 else "OK")
        })
    return fila
