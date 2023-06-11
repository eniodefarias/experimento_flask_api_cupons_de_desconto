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

# Definindo o endpoint para cadastro de cupons
@app.route('/coupons', methods=['POST'])
def create_coupon():
    # Obter os dados do cupom do corpo da requisição
    data = request.get_json()
    # Validar se os dados estão completos
    if not data or not all(key in data for key in ['code', 'expiration_date', 'max_uses', 'min_value', 'discount_type', 'discount_amount', 'public', 'first_purchase']):
        return jsonify({'error': 'Dados incompletos'}), 400
    # Validar se o código do cupom já existe no banco de dados
    if Coupon.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Código já existe'}), 400
    # Validar se a data de expiração é válida
    try:
        expiration_date = datetime.fromisoformat(data['expiration_date'])
        if expiration_date < datetime.now():
            return jsonify({'error': 'Data de expiração inválida'}), 400
    except ValueError:
        return jsonify({'error': 'Data de expiração inválida'}), 400

    # Criar um objeto Coupon com os dados do cupom
    coupon = Coupon(
        code=data['code'],
        expiration_date=expiration_date,
        max_uses=data['max_uses'],
        min_value=data['min_value'],
        discount_type=data['discount_type'],
        discount_amount=data['discount_amount'],
        public=data['public'],
        first_purchase=data['first_purchase']
    )
    # Adicionar o cupom no banco de dados
    db.session.add(coupon)
    db.session.commit()
    # Retornar uma resposta com o cupom criado
    return jsonify(coupon.__dict__), 201

# Definindo o endpoint para consumo dos cupons
@app.route('/coupons/<code>', methods=['POST'])
def use_coupon(code):
    # Obter os dados da compra do corpo da requisição
    data = request.get_json()
    # Validar se os dados estão completos
    if not data or not all(key in data for key in ['total_value', 'first_purchase']):
        return jsonify({'error': 'Dados incompletos'}), 400
    # Buscar o cupom pelo código no banco de dados
    coupon = Coupon.query.filter_by(code=code).first()
    # Validar se o cupom existe
    if not coupon:
        return jsonify({'error': 'Cupom não encontrado'}), 404
    # Validar se o cupom é válido para a compra
    valid, error = coupon.is_valid(data['total_value'], data['first_purchase'])
    if not valid:
        return jsonify({'error': error}), 400
    # Calcular o valor do desconto do cupom para a compra
    discount_value = coupon.get_discount_value(data['total_value'])
    # Atualizar o número de usos do cupom no banco de dados
    coupon.max_uses -= 1
    db.session.commit()
    # Retornar uma resposta com o valor do desconto e o id do cupom usado
    return jsonify({'discount_value': discount_value, 'coupon_id': coupon.id}), 200

# Rodar a aplicação Flask na porta 5000
if __name__ == '__main__':
    app.run(port=5000)
