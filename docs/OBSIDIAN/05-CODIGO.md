# Código e Implementação

## 🎯 Padrões de Projeto

### Factory Pattern
```python
class ServiceFactory:
    @staticmethod
    def create_calendar_service():
        # Criação do serviço
```

### Strategy Pattern
```python
class CommandProcessor:
    def __init__(self, strategy):
        self.strategy = strategy
```

## 🔍 Processamento de Comandos

### Expressões Regulares
```python
patterns = {
    'data': r'dia (\d{1,2}/\d{1,2}(?:/\d{4})?)',
    'hora': r'(\d{1,2})[h:](\d{2})',
}
```

#codigo #padroes #implementacao 