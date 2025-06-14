# Fluxo de Navegação do Usuário

## Fluxo Principal - Cliente

1. **Página Inicial/Login**
   - Cliente acessa o sistema
   - Opções: Login ou Criar Conta
   - Após login: Redirecionamento para Dashboard

2. **Dashboard do Cliente**
   - Visualização de próximos agendamentos
   - Botão "Novo Agendamento"
   - Acesso ao histórico de agendamentos
   - Edição de perfil

3. **Novo Agendamento**
   - Seleção do salão/barbearia
   - Escolha do serviço
   - Seleção de data e horário disponível
   - Confirmação do agendamento

4. **Gerenciamento de Agendamentos**
   - Visualização de agendamentos futuros
   - Opções: Reagendar ou Cancelar
   - Histórico de agendamentos passados

## Fluxo Principal - Prestador de Serviço

1. **Login do Prestador**
   - Acesso com credenciais de prestador
   - Redirecionamento para Dashboard Administrativo

2. **Dashboard Administrativo**
   - Visão geral dos agendamentos do dia
   - Estatísticas de agendamentos
   - Calendário mensal
   - Lista de próximos agendamentos

3. **Gestão de Agendamentos**
   - Visualização em calendário
   - Confirmação de agendamentos
   - Reagendamento de horários
   - Marcação como concluído

4. **Gestão de Serviços**
   - Cadastro de novos serviços
   - Edição de preços e duração
   - Ativação/desativação de serviços

5. **Gestão de Horários**
   - Definição de horários de funcionamento
   - Bloqueio de horários específicos
   - Configuração de intervalos

6. **Relatórios**
   - Relatório de agendamentos por período
   - Relatório de faturamento
   - Relatório de clientes mais frequentes

## Estados dos Agendamentos

- **Pendente:** Agendamento criado, aguardando confirmação
- **Confirmado:** Agendamento confirmado pelo prestador
- **Em Andamento:** Serviço sendo realizado
- **Concluído:** Serviço finalizado
- **Cancelado:** Agendamento cancelado por qualquer parte
- **Não Compareceu:** Cliente não compareceu no horário

## Notificações

- **Para Clientes:**
  - Confirmação de agendamento
  - Lembrete 24h antes
  - Lembrete 2h antes
  - Notificação de cancelamento/reagendamento

- **Para Prestadores:**
  - Novo agendamento recebido
  - Cancelamento de agendamento
  - Lembrete de agendamentos do dia

