from database import TaskDatabase
from datetime import datetime, timedelta, date, time
import pandas as pd
import numpy as np
from typing import Dict

class ProductivityAnalyzer:
    def __init__(self):
        self.db = TaskDatabase()
    
    def analyze_best_completion_hours(self, user_id: int, days_back: int = 30) -> Dict:
        """Analisa os melhores horários de conclusão de tarefas"""
        start_date = date.today() - timedelta(days=days_back)
        tasks = self.db.get_tasks_for_dashboard(user_id, start_date)
        
        df = pd.DataFrame(tasks)
        if df.empty:
            return {"best_hour": 8, "worst_hour": 18}
        
        completed = df[df['status'] == 'completed'].copy()
        if completed.empty:
            return {"best_hour": 8, "worst_hour": 18}
        
        completed['completed_at'] = pd.to_datetime(completed['completed_at'])
        completed['hour'] = completed['completed_at'].dt.hour
        
        hourly_counts = completed.groupby('hour').size()
        
        if len(hourly_counts) == 0:
            return {"best_hour": 8, "worst_hour": 18}
        
        best_hour = int(hourly_counts.idxmax())
        worst_hour = int(hourly_counts.idxmin())
        
        return {
            "best_hour": best_hour,
            "worst_hour": worst_hour,
            "hourly_distribution": hourly_counts.to_dict()
        }
    
    def analyze_best_days(self, user_id: int, days_back: int = 30) -> Dict:
        """Analisa os melhores dias da semana"""
        start_date = date.today() - timedelta(days=days_back)
        tasks = self.db.get_tasks_for_dashboard(user_id, start_date)
        
        df = pd.DataFrame(tasks)
        if df.empty:
            return {"best_day": 1, "worst_day": 5}
        
        df['task_date'] = pd.to_datetime(df['task_date'])
        df['day_of_week'] = df['task_date'].dt.dayofweek
        
        completion_by_day = df.groupby('day_of_week').apply(
            lambda x: (x['status'] == 'completed').sum() / len(x) if len(x) > 0 else 0
        )
        
        if len(completion_by_day) == 0:
            return {"best_day": 1, "worst_day": 5}
        
        best_day = int(completion_by_day.idxmax())
        worst_day = int(completion_by_day.idxmin())
        
        return {
            "best_day": best_day,
            "worst_day": worst_day,
            "daily_completion_rates": completion_by_day.to_dict()
        }
    
    def calculate_productivity_score(self, user_id: int, days_back: int = 7) -> float:
        """Calcula score de produtividade (0-100)"""
        start_date = date.today() - timedelta(days=days_back)
        tasks = self.db.get_tasks_for_dashboard(user_id, start_date)
        
        df = pd.DataFrame(tasks)
        if df.empty:
            return 50.0
        
        completion_rate = (df['status'] == 'completed').sum() / len(df)
        cancellation_rate = (df['status'] == 'cancelled').sum() / len(df)
        
        df['task_date'] = pd.to_datetime(df['task_date'])
        unique_days = df['task_date'].dt.date.nunique()
        consistency_bonus = min(unique_days / days_back, 1.0) * 20
        
        base_score = completion_rate * 60
        penalty = cancellation_rate * 20
        score = min(base_score - penalty + consistency_bonus, 100)
        
        return round(score, 2)
    
    def calculate_optimal_reminder_time(self, user_id: int) -> time:
        """Calcula horário ótimo para lembrete baseado no pior horário"""
        hour_analysis = self.analyze_best_completion_hours(user_id)
        worst_hour = hour_analysis['worst_hour']
        
        optimal_hour = max(worst_hour - 2, 14)
        optimal_hour = min(optimal_hour, 20)
        
        return time(hour=optimal_hour, minute=0)
    
    def analyze_cancellation_patterns(self, user_id: int, days_back: int = 30) -> Dict:
        """Analisa padrões de cancelamento"""
        start_date = date.today() - timedelta(days=days_back)
        tasks = self.db.get_tasks_for_dashboard(user_id, start_date)
        
        df = pd.DataFrame(tasks)
        cancelled = df[df['status'] == 'cancelled']
        
        if cancelled.empty:
            return {"most_common_reason": "Nenhum cancelamento"}
        
        reason_counts = cancelled['cancellation_reason'].value_counts()
        most_common = reason_counts.index[0] if len(reason_counts) > 0 else "N/A"
        
        return {
            "most_common_reason": most_common,
            "total_cancellations": len(cancelled),
            "cancellation_rate": len(cancelled) / len(df)
        }
    
    def run_full_analysis(self, user_id: int) -> Dict:
        """Executa análise completa e salva no banco"""
        hours = self.analyze_best_completion_hours(user_id)
        days = self.analyze_best_days(user_id)
        score = self.calculate_productivity_score(user_id)
        optimal_time = self.calculate_optimal_reminder_time(user_id)
        cancellations = self.analyze_cancellation_patterns(user_id)
        
        start_date = date.today() - timedelta(days=30)
        tasks = self.db.get_tasks_for_dashboard(user_id, start_date)
        df = pd.DataFrame(tasks)
        
        avg_completion = 0.0
        if not df.empty:
            avg_completion = (df['status'] == 'completed').sum() / len(df) * 100
        
        analytics = {
            "best_completion_hour": hours['best_hour'],
            "worst_completion_hour": hours['worst_hour'],
            "best_day_of_week": days['best_day'],
            "worst_day_of_week": days['worst_day'],
            "avg_completion_rate": round(avg_completion, 2),
            "most_common_cancellation_reason": cancellations['most_common_reason'],
            "optimal_reminder_time": optimal_time.isoformat(),
            "productivity_score": score
        }
        
        self.db.save_behavior_analytics(user_id, analytics)
        
        morning_time = time(hour=8, minute=0)
        self.db.update_notification_settings(user_id, morning_time, optimal_time)
        
        return analytics
