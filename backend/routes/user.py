from flask import Blueprint, jsonify, request

# Cria um Blueprint para as rotas de usuário.
# user_bp é o objeto que main.py tenta importar.
user_bp = Blueprint('user', __name__)

# Exemplo de rota de teste (apenas para evitar erros de inicialização)
@user_bp.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "Rota de usuário de teste funcionando!"}), 200

# Você pode adicionar mais rotas aqui, se souber onde elas estavam ou se quiser criar novas.