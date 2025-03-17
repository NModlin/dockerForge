"""
AI usage tracking module for DockerForge.

This module provides functionality to track AI provider usage and costs.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger

logger = get_logger("ai_usage_tracker")


class AIUsageTracker:
    """Tracks AI provider usage and costs."""
    
    def __init__(self):
        """Initialize the usage tracker."""
        # Get data directory from config
        data_dir = get_config("general.data_dir", "~/.dockerforge/data")
        self.db_path = os.path.expanduser(data_dir)
        os.makedirs(self.db_path, exist_ok=True)
        self.db_file = os.path.join(self.db_path, "ai_usage.db")
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Create usage table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                operation TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                cost_usd REAL NOT NULL
            )
            ''')
            
            # Create budget table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                provider TEXT NOT NULL,
                budget_usd REAL NOT NULL,
                UNIQUE(month, provider)
            )
            ''')
            
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    def record_usage(self, provider: str, model: str, operation: str, 
                    input_tokens: int, output_tokens: int, cost_usd: float):
        """
        Record usage data.
        
        Args:
            provider: Provider name
            model: Model name
            operation: Operation name (e.g., analyze, generate_fix)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_usd: Cost in USD
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO ai_usage 
            (timestamp, provider, model, operation, input_tokens, output_tokens, cost_usd)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, provider, model, operation, input_tokens, output_tokens, cost_usd))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Recorded usage: {provider}/{model} {operation} - ${cost_usd:.4f}")
        except sqlite3.Error as e:
            logger.error(f"Error recording usage: {str(e)}")
    
    def get_daily_usage(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get usage statistics for a specific day.
        
        Args:
            date: Date to get usage for (default: today)
            
        Returns:
            Dict[str, Any]: Usage statistics
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.date().isoformat()
        next_date_str = (date.date() + timedelta(days=1)).isoformat()
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT provider, model, 
                   SUM(input_tokens) as total_input_tokens,
                   SUM(output_tokens) as total_output_tokens,
                   SUM(cost_usd) as total_cost_usd
            FROM ai_usage
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY provider, model
            ''', (date_str, next_date_str))
            
            results = cursor.fetchall()
            conn.close()
            
            usage = {
                "date": date_str,
                "providers": {},
                "total_cost_usd": 0.0,
            }
            
            for row in results:
                provider, model, input_tokens, output_tokens, cost = row
                
                if provider not in usage["providers"]:
                    usage["providers"][provider] = {
                        "models": {},
                        "total_cost_usd": 0.0,
                    }
                
                usage["providers"][provider]["models"][model] = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost_usd": cost,
                }
                
                usage["providers"][provider]["total_cost_usd"] += cost
                usage["total_cost_usd"] += cost
            
            return usage
        except sqlite3.Error as e:
            logger.error(f"Error getting daily usage: {str(e)}")
            return {"date": date_str, "providers": {}, "total_cost_usd": 0.0, "error": str(e)}
    
    def get_monthly_usage(self, year: int, month: int) -> Dict[str, Any]:
        """
        Get usage statistics for a specific month.
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            Dict[str, Any]: Usage statistics
        """
        start_date = datetime(year, month, 1).date().isoformat()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date().isoformat()
        else:
            end_date = datetime(year, month + 1, 1).date().isoformat()
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT provider, model, 
                   SUM(input_tokens) as total_input_tokens,
                   SUM(output_tokens) as total_output_tokens,
                   SUM(cost_usd) as total_cost_usd
            FROM ai_usage
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY provider, model
            ''', (start_date, end_date))
            
            results = cursor.fetchall()
            
            # Get budget information
            month_str = f"{year}-{month:02d}"
            cursor.execute('''
            SELECT provider, budget_usd
            FROM ai_budget
            WHERE month = ?
            ''', (month_str,))
            
            budget_results = cursor.fetchall()
            conn.close()
            
            usage = {
                "year": year,
                "month": month,
                "providers": {},
                "total_cost_usd": 0.0,
                "budget": {},
                "total_budget_usd": 0.0,
            }
            
            for row in results:
                provider, model, input_tokens, output_tokens, cost = row
                
                if provider not in usage["providers"]:
                    usage["providers"][provider] = {
                        "models": {},
                        "total_cost_usd": 0.0,
                    }
                
                usage["providers"][provider]["models"][model] = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost_usd": cost,
                }
                
                usage["providers"][provider]["total_cost_usd"] += cost
                usage["total_cost_usd"] += cost
            
            # Add budget information
            for provider, budget in budget_results:
                usage["budget"][provider] = budget
                usage["total_budget_usd"] += budget
            
            return usage
        except sqlite3.Error as e:
            logger.error(f"Error getting monthly usage: {str(e)}")
            return {
                "year": year, 
                "month": month, 
                "providers": {}, 
                "total_cost_usd": 0.0,
                "budget": {},
                "total_budget_usd": 0.0,
                "error": str(e)
            }
    
    def set_monthly_budget(self, year: int, month: int, provider: str, budget_usd: float):
        """
        Set monthly budget for a provider.
        
        Args:
            year: Year
            month: Month (1-12)
            provider: Provider name
            budget_usd: Budget in USD
        """
        month_str = f"{year}-{month:02d}"
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO ai_budget (month, provider, budget_usd)
            VALUES (?, ?, ?)
            ''', (month_str, provider, budget_usd))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Set budget for {provider} for {month_str}: ${budget_usd:.2f}")
        except sqlite3.Error as e:
            logger.error(f"Error setting monthly budget: {str(e)}")
    
    def check_budget_status(self) -> Dict[str, Any]:
        """
        Check current month's budget status.
        
        Returns:
            Dict[str, Any]: Budget status
        """
        now = datetime.now()
        year = now.year
        month = now.month
        
        # Get monthly usage
        usage = self.get_monthly_usage(year, month)
        
        # Calculate budget status
        status = {
            "year": year,
            "month": month,
            "providers": {},
            "total_usage_usd": usage["total_cost_usd"],
            "total_budget_usd": usage["total_budget_usd"],
            "total_remaining_usd": usage["total_budget_usd"] - usage["total_cost_usd"],
            "total_percentage": 0.0,
        }
        
        if usage["total_budget_usd"] > 0:
            status["total_percentage"] = (usage["total_cost_usd"] / usage["total_budget_usd"]) * 100
        
        # Calculate provider-specific status
        for provider, provider_data in usage["providers"].items():
            provider_budget = usage["budget"].get(provider, 0.0)
            provider_usage = provider_data["total_cost_usd"]
            provider_remaining = provider_budget - provider_usage
            provider_percentage = 0.0
            
            if provider_budget > 0:
                provider_percentage = (provider_usage / provider_budget) * 100
            
            status["providers"][provider] = {
                "usage_usd": provider_usage,
                "budget_usd": provider_budget,
                "remaining_usd": provider_remaining,
                "percentage": provider_percentage,
            }
        
        return status
    
    def is_within_budget(self, provider: str, estimated_cost: float) -> bool:
        """
        Check if an estimated cost is within budget.
        
        Args:
            provider: Provider name
            estimated_cost: Estimated cost in USD
            
        Returns:
            bool: True if within budget
        """
        # Get daily and monthly limits from config
        daily_limit = get_config("ai.cost_management.max_daily_cost_usd", 10.0)
        monthly_limit = get_config("ai.cost_management.max_monthly_cost_usd", 50.0)
        
        # Get daily usage
        daily_usage = self.get_daily_usage()
        provider_daily_usage = 0.0
        if provider in daily_usage["providers"]:
            provider_daily_usage = daily_usage["providers"][provider]["total_cost_usd"]
        
        # Check if daily limit would be exceeded
        if provider_daily_usage + estimated_cost > daily_limit:
            logger.warning(
                f"Daily budget limit would be exceeded: "
                f"${provider_daily_usage:.2f} + ${estimated_cost:.2f} > ${daily_limit:.2f}"
            )
            return False
        
        # Get monthly usage
        now = datetime.now()
        monthly_usage = self.get_monthly_usage(now.year, now.month)
        provider_monthly_usage = 0.0
        if provider in monthly_usage["providers"]:
            provider_monthly_usage = monthly_usage["providers"][provider]["total_cost_usd"]
        
        # Check if monthly limit would be exceeded
        if provider_monthly_usage + estimated_cost > monthly_limit:
            logger.warning(
                f"Monthly budget limit would be exceeded: "
                f"${provider_monthly_usage:.2f} + ${estimated_cost:.2f} > ${monthly_limit:.2f}"
            )
            return False
        
        return True
    
    def get_usage_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive usage report.
        
        Returns:
            Dict[str, Any]: Usage report
        """
        now = datetime.now()
        
        # Get daily usage
        daily_usage = self.get_daily_usage()
        
        # Get monthly usage
        monthly_usage = self.get_monthly_usage(now.year, now.month)
        
        # Get budget status
        budget_status = self.check_budget_status()
        
        # Calculate daily average
        days_in_month = (
            datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
        ).replace(day=1) - datetime(now.year, now.month, 1).replace(day=1)
        days_passed = now.day
        days_remaining = days_in_month.days - days_passed + 1
        
        daily_average = 0.0
        if days_passed > 0:
            daily_average = monthly_usage["total_cost_usd"] / days_passed
        
        # Project monthly total
        projected_total = monthly_usage["total_cost_usd"] + (daily_average * days_remaining)
        
        # Calculate budget status
        budget_remaining = monthly_usage["total_budget_usd"] - monthly_usage["total_cost_usd"]
        budget_percentage = 0.0
        if monthly_usage["total_budget_usd"] > 0:
            budget_percentage = (monthly_usage["total_cost_usd"] / monthly_usage["total_budget_usd"]) * 100
        
        # Prepare report
        report = {
            "date": now.date().isoformat(),
            "daily_usage": daily_usage,
            "monthly_usage": monthly_usage,
            "budget_status": budget_status,
            "days_in_month": days_in_month.days,
            "days_passed": days_passed,
            "days_remaining": days_remaining,
            "daily_average_usd": daily_average,
            "projected_total_usd": projected_total,
            "budget_remaining_usd": budget_remaining,
            "budget_percentage": budget_percentage,
            "projected_percentage": 0.0,
        }
        
        if monthly_usage["total_budget_usd"] > 0:
            report["projected_percentage"] = (projected_total / monthly_usage["total_budget_usd"]) * 100
        
        return report
