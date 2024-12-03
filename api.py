from flask import Flask, request, Response
import sqlite3
from collections import OrderedDict
import json

app = Flask(__name__)

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('loja_cliente.db')
    conn.row_factory = sqlite3.Row  # Permite acessar as colunas por nome
    return conn

# Função para converter uma linha de cliente em dicionário na ordem correta
def cliente_row_to_dict(row):
    return OrderedDict([
        ("id", row["id"]),
        ("nome", row["nome"]),
        ("sobrenome", row["sobrenome"]),
        ("email", row["email"]),
        ("telefone", row["telefone"]),
        ("endereco", row["endereco"]),
        ("cidade", row["cidade"]),
        ("estado", row["estado"]),
        ("cep", row["cep"]),
        ("data_cadastro", row["data_cadastro"])
    ])

# Função para converter uma linha de produto em dicionário na ordem correta
def produto_row_to_dict(row):
    return OrderedDict([
        ("id", row["id"]),
        ("nome", row["nome"]),
        ("descricao", row["descricao"]),
        ("preco", row["preco"]),
        ("estoque", row["estoque"]),
        ("data_adicionado", row["data_adicionado"])
    ])

# Rota GET para listar todos os clientes
@app.route('/clientes', methods=['GET'])
def get_clientes():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM Cliente').fetchall()
    conn.close()

    clientes_list = [cliente_row_to_dict(cliente) for cliente in clientes]
    return Response(json.dumps(clientes_list, ensure_ascii=False), mimetype='application/json'), 200

