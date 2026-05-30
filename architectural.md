# Arquitetura do Projeto RCai Virtual Track

## Visão Geral
O sistema implementa uma plataforma virtual de corrida simulada, conectando-perfis de veículos com componentes emissores de dados via interface serial (emulador Arduino). O fluxo principal envolve:
- Configuração do circuito
- Gestão de perfis de veículos
- Atribuição de gestos a pistas
- Simulação de tempo real da corrida

## Componentes Principais

### 1. Configuração do Circuito (config/track.json)
- Responsável por:
  - Definir parâmetros de comunicação serial (porta, baudrate)
  - Especificar topology do circuito
- Fonte de dados para:
  - Arduino Emulator (conexão física)
  - Lane Assignment (ajuste de posições)

### 2. Gerenciador de Perfis de Veículos (vehicle_profiles/profiles.json)
- Estrutura:
  - IDs únicos para cada perfil
  - Especificações técnicas dos veículos
- Funcionalidades:
  - Busca de perfis por ID
  - Validação de compatibilidade com pistas

### 3. Sistema de Atribuição de Gestos (orchestrator/lane_assignment.py)
- Lógica central para:
  - Mapear veículos às pistas
  - Verificar conflito de atribuções
- Interface:
  - Métodos conforme necessidade (atualização, exclusão, leitura)

### 4. Motor de Simulação de Corrida (orchestrator/race_runtime.py)
- Funções principais:
  - Inicialização do emulador
  - Controle do ciclo de vida da simulação
  - Integração com perfis e atribuições
- Dependência: Recebe todas as configurações como entrada

### 5. Arduino Emulador (track_interface/arduino_emulator.py)
- Responsável por:
  - Simular comunicação serial
  - Tratamento de sinais de sensores/virtual
- Parâmetros de configuração:
  - Porta serial
  - Taxa de baud

## Fluxo de Operação
1. Load do config/track.json para inicializar comunicação
2. Carregamento dos perfis de veículos
3. Atribuição inicial de veículos às pistas
4. Inicialização do emulador Arduino
5. Início do motor de runtime com loop contínuo

## Dependências
- Arquivos de configuração:
  - config/track.json
  - vehicle_profiles/profiles.json
- Bibliotecas:
  - Serial comunicação (via pySerial)
  - Estruturas JSON

## Pontos de Extensão
1. Adicionar validação de perfil em tempo real
2. Interface gráfica para definição de pistas