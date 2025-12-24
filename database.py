from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime, date, time
from typing import List, Dict, Optional

class TaskDatabase:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def add_task(self, user_id: int, task_description: str, task_date: date) -> Dict:
        """Adiciona uma nova tarefa"""
        data = {
            "user_id": user_id,
            "task_description": task_description,
            "task_date": task_date.isoformat(),
            "status": "pending"
        }
        result = self.client.table("tasks").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_daily_task_count(self, user_id: int, task_date: date) -> int:
        """Retorna quantidade de tarefas do dia"""
        result = self.client.table("tasks").select("id").eq("user_id", user_id).eq("task_date", task_date.isoformat()).eq("status", "pending").execute()
        return len(result.data)
    
    def complete_task(self, task_id: str) -> Dict:
        """Marca tarefa como concluída"""
        data = {
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        result = self.client.table("tasks").update(data).eq("id", task_id).execute()
        return result.data[0] if result.data else None
    
    def cancel_task(self, task_id: str, reason: str) -> Dict:
        """Cancela tarefa com justificativa"""
        data = {
            "status": "cancelled",
            "cancellation_reason": reason
        }
        result = self.client.table("tasks").update(data).eq("id", task_id).execute()
        return result.data[0] if result.data else None
    
    def get_pending_tasks(self, user_id: int, task_date: date) -> List[Dict]:
        """Busca tarefas pendentes do dia"""
        result = self.client.table("tasks").select("*").eq("user_id", user_id).eq("task_date", task_date.isoformat()).eq("status", "pending").execute()
        return result.data
    
    def get_tasks_for_dashboard(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict]:
        """Busca tarefas para dashboard"""
        query = self.client.table("tasks").select("*").eq("user_id", user_id)
        
        if start_date:
            query = query.gte("task_date", start_date.isoformat())
        if end_date:
            query = query.lte("task_date", end_date.isoformat())
        
        result = query.order("task_date", desc=True).execute()
        return result.data
    
    def get_user_notification_settings(self, user_id: int) -> Dict:
        """Busca configurações de notificação do usuário"""
        result = self.client.table("notification_settings").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None
    
    def update_notification_settings(self, user_id: int, morning_time: time, reminder_time: time) -> Dict:
        """Atualiza horários de notificação"""
        data = {
            "user_id": user_id,
            "morning_notification_time": morning_time.isoformat(),
            "reminder_notification_time": reminder_time.isoformat(),
            "last_adjusted_at": datetime.now().isoformat()
        }
        result = self.client.table("notification_settings").upsert(data).execute()
        return result.data[0] if result.data else None
    
    def save_behavior_analytics(self, user_id: int, analytics: Dict) -> Dict:
        """Salva análise de comportamento do usuário"""
        data = {
            "user_id": user_id,
            "analysis_date": date.today().isoformat(),
            **analytics
        }
        result = self.client.table("user_behavior_analytics").upsert(data).execute()
        return result.data[0] if result.data else None
    
    def get_latest_analytics(self, user_id: int) -> Dict:
        """Busca última análise de comportamento"""
        result = self.client.table("user_behavior_analytics").select("*").eq("user_id", user_id).order("analysis_date", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
