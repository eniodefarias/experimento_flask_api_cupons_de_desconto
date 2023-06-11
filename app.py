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


# Definindo o modelo da tabela de cupons
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
    uses = db.relationship('Use', backref='coupon', lazy=True)

    def __repr__(self):
        return f"<Coupon {self.code}>"


# Definindo o modelo da tabela de usos dos cupons
class Use(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'), nullable=False)
    use_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Use {self.coupon_id} {self.use_date}>"


# Criando as tabelas no banco de dados
db.create_all()


# Definindo o endpoint para cadastro de cupons
@app.route('/coupons', methods=['POST'])
def create_coupon():
    # Obtendo os dados do cupom do corpo da requisição
    data = request.get_json()
    code = data.get('code')
    expiration_date = data.get('expiration_date')
    max_uses = data.get('max_uses')
    min_value = data.get('min_value')
    discount_type = data.get('discount_type')
    discount_amount = data.get('discount_amount')
    public = data.get('public')
    first_purchase = data.get('first_purchase')

    # Validando os dados do cupom
    if not code or not expiration_date or not max_uses or not min_value or not discount_type or not discount_amount or public is None or first_purchase is None:
        return jsonify({'error': 'Dados incompletos'}), 400

    if Coupon.query.filter_by(code=code).first():
        return jsonify({'error': 'Código já existe'}), 400

    if expiration_date < datetime.now():
        return jsonify({'error': 'Data de expiração inválida'}), 400

    if max_uses <= 0 or min_value <= 0 or discount_amount <= 0:
        return jsonify({'error': 'Valores inválidos'}), 400

    if discount_type not in ['percentual', 'fixo', 'primeira']:
        return jsonify({'error': 'Tipo de desconto inválido'}), 400

    # Criando o objeto do cupom e salvando no banco de dados
    coupon = Coupon(code=code, expiration_date=expiration_date, max_uses=max_uses, min_value=min_value, discount_type=discount_type, discount_amount=discount_amount, public=public, first_purchase=first_purchase)

    db.session.add(coupon)
    db.session.commit()

    # Retornando uma resposta de sucesso com os dados do cupom criado
    return jsonify({'id': coupon.id, 'code': coupon.code, 'expiration_date': coupon.expiration_date.isoformat(), 'max_uses': coupon.max_uses, 'min_value': coupon.min_value, 'discount_type': coupon.discount_type, 'discount_amount': coupon.discount_amount, 'public': coupon.public, 'first_purchase': coupon.first_purchase}), 201


# Definindo o endpoint para consumo dos cupons
@app.route('/coupons/<code>', methods=['POST'])
def use_coupon(code):
    # Obtendo os dados da compra do corpo da requisição
    data = request.get_json()
    total_value = data.get('total_value')
    first_purchase = data.get('first_purchase')

    # Validando os dados da compra
    if not total_value or first_purchase is None:
        return jsonify({'error': 'Dados incompletos'}), 400

    if total_value <= 0:
        return jsonify({'error': 'Valor inválido'}), 400

    # Buscando o cupom pelo código
    coupon = Coupon.query.filter_by(code=code).first()

    # Verificando se o cupom existe
    if not coupon:
        return jsonify({'error': 'Cupom não encontrado'}), 404

    # Verificando se o cupom está expirado
    if coupon.expiration_date < datetime.now():
        return jsonify({'error': 'Cupom expirado'}), 400

    # Verificando se o cupom atingiu o número máximo de usos
    if len(coupon.uses) >= coupon.max_uses:
        return jsonify({'error': 'Cupom esgotado'}), 400

    # Verificando se o valor da compra é maior que o valor mínimo do cupom
    if total_value < coupon.min_value:
        return jsonify({'error': 'Valor mínimo não atingido'}), 400

    # Verificando se o cupom é destinado ao público geral ou à primeira compra
    if not coupon.public and not first_purchase:
        return jsonify({'error': 'Cupom não é destinado ao público geral'}), 400

    if coupon.first_purchase and not first_purchase:
        return jsonify({'error': 'Cupom é válido apenas para a primeira compra'}), 400

    # Calculando o valor do desconto de acordo com o tipo de desconto
    if coupon.discount_type == 'percentual':
        discount_value = total_value * coupon.discount_amount / 100
    else:
        discount_value = coupon.discount_amount

    # Criando o objeto do uso do cupom e salvando no banco de dados
    use = Use(coupon_id=coupon.id, use_date=datetime.now())

    db.session.add(use)
    db.session.commit()

    # Retornando uma resposta de sucesso com os dados do cupom usado
    return jsonify({'discount_value': discount_value, 'coupon_id': coupon.id}), 200


# Executando a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)
