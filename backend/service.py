from flask import Blueprint, request, jsonify
from src.models.user import db, Service, Provider
from src.routes.user import token_required

service_bp = Blueprint('service', __name__)

@service_bp.route('/services', methods=['GET'])
def get_services():
    try:
        provider_id = request.args.get('provider_id')
        
        if provider_id:
            services = Service.query.filter_by(provider_id=provider_id, is_active=True).all()
        else:
            services = Service.query.filter_by(is_active=True).all()
        
        services_data = []
        for service in services:
            service_data = service.to_dict()
            service_data['provider_name'] = service.provider.business_name
            services_data.append(service_data)
        
        return jsonify({'services': services_data}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@service_bp.route('/services', methods=['POST'])
@token_required
def create_service(current_user):
    try:
        if current_user.user_type != 'provider':
            return jsonify({'message': 'Apenas prestadores podem criar serviços'}), 403
        
        if not current_user.provider_profile:
            return jsonify({'message': 'Perfil de prestador não encontrado'}), 404
        
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('name') or not data.get('duration_minutes') or not data.get('price'):
            return jsonify({'message': 'Nome, duração e preço são obrigatórios'}), 400
        
        service = Service(
            provider_id=current_user.provider_profile.id,
            name=data['name'],
            description=data.get('description', ''),
            duration_minutes=int(data['duration_minutes']),
            price=float(data['price'])
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço criado com sucesso',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@service_bp.route('/services/<int:service_id>', methods=['PUT'])
@token_required
def update_service(current_user, service_id):
    try:
        if current_user.user_type != 'provider':
            return jsonify({'message': 'Apenas prestadores podem atualizar serviços'}), 403
        
        service = Service.query.get_or_404(service_id)
        
        if service.provider_id != current_user.provider_profile.id:
            return jsonify({'message': 'Você não tem permissão para atualizar este serviço'}), 403
        
        data = request.get_json()
        
        if data.get('name'):
            service.name = data['name']
        if data.get('description'):
            service.description = data['description']
        if data.get('duration_minutes'):
            service.duration_minutes = int(data['duration_minutes'])
        if data.get('price'):
            service.price = float(data['price'])
        if 'is_active' in data:
            service.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço atualizado com sucesso',
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@service_bp.route('/services/<int:service_id>', methods=['DELETE'])
@token_required
def delete_service(current_user, service_id):
    try:
        if current_user.user_type != 'provider':
            return jsonify({'message': 'Apenas prestadores podem deletar serviços'}), 403
        
        service = Service.query.get_or_404(service_id)
        
        if service.provider_id != current_user.provider_profile.id:
            return jsonify({'message': 'Você não tem permissão para deletar este serviço'}), 403
        
        # Marcar como inativo ao invés de deletar
        service.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Serviço desativado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@service_bp.route('/my-services', methods=['GET'])
@token_required
def get_my_services(current_user):
    try:
        if current_user.user_type != 'provider':
            return jsonify({'message': 'Apenas prestadores podem acessar esta rota'}), 403
        
        if not current_user.provider_profile:
            return jsonify({'message': 'Perfil de prestador não encontrado'}), 404
        
        services = Service.query.filter_by(provider_id=current_user.provider_profile.id).all()
        
        return jsonify({'services': [service.to_dict() for service in services]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

