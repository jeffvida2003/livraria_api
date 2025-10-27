## Siga o passo a passo abaixo para executar o projeto:

1 - Garanta que o arquivo Dockerfile é o correto. No ambiente local, renomear os arquivos seguindo o formato abaixo:

```
  Dockerfile -> Dockerfile.prod
  Dockerfile.dev -> Dockerfile
```

2 - Executar o comando abaixo:

```docker compose up --build```

3 - Para testar, acesse uma das URLs abaixo:

[Swagger API Docs](http://localhost:8000/docs) |||
[Redoc API Docs](http://localhost:8000/redoc)
