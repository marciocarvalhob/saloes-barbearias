from flask import Blueprint, jsonify, request, g
from functools import wraps
import jwt # Assumindo que JWT é usado para tokens

# Cria um Blueprint para as rotas de usuário.
user_bp = Blueprint('user', __name__)

# --- INÍCIO DA ADIÇÃO DE token_required ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token de autenticação está faltando!'}), 401

        try:
            # IMPORTANTE: A SECRET_KEY REAL do JWT precisa vir de main.py ou de uma config.
            # Por agora, use uma temporária ou tente pegar de uma variável de ambiente.
            # Se main.py já define JWT_SECRET_KEY, é melhor passar aqui ou ter uma forma de acessá-la.
            # Para simplificar agora, vamos usar uma string temporária.
            # Se o sistema real da Manus tiver uma config global, o ideal é usar essa.
            # Ex: current_app.config['JWT_SECRET_KEY']
            # Ou usar uma variável de ambiente, como 'SECRET_KEY'
            data = jwt.decode(token, os.environ.get('JWT_SECRET_KEY', 'sua_chave_secreta_padrao_aqui'), algorithms=["HS256"])
            # Assumindo que o token decodificado contém um 'user_id' ou 'id'
            # Você pode precisar importar seu modelo de usuário aqui se 'g.user' precisar ser um objeto completo
            # from models.user import User # Se seu modelo User estiver em models/user.py
            # g.user = User.query.get(data['user_id']) # Se usar SQLAlchemy
            g.user = data # Apenas para que algo esteja em g.user para passar.
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirou!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido!'}), 401
        except Exception as e:
            return jsonify({'message': 'Erro no token: ' + str(e)}), 401

        return f(*args, **kwargs)
    return decorated
# --- FIM DA ADIÇÃO DE token_required ---

# Exemplo de rota de teste (apenas para evitar erros de inicialização)
@user_bp.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "Rota de usuário de teste funcionando!"}), 200

# Você pode adicionar mais rotas aqui, se souber onde elas estavam ou se quiser criar novas.