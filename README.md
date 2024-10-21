# backend-cook-together
Backend do projeto CookTogether. Feito em Django.

## Endpoints públicos do projeto
- Base URL: `cooktogether.duckdns.org`
- API base URL: `cooktogether.duckdns.org/api`
  - Exemplo: `cooktogether.duckdns.org/api/recipes/recipe`
- Swagger: `cooktogether.duckdns.org/swagger`
- Painel admin: `cooktogether.duckdns.org/admin`

> As credenciais de login do painel de admin do endpoint público se encontram no card `[CT-04 OPS] Realizar deployment do código no servidor Oracle` no Trello.

## Desenvolvimento local

Para realizar o desenvolvimento local, é necessário configurar a variável de ambiente `DJANGO_ENV` para o valor `dev`, através do comando:
- Linux: `export DJANGO_ENV=dev`
- Windows: `set DJANGO_ENV=dev`
- Ou então crie um arquivo .env na pasta raiz, contendo `DJANGO_ENV=dev`

Quando DJANGO_ENV for igual a dev, será utilizado o ambiente de desenvolvimento, ou seja:
- Será gerado e utilizado um banco sqlite3 local, presente na pasta raiz do projeto
- Imagens de receitas criadas serão guardadas no bucket `recipes_dev` do supabase.

## CI/CD
Foi implementada uma esteira CI/CD para enviar o código presente na main para um servidor rodando na nuvem Oracle. A esteira é ativada a partir de qualquer commit ou merge de PR na `main` (apenas abrir um PR não ativa a esteira).

É recomendado que alterações sejam feitas primeiro em um branch separada de desenvolvimento, e após as devidas validações e testes locais, seja aberto um PR e feito o merge com a Main.

## Utilizando endpoints protegidos
Para a utilização de certos endpoints, é necessário estar autenticado. A autenticação é feita passando um token (Bearer Token) na requisição, sendo este token obtido ao realizar login no endpoint de login (consultar Swagger).

## Criando receitas com e sem imagens
O endpoint `/api/recipes/recipe/create/` é o endpoint que aceita requisições POST para criação de receitas. Entretanto, é importante se atentar que é para a criação de receitas contendo uma imagem, é necessário passar o campo `image` contendo uma string base64 de uma imagem que foi previamente codificada.

Exemplo:
```json
{
  "title": "Minha receita de exemplo",
  "ingredients": [
    {
      "name": "Água",
      "quantity": 1,
      "unit": "Copo"
    }
  ],
  "text_area": "Minha string contendo informações de como fazer a receita",
  "image_base64": "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BSJTEUAAQEAAkZXNjAAAA8A...restante do base64 aqui"
}
```

A string base64 do campo `image_base64` será decodificada e enviada para o bucket do Supabase. O retorno da requisição, e consequentemente, o que será salvo no banco de dados, será o campo `image` que contém o link públcio da imagem presente no bucket do Supabase

Exemplo de retorno da requisição acima:
```json
{
    "id": 1,
    "user": "[Nome do usuário que criou a receita aqui]",
    "title": "Minha receita de exemplo",
    "ingredients": [
        {
            "name": "Água",
            "quantity": 1.0,
            "unit": "Copo"
        }
    ],
    "text_area": "Minha string contendo informações de como fazer a receita",
    "image": "https://[URL do Supabase aqui]/storage/v1/object/public/recipes/recipes/oCpHYBkI3ejAkDJq3efMMbSbAUzDOK.jpg"
}
```

Caso queira criar uma receita sem imagem, basta não passar o campo `image_base64`, ou então passar o campo `image` com valor `null`:
```json
{
    "id": 1,
    "user": "[Nome do usuário que criou a receita aqui]",
    "title": "Minha receita de exemplo",
    "ingredients": [
        {
            "name": "Água",
            "quantity": 1.0,
            "unit": "Copo"
        }
    ],
    "text_area": "Minha string contendo informações de como fazer a receita",
    "image": null
}
```