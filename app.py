import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from supabase import create_client, Client

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Productivity Dash", page_icon="✅", layout="wide")

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- FUNÇÕES DE DADOS ---
def fetch_tasks(selected_date):
    """Busca tarefas filtradas pela data alvo."""
    response = supabase.table("tarefas") \
        .select("*") \
        .eq("data_alvo", str(selected_date)) \
        .order("id") \
        .execute()
    return response.data

def update_task_status(task_id, new_status):
    """Atualiza o status da tarefa no banco de dados."""
    supabase.table("tarefas") \
        .update({"status": new_status}) \
        .eq("id", task_id) \
        .execute()
    # Limpa o cache para forçar recarregamento se necessário (neste app usamos state)

# --- SIDEBAR / FILTROS ---
st.sidebar.title("Configurações")
filtro_data = st.sidebar.date_input("Filtrar por Data", date.today())

# --- BUSCA DE DADOS ---
data = fetch_tasks(filtro_data)
df = pd.DataFrame(data)

# --- CABEÇALHO ---
st.title(f"📊 Dashboard de Produtividade")
st.subheader(f"Tarefas de {filtro_data.strftime('%d/%m/%Y')}")

if not df.empty:
    # --- MÉTRICAS ---
    total_tarefas = len(df)
    concluidas = len(df[df['status'] == 'Concluido'])
    pendentes = total_tarefas - concluidas
    progresso = (concluidas / total_tarefas)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Tarefas", total_tarefas)
    col2.metric("Concluídas", concluidas, f"{int(progresso*100)}%")
    col3.metric("Pendentes", pendentes)

    st.divider()

    # --- LISTA DE TAREFAS E GRÁFICO ---
    col_lista, col_grafico = st.columns([1, 1])

    with col_lista:
        st.write("### 📝 Minhas Tarefas")
        
        # Iterar pelas tarefas para criar checkboxes
        for index, row in df.iterrows():
            # Criar uma chave única para cada checkbox baseada no ID e Status
            is_done = row['status'] == 'Concluido'
            
            # Layout de linha para a tarefa
            t_col1, t_col2 = st.columns([0.1, 0.9])
            
            # Checkbox para atualizar status
            with t_col1:
                check = st.checkbox("", value=is_done, key=f"task_{row['id']}")
                
                # Lógica de atualização imediata
                new_status = "Concluido" if check else "Pendente"
                if new_status != row['status']:
                    update_task_status(row['id'], new_status)
                    st.rerun() # Recarrega para atualizar métricas e interface

            with t_col2:
                # Se concluído, risca o texto
                texto = f"~~{row['titulo']}~~" if is_done else row['titulo']
                st.markdown(f"{texto} `({row['categoria']})`")

    with col_grafico:
        st.write("### 📊 Tarefas por Categoria")
        # Agrupar dados para o gráfico
        df_counts = df.groupby('categoria').size().reset_index(name='quantidade')
        fig = px.bar(
            df_counts, 
            x='categoria', 
            y='quantidade',
            color='categoria',
            labels={'quantidade': 'Nº de Tarefas', 'categoria': 'Categoria'},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Nenhuma tarefa encontrada para esta data. Que tal descansar? ☕")

# --- CSS CUSTOMIZADO (OPCIONAL) ---
st.markdown("""
    <style>
    .stCheckbox { margin-bottom: 0.5rem; }
    [data-testid="stMetricValue"] { font-size: 28px; }
    </style>
    """, unsafe_allow_html=True)
