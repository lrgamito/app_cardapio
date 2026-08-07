# 🍽️ App de Cardápio Semanal

Aplicativo local em Python para gerenciar receitas e gerar um cardápio semanal com regras fixas de seleção.

## ✨ O que o app faz

- Mantém um banco local de receitas em texto no arquivo `data/recipes.json`
- Gera uma semana completa de `Domingo` a `Sábado`
- Define `Domingo / Janta` sempre como `Café`
- Evita repetir o mesmo prato na mesma semana
- Dá peso maior para `Hamburguer`, `Pizza`, `Esfiha` e `Lanche` em `Sexta-feira` e `Sábado`

## 🧱 Estrutura principal

- `app.py`: entrada do aplicativo local
- `cardapio/planner.py`: regras de geração do cardápio
- `cardapio/storage.py`: persistência local em JSON
- `data/recipes.json`: banco textual das receitas
## ⚙️ Requisitos

- Python `3.11+`

## 🚀 Como rodar

1. Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Instale a dependência do app:

```powershell
pip install -r requirements.txt
```

3. Inicie a interface local:

```powershell
streamlit run app.py
```

4. Abra o navegador no endereço exibido pelo Streamlit, normalmente `http://localhost:8501`.

## 🗂️ Como usar

### Aba `Cardápio semanal`

- Clique em `Gerar cardápio semanal`
- O app monta 7 dias em ordem fixa, começando no domingo e terminando no sábado
- Cada dia recebe `Almoço` e `Janta`
- O mesmo prato não se repete na mesma semana

### Aba `Receitas`

- Cadastre pratos como:
  - `Café`
  - `Pizza`
  - `Esfiha`
- Edite ou exclua receitas existentes
- Pesquise por nome ou ingrediente

## 📌 Regras do gerador

- Sempre gera exatamente 7 dias
- Ordem fixa: `Domingo`, `Segunda-feira`, `Terça-feira`, `Quarta-feira`, `Quinta-feira`, `Sexta-feira`, `Sábado`
- `Domingo / Janta` é sempre `Café`
- `Hamburguer`, `Pizza`, `Esfiha` e pratos com `Lanche` no nome ganham peso maior em `Sexta-feira` e `Sábado`
- O app exige pelo menos 14 receitas únicas para fechar a semana inteira

## 💾 Banco local em texto

O app usa JSON como banco local:

- `data/recipes.json`: receitas e ingredientes

## 🧪 Testes

Para rodar os testes locais:

```powershell
python -m unittest discover -s tests
```

## 📝 Observações

- Se `Café` não estiver cadastrado, o app bloqueia a geração do cardápio e orienta o cadastro
- O banco operacional do app é o JSON local em `data/recipes.json`