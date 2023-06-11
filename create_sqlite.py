# Importando as bibliotecas necessárias
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Criando a aplicação Flask
app = Flask(__name__)

# Configurando a conexão com o banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coupons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definindo a classe Coupon que representa a tabela de cupons no banco de dados
class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    max_uses = db.Column(db.Integer, nullable=False)
    min_value = db.Column(db.Float, nullable=False)
    discount_type = db.Column(db.String(10), nullable=False)
    discount_amount = db.Column(db.Float, nullable=False)
    public = db.Column(db.Boolean, nullable=False)
    first_purchase = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<Coupon {self.code}>"

    # Método para validar se um cupom é válido para uma compra
    def is_valid(self, total_value, first_purchase):
        # Verificar se o cupom não está expirado
        if self.expiration_date < datetime.now():
            return False, "Cupom expirado"
        # Verificar se o cupom não está esgotado
        if self.max_uses <= 0:
            return False, "Cupom esgotado"
        # Verificar se o valor da compra atinge o valor mínimo do cupom
        if total_value < self.min_value:
            return False, "Valor mínimo não atingido"
        # Verificar se o cupom é destinado ao público geral ou à primeira compra
        if not self.public and not first_purchase:
            return False, "Cupom não é destinado ao público geral"
        if self.first_purchase and not first_purchase:
            return False, "Cupom é válido apenas para a primeira compra"
        # Se passar por todas as verificações, o cupom é válido
        return True, None

    # Método para calcular o valor do desconto de um cupom para uma compra
    def get_discount_value(self, total_value):
        # Se o tipo de desconto é percentual, calcular o valor proporcional ao valor da compra
        if self.discount_type == "percentual":
            return total_value * (self.discount_amount / 100)
        # Se o tipo de desconto é fixo, retornar o valor do desconto
        elif self.discount_type == "fixo":
            return self.discount_amount
        # Se o tipo de desconto é inválido, retornar zero
        else:
            return 0

# Criando as tabelas no banco de dados SQLite
db.create_all()