# Rota GET para buscar um cliente por ID
@app.route('/clientes/<int:id>', methods=['GET'])
def get_cliente(id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM Cliente WHERE id = ?', (id,)).fetchone()
    conn.close()

    if cliente is None:
        return Response(json.dumps({"error": "Cliente não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    return Response(json.dumps(cliente_row_to_dict(cliente), ensure_ascii=False), mimetype='application/json'), 200

# Rota POST para criar um novo cliente
@app.route('/clientes', methods=['POST'])
def create_cliente():
    data = request.get_json()

    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    email = data.get('email')
    telefone = data.get('telefone')
    endereco = data.get('endereco')
    cidade = data.get('cidade')
    estado = data.get('estado')
    cep = data.get('cep')

    if not nome or not sobrenome or not email:
        return Response(json.dumps({"error": "Nome, sobrenome e email são obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO Cliente (nome, sobrenome, email, telefone, endereco, cidade, estado, cep, data_cadastro) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime("now"))',
                 (nome, sobrenome, email, telefone, endereco, cidade, estado, cep))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Cliente criado com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 201

# Rota PUT para atualizar um cliente por ID
@app.route('/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    data = request.get_json()
    nome = data.get('nome')
    sobrenome = data.get('sobrenome')
    email = data.get('email')
    telefone = data.get('telefone')
    endereco = data.get('endereco')
    cidade = data.get('cidade')
    estado = data.get('estado')
    cep = data.get('cep')

    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM Cliente WHERE id = ?', (id,)).fetchone()
    
    if cliente is None:
        conn.close()
        return Response(json.dumps({"error": "Cliente não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    conn.execute('''
        UPDATE Cliente
        SET nome = ?, sobrenome = ?, email = ?, telefone = ?, endereco = ?, cidade = ?, estado = ?, cep = ?
        WHERE id = ?
    ''', (nome, sobrenome, email, telefone, endereco, cidade, estado, cep, id))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Cliente atualizado com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 200


# Rota DELETE para excluir um cliente por ID
@app.route('/clientes/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM Cliente WHERE id = ?', (id,)).fetchone()

    if cliente is None:
        conn.close()
        return Response(json.dumps({"error": "Cliente não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    conn.execute('DELETE FROM Cliente WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Cliente excluído com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 200


# Rota GET para listar todos os itens do pedido
@app.route('/itensPedido', methods=['GET'])
def get_itens_pedido():
    conn = get_db_connection()
    itens_pedido = conn.execute('SELECT * FROM ItensPedido').fetchall()
    conn.close()

    itens_pedido_list = [
        OrderedDict([
            ("id", item["id"]),
            ("pedido_id", item["pedido_id"]),
            ("produto_id", item["produto_id"]),
            ("quantidade", item["quantidade"]),
            ("preco_unitario", item["preco_unitario"])
        ])
        for item in itens_pedido
    ]
    return Response(json.dumps(itens_pedido_list, ensure_ascii=False), mimetype='application/json'), 200


# Rota GET para buscar um item do pedido por ID
@app.route('/itensPedido/<int:id>', methods=['GET'])
def get_item_pedido(id):
    conn = get_db_connection()
    item_pedido = conn.execute('SELECT * FROM ItensPedido WHERE id = ?', (id,)).fetchone()
    conn.close()

    if item_pedido is None:
        return Response(json.dumps({"error": "Item do pedido não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    item_pedido_dict = OrderedDict([
        ("id", item_pedido["id"]),
        ("pedido_id", item_pedido["pedido_id"]),
        ("produto_id", item_pedido["produto_id"]),
        ("quantidade", item_pedido["quantidade"]),
        ("preco_unitario", item_pedido["preco_unitario"])
    ])
    return Response(json.dumps(item_pedido_dict, ensure_ascii=False), mimetype='application/json'), 200

# Rota POST para criar um novo item do pedido
@app.route('/itensPedido', methods=['POST'])
def create_item_pedido():
    data = request.get_json()
    pedido_id = data.get('pedido_id')
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade')
    preco_unitario = data.get('preco_unitario')

    if not pedido_id or not produto_id or quantidade is None or preco_unitario is None:
        return Response(json.dumps({"error": "Todos os campos (pedido_id, produto_id, quantidade, preco_unitario) são obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO ItensPedido (pedido_id, produto_id, quantidade, preco_unitario)
        VALUES (?, ?, ?, ?)
    ''', (pedido_id, produto_id, quantidade, preco_unitario))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Item do pedido criado com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 201


# Rota PUT para atualizar um item do pedido por ID
@app.route('/itensPedido/<int:id>', methods=['PUT'])
def update_item_pedido(id):
    data = request.get_json()
    pedido_id = data.get('pedido_id')
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade')
    preco_unitario = data.get('preco_unitario')

    if not pedido_id or not produto_id or quantidade is None or preco_unitario is None:
        return Response(json.dumps({"error": "Todos os campos (pedido_id, produto_id, quantidade, preco_unitario) são obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    conn = get_db_connection()
    item_pedido = conn.execute('SELECT * FROM ItensPedido WHERE id = ?', (id,)).fetchone()

    if item_pedido is None:
        conn.close()
        return Response(json.dumps({"error": "Item do pedido não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    conn.execute('''
        UPDATE ItensPedido
        SET pedido_id = ?, produto_id = ?, quantidade = ?, preco_unitario = ?
        WHERE id = ?
    ''', (pedido_id, produto_id, quantidade, preco_unitario, id))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Item do pedido atualizado com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 200

# Rota DELETE para excluir um item do pedido por ID
@app.route('/itensPedido/<int:id>', methods=['DELETE'])
def delete_item_pedido(id):
    conn = get_db_connection()
    item_pedido = conn.execute('SELECT * FROM ItensPedido WHERE id = ?', (id,)).fetchone()

    if item_pedido is None:
        conn.close()
        return Response(json.dumps({"error": "Item do pedido não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    conn.execute('DELETE FROM ItensPedido WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Item do pedido excluído com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 200

# Rota DELETE para excluir um pedido por ID
@app.route('/pedidos/<int:id>', methods=['DELETE'])
def delete_pedido(id):
    conn = get_db_connection()
    pedido = conn.execute('SELECT * FROM Pedido WHERE id = ?', (id,)).fetchone()

    if pedido is None:
        conn.close()
        return Response(json.dumps({"error": "Pedido não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    conn.execute('DELETE FROM Pedido WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Pedido excluído com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 200




# Rota GET para listar todos os produtos
@app.route('/produtos', methods=['GET'])
def get_produtos():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM Produto').fetchall()
    conn.close()

    produtos_list = [produto_row_to_dict(produto) for produto in produtos]
    return Response(json.dumps(produtos_list, ensure_ascii=False), mimetype='application/json'), 200

# Rota GET para buscar um produto por ID
@app.route('/produtos/<int:id>', methods=['GET'])
def get_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM Produto WHERE id = ?', (id,)).fetchone()
    conn.close()

    if produto is None:
        return Response(json.dumps({"error": "Produto não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    return Response(json.dumps(produto_row_to_dict(produto), ensure_ascii=False), mimetype='application/json'), 200

# Rota POST para criar um novo produto
@app.route('/produtos', methods=['POST'])
def create_produto():
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')
    preco = data.get('preco')
    estoque = data.get('estoque')

    if not nome or preco is None or estoque is None:
        return Response(json.dumps({"error": "Nome, preço e estoque são obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO Produto (nome, descricao, preco, estoque, data_adicionado) VALUES (?, ?, ?, ?, datetime("now"))',
                 (nome, descricao, preco, estoque))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Produto criado com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 201

# Rota PUT para atualizar um produto por ID
@app.route('/produtos/<int:id>', methods=['PUT'])
def update_produto(id):
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')
    preco = data.get('preco')
    estoque = data.get('estoque')

    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM Produto WHERE id = ?', (id,)).fetchone()
    
    if produto is None:
        conn.close()
        return Response(json.dumps({"error": "Produto não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    conn.execute('''
        UPDATE Produto
        SET nome = ?, descricao = ?, preco = ?, estoque = ?
        WHERE id = ?
    ''', (nome, descricao, preco, estoque, id))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Produto atualizado com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 200

# Rota DELETE para excluir um produto por ID
@app.route('/produtos/<int:id>', methods=['DELETE'])
def delete_produto(id):
    conn = get_db_connection()
    produto = conn.execute('SELECT * FROM Produto WHERE id = ?', (id,)).fetchone()

    if produto is None:
        conn.close()
        return Response(json.dumps({"error": "Produto não encontrado"}, ensure_ascii=False), mimetype='application/json'), 404

    conn.execute('DELETE FROM Produto WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return Response(json.dumps({"message": "Produto excluído com sucesso!"}, ensure_ascii=False), mimetype='application/json'), 200





if __name__ == '__main__':
    app.run(debug=True)
