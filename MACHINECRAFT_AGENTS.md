"""
VP Agent Factory for Machinecraft Departments
Creates specialized VP instances for different use cases
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class Department(str, Enum):
    """Machinecraft departments"""
    FINANCE = "finance"
    SALES = "sales" 
    MARKETING = "marketing"
    ENGINEERING = "engineering"
    RECRUITMENT = "recruitment"
    HR = "hr"
    MAINTENANCE = "maintenance"
    SUPPLY_CHAIN = "supply"
    EXPORT = "export"

@dataclass
class AgentConfig:
    """Configuration for specialized VP agents"""
    department: Department
    namespace: str
    display_name: str
    description: str
    document_types: list[str]
    specialized_prompts: dict[str, str]
    integrations: list[str]
    color_scheme: dict[str, str]
    
class VPAgentFactory:
    """Factory for creating specialized VP agents"""
    
    def __init__(self):
        self.agent_configs = self._load_agent_configs()
    
    def create_agent(self, department: Department) -> 'VPAgent':
        """Create a specialized VP agent for a department"""
        config = self.agent_configs.get(department)
        if not config:
            raise ValueError(f"No configuration found for department: {department}")
        
        return VPAgent(config)
    
    def _load_agent_configs(self) -> Dict[Department, AgentConfig]:
        """Load configurations for all departments"""
        return {
            Department.FINANCE: AgentConfig(
                department=Department.FINANCE,
                namespace="machinecraft_finance",
                display_name="VP-Finance",
                description="Financial analysis and reporting specialist",
                document_types=["xlsx", "pdf", "csv", "financial_statements"],
                specialized_prompts={
                    "system": "You are VP-Finance, Machinecraft's financial analysis expert. Analyze financial data with precision and provide actionable insights for business decisions.",
                    "context": "Focus on financial metrics, cost analysis, budget variance, and profitability insights."
                },
                integrations=["erp", "accounting", "banking"],
                color_scheme={"primary": "#059669", "secondary": "#065F46"}  # Green for money
            ),
            
            Department.SALES: AgentConfig(
                department=Department.SALES,
                namespace="machinecraft_sales", 
                display_name="VP-Sales",
                description="Sales pipeline and customer intelligence specialist",
                document_types=["crm_data", "proposals", "contracts", "customer_comms"],
                specialized_prompts={
                    "system": "You are VP-Sales, Machinecraft's sales intelligence expert. Analyze sales data to identify opportunities and optimize the sales process.",
                    "context": "Focus on lead qualification, pipeline health, customer success patterns, and competitive positioning."
                },
                integrations=["crm", "email", "calendar"],
                color_scheme={"primary": "#DC2626", "secondary": "#991B1B"}  # Red for urgency
            ),
            
            Department.MARKETING: AgentConfig(
                department=Department.MARKETING,
                namespace="machinecraft_marketing",
                display_name="VP-Marketing", 
                description="Marketing campaign and brand intelligence specialist",
                document_types=["analytics", "campaigns", "competitor_intel", "social_media"],
                specialized_prompts={
                    "system": "You are VP-Marketing, Machinecraft's marketing intelligence expert. Analyze marketing data to optimize campaigns and brand positioning.",
                    "context": "Focus on campaign performance, brand perception, competitive analysis, and market trends."
                },
                integrations=["analytics", "social_media", "advertising"],
                color_scheme={"primary": "#7C3AED", "secondary": "#5B21B6"}  # Purple for creativity
            ),
            
            Department.ENGINEERING: AgentConfig(
                department=Department.ENGINEERING,
                namespace="machinecraft_engineering",
                display_name="VP-Engineering",
                description="Technical documentation and quality intelligence specialist", 
                document_types=["cad", "specs", "quality_reports", "manuals"],
                specialized_prompts={
                    "system": "You are VP-Engineering, Machinecraft's technical intelligence expert. Analyze engineering data to improve designs and processes.",
                    "context": "Focus on technical specifications, quality metrics, design improvements, and manufacturing optimization."
                },
                integrations=["cad", "plm", "quality_systems"],
                color_scheme={"primary": "#0891B2", "secondary": "#0E7490"}  # Blue for technical
            ),
            
            Department.RECRUITMENT: AgentConfig(
                department=Department.RECRUITMENT,
                namespace="machinecraft_recruitment",
                display_name="VP-Recruitment",
                description="Talent acquisition and candidate intelligence specialist",
                document_types=["resumes", "linkedin", "interviews", "assessments"],
                specialized_prompts={
                    "system": "You are VP-Recruitment, Machinecraft's talent intelligence expert. Analyze candidate data to optimize hiring decisions.",
                    "context": "Focus on skill matching, candidate quality, hiring pipeline efficiency, and talent market trends."
                },
                integrations=["ats", "linkedin", "assessment_tools"],
                color_scheme={"primary": "#EA580C", "secondary": "#C2410C"}  # Orange for energy
            ),
            
            Department.HR: AgentConfig(
                department=Department.HR,
                namespace="machinecraft_hr",
                display_name="VP-HR",
                description="Employee engagement and organizational intelligence specialist",
                document_types=["performance", "surveys", "policies", "training"],
                specialized_prompts={
                    "system": "You are VP-HR, Machinecraft's people intelligence expert. Analyze HR data to improve employee experience and organizational effectiveness.",
                    "context": "Focus on employee engagement, performance patterns, training effectiveness, and organizational health."
                },
                integrations=["hris", "survey_tools", "training_platforms"],
                color_scheme={"primary": "#DB2777", "secondary": "#BE185D"}  # Pink for people
            )
        }

class VPAgent:
    """Specialized VP agent for a specific department"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.vp_core = self._initialize_vp_core()
        self.specialized_features = self._load_specializations()
    
    def _initialize_vp_core(self):
        """Initialize core VP functionality"""
        from core.config import settings
        
        # Override namespace for department
        settings.pinecone_namespace = self.config.namespace
        
        # Initialize core VP components
        from apps.cli import VPCore  # Hypothetical core class
        return VPCore(
            department=self.config.department,
            namespace=self.config.namespace
        )
    
    def _load_specializations(self):
        """Load department-specific features"""
        return {
            "prompts": self.config.specialized_prompts,
            "document_filters": self.config.document_types,
            "integrations": self.config.integrations
        }
    
    def ask(self, question: str, **kwargs) -> dict:
        """Ask question with department specialization"""
        # Add department context to the query
        department_context = f"Department: {self.config.department.value}\n"
        department_context += f"Focus: {self.config.description}\n"
        
        # Use specialized system prompt
        system_prompt = self.config.specialized_prompts.get("system", "")
        
        # Call core VP with specialization
        return self.vp_core.ask(
            question=question,
            system_prompt=system_prompt,
            context=department_context,
            **kwargs
        )
    
    def ingest_department_docs(self, path: str) -> dict:
        """Ingest documents with department-specific processing"""
        # Filter documents by department relevance
        relevant_docs = self._filter_department_documents(path)
        
        # Process with department context
        return self.vp_core.ingest(
            documents=relevant_docs,
            metadata={"department": self.config.department.value}
        )
    
    def _filter_department_documents(self, path: str) -> list:
        """Filter documents relevant to this department"""
        # Implementation would filter based on:
        # - File types (config.document_types)
        # - File names (department keywords)
        # - Content analysis (department relevance)
        pass

# Factory instance
vp_factory = VPAgentFactory()

# Usage examples
def create_finance_agent():
    return vp_factory.create_agent(Department.FINANCE)

def create_sales_agent():
    return vp_factory.create_agent(Department.SALES)
