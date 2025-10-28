# Troubleshooting - Erro 401 no Render

## Passos para Debug

### 1. Verificar se a API está online
```
GET https://seu-app.onrender.com/
GET https://seu-app.onrender.com/health
```

### 2. Verificar configurações
```
GET https://seu-app.onrender.com/debug/config
```
**Esperado**: 
- `secret_key_set: true`
- `secret_key_length > 0`
- `algorithm: "HS256"`

### 3. Testar criação de token
```
GET https://seu-app.onrender.com/debug/test-token
```
**Esperado**: `success: true`

### 4. Configurações necessárias no Render

No painel do Render, em **Environment Variables**, adicione:

```
SECRET_KEY=sua-chave-ultra-secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=postgresql://usuario:senha@host:5432/database
```

### 5. Teste completo do fluxo

1. **Criar usuário** (se ainda não existe):
```bash
curl -X POST "https://seu-app.onrender.com/usuarios" \
     -H "Content-Type: application/json" \
     -d '{"nome": "teste", "email": "teste@teste.com", "senha": "123456"}'
```

2. **Fazer login**:
```bash
curl -X POST "https://seu-app.onrender.com/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=teste&password=123456"
```

3. **Usar o token retornado** para acessar livros:
```bash
curl -X GET "https://seu-app.onrender.com/livros" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### 6. Verificar logs

No painel do Render, vá em **Logs** e procure por:
- `DEBUG LOGIN -`
- `DEBUG TOKEN -`
- `DEBUG -` (para autenticação)

## Possíveis Causas e Soluções

### Causa 1: SECRET_KEY diferente ou não configurada
**Solução**: Configurar corretamente no Render

### Causa 2: Problema de CORS
**Solução**: Já adicionado middleware CORS

### Causa 3: Formato do token incorreto
**Solução**: Verificar se está sendo enviado como "Bearer TOKEN"

### Causa 4: Token expirado
**Solução**: Verificar tempo de expiração (60 minutos padrão)

### Causa 5: Usuário não existe no banco do Render
**Solução**: Criar usuário novamente no ambiente de produção

## Como testar localmente

1. **Parar servidor local**
2. **Usar as mesmas variáveis do Render**:
```bash
export SECRET_KEY=sua-chave-ultra-secreta
export ALGORITHM=HS256
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```
3. **Iniciar servidor e testar**

## Limpeza após resolver

Após identificar e resolver o problema, remover:
- Todos os `print("DEBUG")` do código
- Endpoints `/debug/*`
- Este arquivo de troubleshooting