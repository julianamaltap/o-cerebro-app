import os
from dotenv import load_dotenv
import streamlit as st

# Tentar carregar do arquivo .env local (desenvolvimento)
load_dotenv()

# Função para pegar variáveis (prioriza Streamlit secrets em produção)
def get_config(key):
    # Primeiro tenta pegar do Streamlit secrets (produção)
    try:
        return st.secrets[key]
    except:
        # Se não encontrar, pega do ambiente (desenvolvimento)
        return os.getenv(key)

SUPABASE_URL = get_config("https://oawnaldplwsnitvffvjn.supabase.co")
SUPABASE_KEY = get_config("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9hd25hbGRwbHdzbml0dmZmdmpuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1MTYzNzUsImV4cCI6MjA4MjA5MjM3NX0.2y9b-ieBLioOlcmFGqtAZ-I-757STMTGtGQDU0LJ8c8")
TELEGRAM_BOT_TOKEN = get_config("8529392302:AAHxGs04XvW_7yEeqqTX6wuvJvnYL_zTyrI")
GEMINI_API_KEY = get_config("AIzaSyBLjjMsi-hI6dpdhmNZ0ezmMX2p7qwFwSY")
