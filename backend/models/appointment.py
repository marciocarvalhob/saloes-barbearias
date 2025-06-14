from flask import Blueprint, request, jsonify
from src.models.user import db, Appointment, Service, Provider, User
from src.routes.user import token_required
from datetime import datetime, timedelta

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments', methods=['GET'])
@token_required
def get_appointments(current_user):
    try:
        # Filtros opcionais
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Query base dependendo do tipo de usuário
        if current_user.user_type == 'client':
            query = Appointment.query.filter_by(client_id=current_user.id)
        elif current_user.user_type == 'provider':
            if not current_user.provider_profile:
                return jsonify({'message': 'Perfil de prestador não encontrado'}), 404
            query = Appointment.query.filter_by(provider_id=current_user.provider_profile.id)
        else:
            return jsonify({'message': 'Tipo de usuário inválido'}), 400
        
        # Aplicar filtros
        if status:
            query = query.filter_by(status=status)
        
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(Appointment.appointment_date >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(Appointment.appointment_date <= date_to_obj)
        
        appointments = query.order_by(Appointment.appointment_date.desc()).all()
        
        return jsonify({'appointments': [appointment.to_dict() for appointment in appointments]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@appointment_bp.route('/appointments', methods=['POST'])
@token_required
def create_appointment(current_user):
    try:
        if current_user.user_type != 'client':
            return jsonify({'message': 'Apenas clientes podem criar agendamentos'}), 403
        
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['provider_id', 'service_id', 'appointment_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} é obrigatório'}), 400
        
        # Verificar se o serviço existe e está ativo
        service = Service.query.get(data['service_id'])
        if not service or not service.is_active:
            return jsonify({'message': 'Serviço não encontrado ou inativo'}), 404
        
        # Verificar se o prestador existe
        provider = Provider.query.get(data['provider_id'])
        if not provider:
            return jsonify({'message': 'Prestador não encontrado'}), 404
        
        # Verificar se o serviço pertence ao prestador
        if service.provider_id != provider.id:
            return jsonify({'message': 'Serviço não pertence ao prestador selecionado'}), 400
        
        # Converter data do agendamento
        try:
            appointment_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Formato de data inválido'}), 400
        
        # Verificar se a data não é no passado
        if appointment_date <= datetime.utcnow():
            return jsonify({'message': 'Não é possível agendar para datas passadas'}), 400
        
        # Verificar conflitos de horário
        service_end_time = appointment_date + timedelta(minutes=service.duration_minutes)
        
        conflicting_appointments = Appointment.query.filter(
            Appointment.provider_id == provider.id,
            Appointment.status.in_(['pending', 'confirmed']),
            Appointment.appointment_date < service_end_time,
            db.func.datetime(Appointment.appointment_date, f'+{service.duration_minutes} minutes') > appointment_date
        ).first()
        
        if conflicting_appointments:
            return jsonify({'message': 'Horário não disponível'}), 409
        
        # Criar agendamento
        appointment = Appointment(
            client_id=current_user.id,
            provider_id=provider.id,
            service_id=service.id,
            appointment_date=appointment_date,
            notes=data.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Agendamento criado com sucesso',
            'appointment': appointment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@token_required
def update_appointment(current_user, appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Verificar permissões
        if current_user.user_type == 'client' and appointment.client_id != current_user.id:
            return jsonify({'message': 'Você não tem permissão para atualizar este agendamento'}), 403
        elif current_user.user_type == 'provider':
            if not current_user.provider_profile or appointment.provider_id != current_user.provider_profile.id:
                return jsonify({'message': 'Você não tem permissão para atualizar este agendamento'}), 403
        
        data = request.get_json()
        
        # Atualizar status (principalmente para prestadores)
        if data.get('status') and current_user.user_type == 'provider':
            valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'no_show']
            if data['status'] in valid_statuses:
                appointment.status = data['status']
        
        # Atualizar notas
        if data.get('notes'):
            appointment.notes = data['notes']
        
        # Reagendamento (apenas se status for pending)
        if data.get('appointment_date') and appointment.status == 'pending':
            try:
                new_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00'))
                if new_date > datetime.utcnow():
                    appointment.appointment_date = new_date
            except ValueError:
                return jsonify({'message': 'Formato de data inválido'}), 400
        
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Agendamento atualizado com sucesso',
            'appointment': appointment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@token_required
def cancel_appointment(current_user, appointment_id):
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Verificar permissões
        if current_user.user_type == 'client' and appointment.client_id != current_user.id:
            return jsonify({'message': 'Você não tem permissão para cancelar este agendamento'}), 403
        elif current_user.user_type == 'provider':
            if not current_user.provider_profile or appointment.provider_id != current_user.provider_profile.id:
                return jsonify({'message': 'Você não tem permissão para cancelar este agendamento'}), 403
        
        # Verificar se pode ser cancelado
        if appointment.status in ['completed', 'cancelled']:
            return jsonify({'message': 'Agendamento não pode ser cancelado'}), 400
        
        appointment.status = 'cancelled'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Agendamento cancelado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@appointment_bp.route('/available-slots', methods=['GET'])
def get_available_slots():
    try:
        provider_id = request.args.get('provider_id')
        service_id = request.args.get('service_id')
        date = request.args.get('date')  # YYYY-MM-DD
        
        if not all([provider_id, service_id, date]):
            return jsonify({'message': 'provider_id, service_id e date são obrigatórios'}), 400
        
        # Verificar se o serviço existe
        service = Service.query.get(service_id)
        if not service or not service.is_active:
            return jsonify({'message': 'Serviço não encontrado'}), 404
        
        # Verificar se o prestador existe
        provider = Provider.query.get(provider_id)
        if not provider:
            return jsonify({'message': 'Prestador não encontrado'}), 404
        
        # Converter data
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Formato de data inválido (use YYYY-MM-DD)'}), 400
        
        # Gerar horários disponíveis (exemplo: 8h às 18h, de 30 em 30 minutos)
        available_slots = []
        start_hour = 8
        end_hour = 18
        slot_duration = 30  # minutos
        
        current_time = datetime.combine(target_date, datetime.min.time().replace(hour=start_hour))
        end_time = datetime.combine(target_date, datetime.min.time().replace(hour=end_hour))
        
        while current_time < end_time:
            # Verificar se não há conflito com agendamentos existentes
            service_end_time = current_time + timedelta(minutes=service.duration_minutes)
            
            conflicting = Appointment.query.filter(
                Appointment.provider_id == provider.id,
                Appointment.status.in_(['pending', 'confirmed']),
                Appointment.appointment_date < service_end_time,
                db.func.datetime(Appointment.appointment_date, f'+{service.duration_minutes} minutes') > current_time
            ).first()
            
            if not conflicting and current_time > datetime.utcnow():
                available_slots.append(current_time.isoformat())
            
            current_time += timedelta(minutes=slot_duration)
        
        return jsonify({'available_slots': available_slots}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

