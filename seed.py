"""
Script de Inicialização e População de Dados (Seed).
Atividade Prática - Arquitetura e Desenvolvimento de APIs - UNINTER.

Cria as tabelas no banco de dados SQLite (catalogo.db) e insere categorias
e produtos de demonstração para testes imediatos.

Execução:
    python seed.py
"""
import sys
from app.database import engine, Base, SessionLocal
from app.models import Categoria, Produto

def popular_banco():
    print("=" * 65)
    print("Inicializando banco de dados e aplicando semente de dados...")
    print("=" * 65)

    # Cria todas as tabelas mapeadas no SQLAlchemy
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Verifica se já existem categorias para evitar duplicações desnecessárias
        if db.query(Categoria).count() > 0:
            print("O banco de dados já contém registros. Limpando dados antigos para recarga...")
            db.query(Produto).delete()
            db.query(Categoria).delete()
            db.commit()

        # 1. Criação de Categorias Iniciais
        categorias_dados = [
            {"nome": "Informática", "descricao": "Computadores, periféricos e suprimentos de TI"},
            {"nome": "Smartphones & Telefonia", "descricao": "Aparelhos celulares, carregadores e suportes"},
            {"nome": "Móveis para Escritório", "descricao": "Cadeiras ergonômicas, mesas e organizadores"},
            {"nome": "Áudio & Vídeo", "descricao": "Headsets, fones TWS, caixas de som e microfones"}
        ]

        categorias_criadas = {}
        for cat in categorias_dados:
            c = Categoria(nome=cat["nome"], descricao=cat["descricao"])
            db.add(c)
            db.flush()  # Para obter o ID gerado
            categorias_criadas[cat["nome"]] = c
            print(f"[+] Categoria criada: {c.nome} (ID: {c.id})")

        # 2. Criação de Produtos Iniciais
        produtos_dados = [
            {
                "nome": "Mouse Gamer Ergonômico RGB",
                "descricao": "Mouse óptico com sensor de 12.000 DPI, 7 botões programáveis e cabo trançado.",
                "preco": 149.90,
                "estoque": 35,
                "codigo_sku": "INF-MOU-001",
                "categoria_id": categorias_criadas["Informática"].id,
                "ativo": True
            },
            {
                "nome": "Teclado Mecânico ABNT2 Switch Blue",
                "descricao": "Teclado mecânico compacto 75%, iluminação Rainbow e teclas em double-shot injection.",
                "preco": 289.00,
                "estoque": 20,
                "codigo_sku": "INF-TEC-002",
                "categoria_id": categorias_criadas["Informática"].id,
                "ativo": True
            },
            {
                "nome": "Monitor UltraWide 29 Polegadas Full HD",
                "descricao": "Painel IPS, 75Hz, HDR10, tempo de resposta de 1ms MBR com entradas HDMI.",
                "preco": 1199.90,
                "estoque": 12,
                "codigo_sku": "INF-MON-003",
                "categoria_id": categorias_criadas["Informática"].id,
                "ativo": True
            },
            {
                "nome": "Carregador Rápido GaN 65W USB-C",
                "descricao": "Carregador ultra compacto com tecnologia Nitreto de Gálio para notebooks e celulares.",
                "preco": 189.50,
                "estoque": 50,
                "codigo_sku": "TEL-CAR-001",
                "categoria_id": categorias_criadas["Smartphones & Telefonia"].id,
                "ativo": True
            },
            {
                "nome": "Suporte Articulado de Mesa para Celular",
                "descricao": "Suporte metálico regulável com rotação 360 graus e base antiderrapante.",
                "preco": 59.90,
                "estoque": 80,
                "codigo_sku": "TEL-SUP-002",
                "categoria_id": categorias_criadas["Smartphones & Telefonia"].id,
                "ativo": True
            },
            {
                "nome": "Cadeira Ergonômica Presidente Mesh",
                "descricao": "Apoio lombar ajustável, braços 3D e mecanismo relax com trava em múltiplas posições.",
                "preco": 890.00,
                "estoque": 8,
                "codigo_sku": "MOV-CAD-001",
                "categoria_id": categorias_criadas["Móveis para Escritório"].id,
                "ativo": True
            },
            {
                "nome": "Headset Gamer com Cancelamento de Ruído",
                "descricao": "Drivers de 50mm, microfone cardioide destacável e almofadas com espuma viscoelástica.",
                "preco": 349.90,
                "estoque": 15,
                "codigo_sku": "AUD-HED-001",
                "categoria_id": categorias_criadas["Áudio & Vídeo"].id,
                "ativo": True
            }
        ]

        for p in produtos_dados:
            prod = Produto(**p)
            db.add(prod)
            print(f"[+] Produto criado: {prod.nome} | R$ {prod.preco:.2f} | SKU: {prod.codigo_sku}")

        db.commit()
        print("=" * 65)
        print(f"Sucesso! {len(categorias_dados)} categorias e {len(produtos_dados)} produtos inseridos.")
        print("Banco de dados pronto para testes e avaliações!")
        print("=" * 65)
    except Exception as e:
        db.rollback()
        print(f"Erro ao inicializar dados: {e}", file=sys.stderr)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    popular_banco()
