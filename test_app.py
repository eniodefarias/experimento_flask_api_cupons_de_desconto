# Importando as bibliotecas necessárias
import unittest
from app import app, db, Coupon, Use
from datetime import datetime


# Criando a classe de testes
class TestApp(unittest.TestCase):

    # Configurando o banco de dados de teste
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = app.test_client()
        db.create_all()

    # Removendo o banco de dados de teste
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Testando o cadastro de um cupom válido
    def test_create_coupon_valid(self):
        data = {"code": "ABC123", "expiration_date": "2023-12-31T23:59:59", "max_uses": 500, "min_value": 100, "discount_type": "percentual", "discount_amount": 30, "public": True, "first_purchase": False}
        response = self.client.post('/coupons', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['code'], data['code'])
        self.assertEqual(response.json['expiration_date'], data['expiration_date'])
        self.assertEqual(response.json['max_uses'], data['max_uses'])
        self.assertEqual(response.json['min_value'], data['min_value'])
        self.assertEqual(response.json['discount_type'], data['discount_type'])
        self.assertEqual(response.json['discount_amount'], data['discount_amount'])
        self.assertEqual(response.json['public'], data['public'])
        self.assertEqual(response.json['first_purchase'], data['first_purchase'])

    # Testando o cadastro de um cupom inválido (código já existente)
    def test_create_coupon_invalid_code(self):
        coupon = Coupon(code="ABC123", expiration_date=datetime(2023, 12, 31, 23, 59, 59), max_uses=500, min_value=100, discount_type="percentual", discount_amount=30, public=True, first_purchase=False)

        db.session.add(coupon)
        db.session.commit()

        data = {"code": "ABC123", "expiration_date": "2023-12-31T23:59:59", "max_uses": 500, "min_value": 100, "discount_type": "percentual", "discount_amount": 30, "public": True, "first_purchase": False}

        response = self.client.post('/coupons', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Código já existe')

    # Testando o cadastro de um cupom inválido (data de expiração passada)
    def test_create_coupon_invalid_date(self):
        data = {"code": "ABC123", "expiration_date": "2020-12-31T23:59:59", "max_uses": 500, "min_value": 100, "discount_type": "percentual", "discount_amount": 30, "public": True, "first_purchase": False}

        response = self.client.post('/coupons', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Data de expiração inválida')

    # Testando o cadastro de um cupom inválido (dados incompletos)
    def test_create_coupon_invalid_data(self):
        data = {# código do cupom faltando
            # expiration_date faltando
            # max_uses faltando
            # min_value faltando
            # discount_type faltando
            # discount_amount faltando
            # public faltando
            # first_purchase faltando
        }

        response = self.client.post('/coupons', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Dados incompletos')

    # Testando o consumo de um cupom válido (desconto percentual para público geral)
    def test_use_coupon_valid_percentual_public(self):
        coupon = Coupon(code="ABC123", expiration_date=datetime(2023, 12, 31, 23, 59, 59), max_uses=500, min_value=100, discount_type="percentual", discount_amount=30, public=True, first_purchase=False)

        db.session.add(coupon)
        db.session.commit()

        data = {"total_value": 150, "first_purchase": False}

        response = self.client.post('/coupons/ABC123', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['discount_value'], 45)
        self.assertEqual(response.json['coupon_id'], coupon.id)

    # Testando o consumo de um cupom válido (desconto fixo para primeira compra)
    def test_use_coupon_valid_fixo_first(self):
        coupon = Coupon(code="ABC123", expiration_date=datetime(2023, 12, 31, 23, 59, 59), max_uses=500, min_value=100, discount_type="fixo", discount_amount=10, public=False, first_purchase=True)

        db.session.add(coupon)
        db.session.commit()

        data = {"total_value": 150, "first_purchase": True}

        response = self.client.post('/coupons/ABC123', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['discount_value'], 10)
        self.assertEqual(response.json['coupon_id'], coupon.id)

    # Testando o consumo de um cupom inválido (cupom não encontrado)
    def test_use_coupon_invalid_not_found(self):
        data = {"total_value": 150, "first_purchase": False}

        response = self.client.post('/coupons/ABC123', json=data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Cupom não encontrado')

    # Testando o consumo de um cupom inválido (cupom expirado)
    def test_use_coupon_invalid_expired(self):
        coupon = Coupon(code="ABC123", expiration_date=datetime(2020, 12, 31, 23, 59, 59), max_uses=500, min_value=100, discount_type="percentual", discount_amount=30, public=True, first_purchase=False)

        db.session.add(coupon)
        db.session.commit()

        data = {"total_value": 150, "first_purchase": False}

        response = self.client.post('/coupons/ABC123', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Cupom expirado')

    # Testando o consumo de um cupom inválido (cupom esgotado)
    def test_use_coupon_invalid_exhausted(self):
        coupon = Coupon(code="ABC123", expiration_date=datetime(2023, 12, 31, 23, 59, 59), max_uses=1, min_value=100, discount_type="percentual", discount_amount=30, public=True, first_purchase=False)

        use = Use(coupon_id=coupon.id, use_date=datetime.now())

        db.session.add(coupon)
        db.session.add(use)
        db.session.commit()

        data = {"total_value": 150, "first_purchase": False}

        response = self.client.post('/coupons/ABC123', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Cupom esgotado')

    # Testando o consumo de um cupom inválido (valor mínimo não atingido)
    def test_use_coupon_invalid_min_value(self):
        coupon = Coupon(code="ABC123", expiration_date=datetime(2023, 12, 31, 23, 59, 59), max_uses=500, min_value=100, discount_type="percentual", discount_amount=30, public=True, first_purchase=False)

        db.session.add(coupon)
        db.session.commit()

        data = {"total_value": 50, "first_purchase": False}

        response = self.client.post('/coupons/ABC123', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], 'Valor mínimo não atingido')

    # Testando o consumo de um cupom inválido (cupom não destinado ao público geral)
    def test_use_coupon_invalid_not_public(self):
