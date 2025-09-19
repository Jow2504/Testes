import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# -------------------- CONFIGURAÇÃO --------------------
st.set_page_config(page_title="Sistema de Cadastro e Login", layout="wide")

st.markdown("""
<div style="text-align: center;">
<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTskwQub0SrrAmRQnXZCKKyLXOz-lGwg0lSgQ&s" alt="Logo" width="150">
</div>
""", unsafe_allow_html=True)

st.title("Sistema de Cadastro e Login Templo de Umbanda Cabocla Jurema e Caboclo Ubirajara")

# -------------------- ESTADO DE SESSÃO --------------------
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None

def sair():
    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.pagina = "Login"
    st.rerun()

# -------------------- BOTÃO SAIR --------------------
col1, col2 = st.columns([0.15, 0.85])
with col1:
    if st.session_state.logado:
        if st.button("⏏ Sair"):
            sair()

# -------------------- AUTENTICAÇÃO GOOGLE SHEETS --------------------
try:
    creds_dict_str = st.secrets["GDRIVE_CREDENTIALS"]
    creds_dict = dict(creds_dict_str) if isinstance(creds_dict_str, dict) else json.loads(json.dumps(creds_dict_str))
    creds = Credentials.from_service_account_info(creds_dict)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"Erro ao autenticar. Verifique se o segredo 'GDRIVE_CREDENTIALS' está correto. Detalhes: {e}")
    st.stop()

# -------------------- PLANILHA --------------------
PLANILHA_ID = "1I9ux6BVYQBbG-56VJCZ8ptRWnfJB_L0qJJVFGmw1C2A"
SHEET_NAME = "Página1"

try:
    spreadsheet = client.open_by_key(PLANILHA_ID)
    sheet = spreadsheet.worksheet(SHEET_NAME)
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}")
    st.stop()

# -------------------- FUNÇÕES --------------------
def carregar_dados():
    try:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def cadastrar_usuario(usuario, senha, nome, email):
    df = carregar_dados()
    if not usuario.strip() or not senha.strip():
        st.warning("Usuário e senha são obrigatórios!")
        return
    if not df.empty and "Usuario" in df.columns and usuario in df["Usuario"].values:
        st.error("Este usuário já existe!")
    else:
        try:
            sheet.append_row([usuario, senha, nome, email])
            st.success(f"Usuário {usuario} cadastrado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao cadastrar usuário: {e}")

def validar_login(usuario, senha):
    df = carregar_dados()
    if df.empty or "Usuario" not in df.columns or "Senha" not in df.columns:
        st.error("A planilha não contém colunas 'Usuario' e 'Senha'.")
        return False
    if usuario in df["Usuario"].values:
        senha_correta = str(df.loc[df["Usuario"] == usuario, "Senha"].values[0])
        if senha == senha_correta:
            return True
    return False

# -------------------- INTERFACE --------------------
if not st.session_state.logado:
    opcao = st.radio("Selecione a opção:", ["Login", "Cadastro"], horizontal=True)

    if opcao == "Cadastro":
        st.header("Cadastro de Novo Usuário")
        nome = st.text_input("Nome:")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha:", type="password")
        email = st.text_input("Email:")

        if st.button("Cadastrar"):
            cadastrar_usuario(usuario, senha, nome, email)

    elif opcao == "Login":
        st.header("Login de Usuário")
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")

        if st.button("Entrar"):
            if validar_login(usuario, senha):
                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.success(f"Bem-vindo, {usuario}! ✅")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")

else:
    st.sidebar.title("📑 Menu")
    opcao = st.sidebar.radio("Navegação", ["Inicio", "Giras/Louvações", "Complete seu cadastro", "Pagamento Mensalidade"])
    st.markdown(f"### 🔐 Usuário logado: {st.session_state.usuario}")

    if opcao == "Inicio":
        st.write("Bem-vindo à página inicial do sistema!")
    elif opcao == "Giras/Louvações":
        st.write("Eventos do Terreiro.")
    elif opcao == "Complete seu cadastro":
        st.write("Insira mais informações")
    elif opcao == "Pagamento Mensalidade":
        st.write("Efetue seu pagamento")
