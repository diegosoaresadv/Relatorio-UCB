# ⚖️ Sistema de Gestão de Processos Judiciais

Aplicação web desenvolvida em **Python + Streamlit** para controle, cadastro e acompanhamento de processos judiciais, com geração de relatórios e exportação de dados.

---

## ✨ Funcionalidades

- **Dashboard interativo** com KPIs e gráficos consolidados (status, probabilidade de perda, provisões)
- **Cadastro de processos** com formulário completo e validação de campos
- **Edição e exclusão** de processos existentes com confirmação
- **Filtros avançados** por status, aba, probabilidade de perda, risco, natureza e faixa de valor
- **Exportação de relatórios** em `.csv` e `.xlsx` (com aba de resumo financeiro)
- **Importação de CSV** para restauração ou atualização da base de dados

---

## 🗂️ Estrutura do Projeto

```
.
├── app.py                  # Aplicação principal
├── requirements.txt        # Dependências Python
├── README.md
├── assets/
│   └── logo.png            # Logotipo da organização
├── data/
│   └── processos.csv       # Base de dados local (gerada automaticamente)
└── .streamlit/
    └── config.toml         # Tema e configurações do Streamlit
```

---

## ⚙️ Requisitos

- Python **3.10** ou superior
- pip

Dependências listadas em `requirements.txt`:

```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
```

---

## 🚀 Como Executar Localmente

**1. Clone ou baixe o projeto:**

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

**2. Crie e ative um ambiente virtual (recomendado):**

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**4. Execute a aplicação:**

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`.

---

## ☁️ Deploy no Streamlit Cloud

1. Faça o **push** do projeto para um repositório no GitHub (certifique-se de incluir `assets/`, `data/` e `.streamlit/`).
2. Acesse [share.streamlit.io](https://share.streamlit.io) e clique em **New app**.
3. Selecione o repositório, a branch e aponte o **Main file path** para `app.py`.
4. Clique em **Deploy** — as dependências serão instaladas automaticamente via `requirements.txt`.

> **Atenção:** O sistema de arquivos do Streamlit Cloud é efêmero. Os dados cadastrados durante a sessão serão perdidos ao reiniciar o servidor. Para persistência em produção, recomenda-se integrar um banco de dados externo (ex.: PostgreSQL, Supabase ou Google Sheets via API).

---

## 📋 Campos do Formulário

| Campo | Tipo |
|---|---|
| Aba / Categoria | Seleção |
| Parte Contrária | Texto livre |
| Número CNJ | Texto livre (obrigatório, único) |
| Natureza | Seleção |
| Objeto da Ação | Seleção + campo livre |
| Posição do Cliente | Seleção |
| Valor da Causa (R$) | Numérico |
| Pedido | Seleção |
| Contingência | Seleção |
| Fase Processual | Seleção + campo livre |
| Probabilidade de Perda | Seleção |
| Custas Processuais | Texto livre |
| Garantia / Depósito | Texto livre |
| Valor da Garantia (R$) | Numérico |
| Provisão / Valor Estimado de Perda (R$) | Numérico |
| Data do Último Andamento | Data |
| Matéria | Seleção + campo livre |
| Processo Administrativo | Texto livre |
| Descrição / Andamento | Texto longo |
| Risco | Seleção |
| Tipo de Ação | Seleção + campo livre |
| Status | Seleção |

---

## 🔄 Fluxo de Uso Recomendado

```
Cadastrar Processo → Acompanhar Andamentos (Editar) → Gerar Relatório → Exportar CSV/Excel
```

Para **restaurar uma base exportada anteriormente**, acesse a página *Relatório e Exportação* e utilize a seção **Importar CSV**.

---

## 🛠️ Tecnologias Utilizadas

| Biblioteca | Finalidade |
|---|---|
| [Streamlit](https://streamlit.io) | Interface web |
| [Pandas](https://pandas.pydata.org) | Manipulação de dados |
| [Plotly](https://plotly.com/python/) | Gráficos interativos |
| [OpenPyXL](https://openpyxl.readthedocs.io) | Exportação Excel |

---

## 📄 Licença

Uso interno. Todos os direitos reservados.
