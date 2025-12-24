import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from database import TaskDatabase
from productivity_analyzer import ProductivityAnalyzer
from llm_processor import TaskProcessor

st.set_page_config(page_title="Dashboard de Tarefas", layout="wide", page_icon="📊")

db = TaskDatabase()
analyzer = ProductivityAnalyzer()
processor = TaskProcessor()

# Input do User ID
st.sidebar.title("⚙️ Configurações")
USER_ID = st.sidebar.number_input("Seu Telegram User ID", min_value=1, value=123456789, help="Digite seu ID do Telegram")

st.title("📊 Dashboard de Produtividade Inteligente")

# Sidebar com análises
with st.sidebar:
    st.header("🧠 Insights Inteligentes")
    
    if st.button("🔄 Atualizar Análise", type="primary"):
        with st.spinner("Analisando seu comportamento..."):
            try:
                analyzer.run_full_analysis(USER_ID)
                st.success("✅ Análise atualizada!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro na análise: {e}")
    
    analytics = db.get_latest_analytics(USER_ID)
    
    if analytics:
        st.subheader("⏰ Seus Melhores Horários")
        st.metric("Hora Mais Produtiva", f"{analytics['best_completion_hour']}:00h")
        st.metric("Hora Menos Produtiva", f"{analytics['worst_completion_hour']}:00h")
        
        st.subheader("📅 Melhores Dias")
        days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        st.metric("Melhor Dia", days[analytics['best_day_of_week']])
        st.metric("Pior Dia", days[analytics['worst_day_of_week']])
        
        st.subheader("📈 Performance")
        st.metric("Score de Produtividade", f"{analytics['productivity_score']:.1f}/100")
        
        st.subheader("⏰ Notificação Ajustada")
        settings = db.get_user_notification_settings(USER_ID)
        if settings:
            st.info(f"🔔 Lembrete: {settings['reminder_notification_time']}")
        
        st.subheader("💡 Sugestões Personalizadas")
        if st.button("Gerar Sugestões com IA"):
            with st.spinner("Gemini analisando..."):
                try:
                    suggestions = processor.suggest_task_optimization(analytics)
                    st.markdown(suggestions)
                except Exception as e:
                    st.error(f"Erro: {e}")
    else:
        st.info("👆 Clique em 'Atualizar Análise' para começar")

# Filtros de data
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Data inicial", date.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("Data final", date.today())

# Buscar dados
try:
    tasks = db.get_tasks_for_dashboard(USER_ID, start_date, end_date)
    df = pd.DataFrame(tasks)

    if not df.empty:
        df['task_date'] = pd.to_datetime(df['task_date'])
        df['completed_at'] = pd.to_datetime(df['completed_at'])
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(df)
            st.metric("Total de Tarefas", total_tasks)
        
        with col2:
            completed = len(df[df['status'] == 'completed'])
            st.metric("Concluídas", completed, delta=f"{completed}/{total_tasks}")
        
        with col3:
            pending = len(df[df['status'] == 'pending'])
            st.metric("Pendentes", pending)
        
        with col4:
            if total_tasks > 0:
                completion_rate = (completed / total_tasks) * 100
                st.metric("Taxa de Conclusão", f"{completion_rate:.1f}%")
        
        # Gráfico de tarefas por status
        st.subheader("📈 Distribuição de Tarefas")
        status_counts = df['status'].value_counts()
        fig_status = px.pie(values=status_counts.values, names=status_counts.index, 
                            title="Status das Tarefas",
                            color_discrete_map={'completed': '#00d26a', 'pending': '#ffa600', 'cancelled': '#ff4444'})
        st.plotly_chart(fig_status, use_container_width=True)
        
        # Análise de produtividade por hora do dia
        st.subheader("⏰ Produtividade por Hora do Dia")
        completed_df = df[df['status'] == 'completed'].copy()
        if not completed_df.empty:
            completed_df['hour'] = completed_df['completed_at'].dt.hour
            hourly_completion = completed_df.groupby('hour').size().reset_index(name='count')
            
            fig_hourly = px.bar(hourly_completion, x='hour', y='count',
                               title="Tarefas Concluídas por Hora",
                               labels={'hour': 'Hora do Dia', 'count': 'Tarefas Concluídas'},
                               color_discrete_sequence=['#00d26a'])
            fig_hourly.update_xaxis(tickmode='linear', tick0=0, dtick=1)
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Análise por dia da semana
        st.subheader("📅 Produtividade por Dia da Semana")
        df['day_of_week'] = df['task_date'].dt.dayofweek
        df['day_name'] = df['task_date'].dt.day_name()
        
        daily_stats = df.groupby(['day_name', 'status']).size().reset_index(name='count')
        fig_weekly = px.bar(daily_stats, x='day_name', y='count', color='status',
                           title="Tarefas por Dia da Semana",
                           color_discrete_map={'completed': '#00d26a', 'pending': '#ffa600', 'cancelled': '#ff4444'})
        st.plotly_chart(fig_weekly, use_container_width=True)
        
        # Gráfico de tarefas ao longo do tempo
        st.subheader("📅 Evolução Temporal")
        daily_tasks = df.groupby(['task_date', 'status']).size().reset_index(name='count')
        fig_timeline = px.line(daily_tasks, x='task_date', y='count', color='status',
                              title="Tarefas ao Longo do Tempo",
                              color_discrete_map={'completed': '#00d26a', 'pending': '#ffa600', 'cancelled': '#ff4444'})
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Análise de motivos de cancelamento
        st.subheader("❌ Principais Motivos de Cancelamento")
        cancelled_df = df[df['status'] == 'cancelled']
        if not cancelled_df.empty and 'cancellation_reason' in cancelled_df.columns:
            reasons = cancelled_df['cancellation_reason'].value_counts().head(5)
            if not reasons.empty:
                fig_reasons = px.bar(x=reasons.values, y=reasons.index, orientation='h',
                                    title="Top 5 Motivos de Cancelamento",
                                    labels={'x': 'Quantidade', 'y': 'Motivo'},
                                    color_discrete_sequence=['#ff4444'])
                st.plotly_chart(fig_reasons, use_container_width=True)
        
        # Tabela de tarefas recentes
        st.subheader("📋 Tarefas Recentes")
        display_df = df[['task_date', 'task_description', 'status', 'cancellation_reason']].sort_values('task_date', ascending=False).head(20)
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("📝 Nenhuma tarefa encontrada no período selecionado.")
        st.write("Comece adicionando tarefas através do bot no Telegram!")

except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.info("Verifique se as credenciais do Supabase estão corretas nos Secrets.")
