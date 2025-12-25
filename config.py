import os
import streamlit as st

# Função para pegar variáveis (prioriza Streamlit secrets)
def get_config(key):
    # Primeiro tenta pegar do Streamlit secrets (produção)
    try:
        return st.secrets[key]
    except:
        # Se não encontrar, pega do ambiente
        return os.getenv(key)

SUPABASE_URL = get_config("SUPABASE_URL")
SUPABASE_KEY = get_config("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN = get_config("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = get_config("GEMINI_API_KEY")
