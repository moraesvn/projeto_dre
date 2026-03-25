# Regras de Desenvolvimento - Projeto DRE

## Princípios Gerais

### 1. Execução Incremental
- **Uma etapa por vez**: Sempre executar apenas uma etapa de cada vez
- **Aprovação obrigatória**: Perguntar ao desenvolvedor antes de prosseguir para a próxima etapa
- **Blocos pequenos**: Trabalhar com mudanças pequenas e focadas, não grandes refatorações de uma vez

### 2. Comunicação
- **Explicação resumida**: Após cada etapa, explicar brevemente o que foi feito
- **Clareza**: Descrever o objetivo e o resultado de cada mudança
- **Transparência**: Informar quais arquivos foram modificados/criados

### 3. Estrutura de Trabalho

#### Antes de Iniciar
1. Entender o contexto da tarefa
2. Identificar os arquivos que serão afetados
3. Planejar as etapas necessárias

#### Durante a Execução
1. Executar **apenas uma etapa**
2. Fazer commit/checkpoint lógico (se aplicável)
3. Explicar o que foi feito
4. **Perguntar**: "Posso continuar para a próxima etapa?"

#### Após Concluir
1. Resumir todas as mudanças realizadas
2. Verificar se há erros de lint/compilação
3. Confirmar se a funcionalidade está completa

### 4. Tamanho das Mudanças
- **Máximo**: Uma função, uma classe ou um arquivo pequeno por etapa
- **Evitar**: Múltiplas mudanças não relacionadas na mesma etapa
- **Priorizar**: Mudanças que podem ser testadas isoladamente

### 5. Validação
- Verificar erros de sintaxe após cada etapa
- Testar funcionalidade básica quando aplicável
- Não assumir que tudo funcionará sem validação

### 6. Documentação
- Comentar mudanças significativas no código
- Atualizar documentação quando necessário
- Manter histórico claro das alterações

## Exemplo de Fluxo

```
Etapa 1: Criar função auxiliar X
→ Explicação: "Criei a função X em utils.py para processar dados Y"
→ Pergunta: "Posso continuar para a próxima etapa?"

Etapa 2: Integrar função X no módulo Z
→ Explicação: "Integrei a função X no módulo Z, substituindo a lógica antiga"
→ Pergunta: "Posso continuar para a próxima etapa?"

[...]
```

## Exceções

- Correções de bugs críticos podem ser feitas em etapas maiores se necessário
- Mudanças puramente cosméticas (formatação, espaços) podem ser agrupadas
- Sempre comunicar exceções ao desenvolvedor

---


