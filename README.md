experimento_flask_api_cupons_de_desconto

Essa é uma API REST desenvolvida em Python e Flask que permite o cadastro e o consumo de cupons de desconto.



# API de Cupons de Desconto

Essa é uma API REST desenvolvida em Python e Flask que permite o cadastro e o consumo de cupons de desconto. Os cupons de desconto têm as seguintes regras:

## Validade do cupom

Um cupom de desconto será válido, caso atenda os seguintes requisitos:

- A data de utilização seja inferior à data de expiração
- O número de utilizações seja menor que o número máximo de utilizações. Exemplo:
um cupom pode ter no máximo 500 utilizações.
- O valor total da compra seja menor que o valor mínimo para utilização do cupom.
Exemplo: Um cupom só será válido para compras maiores que 100 reais.

## Tipos de desconto

Será possível cadastrar três tipos de desconto:

- Percentual de desconto aplicado ao valor total. Exemplo: Se o valor da compra é
100 reais e o percentual de desconto é 30, o valor final é 70
- Desconto de valor fixo, destinado ao público geral. Exemplo: Se o valor da compra é
150 reais e o valor do desconto é 10 reais, o valor final é 140
- Desconto de valor fixo, para o caso de ser a primeira compra do cliente no site. Caso
o desconto seja exclusivo para primeira compra e o usuário já efetuou alguma
compra anteriormente, o desconto é inválido. Exemplo: Se for a primeira compra e o
valor for 150 e o valor do desconto é 10 reais, o valor final é 140. Caso contrário,
deve ser gerado um erro para o usuário.

## Preparando o ambiente

Para executar essa API, você precisa ter instalado o Python 3 e o pip na sua máquina. Depois, você precisa instalar as dependências do projeto usando o seguinte comando:

```bash
pip install -r requirements.txt
```

Isso vai instalar as bibliotecas Flask e SQLAlchemy, que são necessárias para rodar a aplicação.

## Executando a aplicação

Para executar a aplicação, você pode usar o seguinte comando no terminal:

```bash
python app.py
```

Isso vai iniciar um servidor local na porta 5000. Você pode acessar a API usando a URL http://localhost:5000.

## Endpoints da API

A API possui dois endpoints: um para cadastro de cupons e outro para consumo dos cupons.

### Cadastro de cupons

O endpoint para cadastro de cupons é:

```
POST /coupons
```

Esse endpoint recebe um objeto JSON no corpo da requisição com os dados do cupom a ser cadastrado. Os dados do cupom são:

- código do cupom: deve ser único, não podendo haver dois cupons com o mesmo
código
- data de expiração: data e hora de até quando o cupom é válido. A vigência do
cupom inicia a partir de quando o mesmo é cadastrado
- número máximo de utilizações.
- valor mínimo de compra

- tipo de desconto e quantidade do desconto
- indicativo se é destinado ao público geral
- indicativo se é valido apenas para a primeira compra

Um exemplo de objeto JSON válido para cadastrar um cupom é:

```json
{
  "code": "ABC123",
  "expiration_date": "2023-12-31T23:59:59",
  "max_uses": 500,
  "min_value": 100,
  "discount_type": "percentual",
  "discount_amount": 30,
  "public": true,
  "first_purchase": false
}
```

Se o cadastro for bem sucedido, esse endpoint retorna uma resposta com código 201 (Created) e um objeto JSON com os dados do cupom criado. Um exemplo de resposta válida é:

```json
{
    "id": 1,
    "code": "ABC123",
    "expiration_date": "2023-12-31T23:59:59",
    "max_uses": 500,
    "min_value": 100,
    "discount_type": "percentual",
    "discount_amount": 30,
    "public": true,
    "first_purchase": false
}
```

Se o cadastro for mal sucedido, esse endpoint retorna uma resposta com código 400 (Bad Request) e um objeto JSON com uma mensagem de erro indicando o motivo do cadastro ter sido recusado. Alguns exemplos de respostas inválidas são:

```json
{
    "error": "Dados incompletos"
}
```

```json
{
    "error": "Código já existe"
}
```

```json
{
    "error": "Data de expiração inválida"
}
```

### Consumo dos cupons

O endpoint para consumo dos cupons é:

```
POST /coupons/<code>
```

Esse endpoint recebe um objeto JSON no corpo da requisição com os dados da compra a ser realizada com o cupom. Os dados da compra são:

- valor total da compra
- indicativo de primeira compra

Um exemplo de objeto JSON válido para consumir um cupom é:

```json
{
  "total_value": 150,
  "first_purchase": true
}
```

Se o consumo for bem sucedido, esse endpoint retorna uma resposta com código 200 (OK) e um objeto JSON com os dados do cupom usado. Um exemplo de resposta válida é:

```json
{
    "discount_value": 10,
    "coupon_id": 1
}
```

Se o consumo for mal sucedido, esse endpoint retorna uma resposta com código 400 (Bad Request) ou 404 (Not Found) e um objeto JSON com uma mensagem de erro indicando o motivo do consumo ter sido recusado. Alguns exemplos de respostas inválidas são:

```json
{
    "error": "Cupom não encontrado"
}
```

```json
{
    "error": "Cupom expirado"
}
```

```json
{
    "error": "Cupom esgotado"
}
```

```json
{
    "error": "Valor mínimo não atingido"
}
```

```json
{
    "error": "Cupom não é destinado ao público geral"
}
```

```json
{
    "error": "Cupom é válido apenas para a primeira compra"
}
```

## Testes da aplicação

Para testar a aplicação, você pode usar o módulo unittest do Python. O arquivo test_app.py contém alguns testes unitários para os endpoints da API. Para executar os testes, você pode usar o seguinte comando no terminal:

```bash
python -m unittest test_app.py
```

Isso vai executar todos os testes definidos na classe TestApp e mostrar os resultados na tela. Você pode ver se os testes passaram ou falharam e quantos casos de teste foram executados.








## Testando

para testar essa API REST, pode-se usar alguma ferramenta como o Postman ou o cURL. Por exemplo, para cadastrar um cupom usando o cURL, você pode usar o seguinte comando:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"code": "ABC123", "expiration_date": "2023-12-31T23:59:59", "max_uses": 500, "min_value": 100, "discount_type": "percentual", "discount_amount": 30, "public": true, "first_purchase": false}' http://localhost:5000/coupons
```

Para consumir um cupom usando o cURL, você pode usar o seguinte comando:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"total_value": 150, "first_purchase": true}' http://localhost:5000/coupons/ABC123
```