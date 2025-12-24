import google.generativeai as genai
from config import GEMINI_API_KEY
import json
from typing import List

class TaskProcessor:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def extract_tasks(self, user_message: str) -> List[str]:
        """Extrai tarefas da mensagem do usuário usando Gemini"""
        
        prompt = f"""
Você é um assistente que identifica tarefas em mensagens de texto.

Analise a seguinte mensagem e extraia APENAS as tarefas mencionadas.
Retorne as tarefas como uma lista JSON.
Cada tarefa deve ser clara e objetiva.
Máximo de 5 tarefas.

Mensagem: "{user_message}"

Retorne APENAS um JSON no formato:
{{"tasks": ["tarefa 1", "tarefa 2", ...]}}

Não adicione nenhum texto antes ou depois do JSON.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            result = json.loads(response_text)
            tasks = result.get("tasks", [])
            return tasks[:5]
        except Exception as e:
            print(f"Erro ao processar com Gemini: {e}")
            return []
    
    def suggest_task_optimization(self, user_analytics: dict) -> str:
        """Sugere otimizações baseadas em analytics"""
        prompt = f"""
Com base nos seguintes dados de produtividade do usuário, forneça 3 sugestões práticas e diretas:

Melhor horário: {user_analytics.get('best_completion_hour')}h
Pior horário: {user_analytics.get('worst_completion_hour')}h
Melhor dia: {user_analytics.get('best_day_of_week')}
Score de produtividade: {user_analytics.get('productivity_score')}/100
Taxa de conclusão: {user_analytics.get('avg_completion_rate')}%

Forneça 3 sugestões numeradas, cada uma com no máximo 25 palavras.
Seja direto e prático.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "Continue mantendo sua consistência nas tarefas diárias."
