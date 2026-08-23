# SentiNeo - Sensor Node Simulator

SentiNeo é um simulador de nós sensores para sistemas de monitoramento ambiental, com suporte a múltiplos modos de ataque para testes de resiliência.

## Visão Geral

O projeto implementa um nó sensor simulado que gera telemetria ambiental (temperatura, umidade, energia, vibração) e detecta eventos críticos através de uma engine de regras. Suporta modos de operação normais e ataques simulados.

## Funcionalidades

- **5 modos de operação:**
  - `normal` - operação padrão com variações aleatórias
  - `temperature` - ataque de incremento de temperatura
  - `energy` - ataque de consumo energético crescente
  - `vibration` - aumento progressivo de vibração
  - `door` - simulação de porta aberta
  - `random` - modo de ataque aleatório entre os acima

- **Engine de regras** que classifica telemetria em:
  - Eventos de temperatura (warning/critical)
  - Eventos de energia (warning/critical)
  - Eventos de vibração (warning/critical)
  - Detecção de porta aberta

- **Status do sistema:** online / warning / critical

- **Integração MQTT** para publicação de telemetria, status e eventos

## Estrutura do Projeto

```
sentineo/
├── .gitignore          # Padrões de exclusão
├── docker-compose.yml  # Configuração Docker
├── backend/            # Módulos backend (alerts, devices, rules, telemetry)
│   ├── alerts/
│   ├── devices/
│   ├── rules/
│   └── telemetry/
├── simulator/          # Simulador principal
│   ├── node.py         # Núcleo do simulador (432 lines)
│   ├── pyproject.toml  # Dependências Python
│   ├── .env           # Configuração de ambiente
│   ├── README.md      # Documentação do simulador
│   └── requirements.txt
└── README.md           # Documentação geral do projeto
```

## Como Executar

```bash
# Clone o repositório
git clone https://github.com/Lucasbig6/sentineo-alerts.git
cd sentineo

# Instale as dependências
pip install -r simulator/requirements.txt

# Execute o simulador
python simulator/node.py --attack normal
# ou com modo de ataque
python simulator/node.py --attack temperature
```

## Modos de Ataque

- **normal**: Variações aleatórias ao redor de bases (temp: 30°C, hum: 65%)
- **temperature**: Temperatura aumenta progressivamente (começa em 30°C, incrementa 0.5°C a cada passo)
- **energy**: Consumo energético aumenta progressivamente
- **vibration**: Vibração aumenta progressivamente
- **door**: Porta alterna entre aberto/fechado aleatoriamente
- **random**: Ataca com um modo aleatório entre temperature, energy, vibration, door

## Dependências

- numpy >= 2.5.2
- paho-mqtt >= 2.1.0
- python-dotenv >= 1.2.3

## Variáveis de Ambiente

Configurar o arquivo `.env` no diretório `simulator/`:
- `NODE_ID`: ID do nó (padrão: node-001)
- `MQTT_HOST`: Host do broker MQTT (padrão: localhost)
- `MQTT_PORT`: Porta MQTT (padrão: 1883)