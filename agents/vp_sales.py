"""
VP-Sales: Specialized sales intelligence agent for Machinecraft
Uses VP Core via MCP for document processing and search
"""

from __future__ import annotations
import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

from mcp.client import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@dataclass
class SalesLead:
    """Sales lead data structure"""
    company: str
    contact_person: str
    email: str
    phone: Optional[str] = None
    industry: str = "manufacturing"
    status: str = "prospect"
    notes: str = ""
    
@dataclass 
class SalesQuery:
    """Sales-specific query structure"""
    question: str
    context_type: str  # "lead", "proposal", "contract", "competitor"
    urgency: str = "normal"  # "low", "normal", "high", "critical"
    
class VPSalesAgent:
    """VP-Sales: Specialized sales intelligence agent"""
    
    def __init__(self):
        self.department = "sales"
        self.namespace = "machinecraft_sales"
        self.vp_session: Optional[ClientSession] = None
        
        # Sales-specific configuration
        self.sales_prompts = {
            "lead_analysis": """You are VP-Sales, Machinecraft's sales intelligence expert. 
            Analyze the provided information to assess lead quality and recommend next actions.
            Focus on: company size, budget indicators, decision timeline, pain points, and fit with Machinecraft's solutions.""",
            
            "proposal_review": """You are VP-Sales, reviewing proposal documents.
            Analyze for: competitive positioning, pricing strategy, technical requirements, and win probability.
            Provide actionable recommendations for improving proposal success.""",
            
            "competitor_analysis": """You are VP-Sales, analyzing competitive intelligence.
            Focus on: pricing comparison, feature gaps, market positioning, and competitive advantages.
            Provide strategic recommendations for sales positioning.""",
            
            "pipeline_analysis": """You are VP-Sales, analyzing sales pipeline data.
            Focus on: conversion rates, bottlenecks, opportunity quality, and forecast accuracy.
            Provide recommendations for pipeline optimization."""
        }
        
        # Sales-specific document filters
        self.sales_document_types = [
            "proposals", "contracts", "rfp", "rfq", "customer_emails", 
            "meeting_notes", "competitor_analysis", "pricing_sheets",
            "case_studies", "testimonials", "sales_presentations"
        ]
    
    async def connect_to_vp_core(self):
        """Connect to VP Core MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=["-m", "mcp.vp_server"]
            )
            
            self.vp_session = await stdio_client(server_params)
            logger.info("🔗 VP-Sales connected to VP Core")
            
        except Exception as e:
            logger.error(f"Failed to connect to VP Core: {e}")
            raise
    
    async def analyze_lead(self, lead_info: SalesLead, additional_context: str = "") -> Dict[str, Any]:
        """Analyze a sales lead using VP's intelligence"""
        if not self.vp_session:
            await self.connect_to_vp_core()
        
        # Search for relevant information about the company/industry
        search_query = f"{lead_info.company} {lead_info.industry} manufacturing"
        
        search_result = await self.vp_session.call_tool(
            "search_documents",
            {
                "query": search_query,
                "department": "sales",
                "k": 8,
                "hybrid": True,
                "rerank": True
            }
        )
        
        # Generate lead analysis
        analysis_context = f"""
        Lead Information:
        - Company: {lead_info.company}
        - Contact: {lead_info.contact_person} ({lead_info.email})
        - Industry: {lead_info.industry}
        - Status: {lead_info.status}
        - Notes: {lead_info.notes}
        
        Additional Context: {additional_context}
        """
        
        analysis_result = await self.vp_session.call_tool(
            "generate_answer",
            {
                "question": f"Analyze this sales lead: {lead_info.company}. What's the potential and recommended next steps?",
                "context": analysis_context,
                "department_focus": "sales lead qualification"
            }
        )
        
        return {
            "lead": lead_info,
            "search_results": search_result.content[0].text,
            "analysis": analysis_result.content[0].text,
            "recommendations": self._extract_recommendations(analysis_result.content[0].text)
        }
    
    async def analyze_proposal(self, proposal_path: str, rfp_requirements: str = "") -> Dict[str, Any]:
        """Analyze a sales proposal using VP's capabilities"""
        if not self.vp_session:
            await self.connect_to_vp_core()
        
        # First, ingest the proposal if it's new
        ingest_result = await self.vp_session.call_tool(
            "ingest_documents",
            {
                "path": proposal_path,
                "department": "sales"
            }
        )
        
        # Search for competitive and pricing information
        search_result = await self.vp_session.call_tool(
            "search_documents",
            {
                "query": "pricing strategy competitive positioning proposal",
                "department": "sales",
                "k": 10,
                "hybrid": True
            }
        )
        
        # Generate proposal analysis
        analysis_context = f"""
        RFP Requirements: {rfp_requirements}
        
        Analysis Focus:
        - Competitive positioning vs. other vendors
        - Pricing strategy and justification
        - Technical requirements coverage
        - Win probability assessment
        - Risk factors and mitigation
        """
        
        analysis_result = await self.vp_session.call_tool(
            "generate_answer",
            {
                "question": "Analyze this proposal for win probability and provide recommendations for improvement.",
                "context": analysis_context,
                "department_focus": "proposal review and optimization"
            }
        )
        
        return {
            "proposal_path": proposal_path,
            "ingestion_result": ingest_result.content[0].text,
            "competitive_intel": search_result.content[0].text,
            "analysis": analysis_result.content[0].text,
            "win_probability": self._assess_win_probability(analysis_result.content[0].text)
        }
    
    async def competitor_intelligence(self, competitor_name: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Gather competitive intelligence using VP's web capture and search"""
        if not self.vp_session:
            await self.connect_to_vp_core()
        
        # Capture competitor website if URL provided
        if competitor_name.startswith("http"):
            capture_result = await self.vp_session.call_tool(
                "capture_webpage",
                {
                    "url": competitor_name,
                    "format": "png",
                    "device": "desktop"
                }
            )
            
            # OCR the captured page
            if "saved_path" in capture_result.content[0].text:
                capture_data = json.loads(capture_result.content[0].text)
                ocr_result = await self.vp_session.call_tool(
                    "ocr_document",
                    {
                        "file_path": capture_data["saved_path"],
                        "use_docai": True
                    }
                )
        
        # Search existing competitive intelligence
        search_result = await self.vp_session.call_tool(
            "search_documents",
            {
                "query": f"{competitor_name} competitive analysis pricing features",
                "department": "sales",
                "k": 15,
                "hybrid": True,
                "rerank": True
            }
        )
        
        # Generate competitive analysis
        analysis_result = await self.vp_session.call_tool(
            "generate_answer",
            {
                "question": f"Provide competitive analysis for {competitor_name}. Compare their strengths, weaknesses, pricing, and positioning vs Machinecraft.",
                "department_focus": "competitive intelligence and sales strategy"
            }
        )
        
        return {
            "competitor": competitor_name,
            "analysis_type": analysis_type,
            "web_capture": capture_result.content[0].text if 'capture_result' in locals() else None,
            "ocr_data": ocr_result.content[0].text if 'ocr_result' in locals() else None,
            "existing_intel": search_result.content[0].text,
            "analysis": analysis_result.content[0].text,
            "strategic_recommendations": self._extract_strategic_recommendations(analysis_result.content[0].text)
        }
    
    async def pipeline_health_check(self) -> Dict[str, Any]:
        """Analyze sales pipeline health using VP's analytics"""
        if not self.vp_session:
            await self.connect_to_vp_core()
        
        # Search for pipeline and sales data
        pipeline_search = await self.vp_session.call_tool(
            "search_documents",
            {
                "query": "sales pipeline opportunities conversion rates forecast",
                "department": "sales",
                "k": 20,
                "hybrid": True
            }
        )
        
        # Generate pipeline analysis
        analysis_result = await self.vp_session.call_tool(
            "generate_answer",
            {
                "question": "Analyze the current sales pipeline health. Identify bottlenecks, conversion issues, and improvement opportunities.",
                "department_focus": "sales pipeline optimization"
            }
        )
        
        return {
            "pipeline_data": pipeline_search.content[0].text,
            "health_analysis": analysis_result.content[0].text,
            "recommendations": self._extract_pipeline_recommendations(analysis_result.content[0].text)
        }
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract actionable recommendations from analysis"""
        # Simple extraction - could be enhanced with NLP
        lines = analysis_text.split('\n')
        recommendations = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'action']):
                recommendations.append(line.strip())
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _assess_win_probability(self, analysis_text: str) -> str:
        """Assess win probability from analysis text"""
        text_lower = analysis_text.lower()
        
        if any(word in text_lower for word in ['high', 'strong', 'excellent', 'likely']):
            return "high"
        elif any(word in text_lower for word in ['medium', 'moderate', 'possible']):
            return "medium"
        elif any(word in text_lower for word in ['low', 'weak', 'unlikely', 'poor']):
            return "low"
        else:
            return "unknown"
    
    def _extract_strategic_recommendations(self, analysis_text: str) -> List[str]:
        """Extract strategic recommendations for competitive positioning"""
        lines = analysis_text.split('\n')
        strategic_recs = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['strategy', 'position', 'compete', 'advantage']):
                strategic_recs.append(line.strip())
        
        return strategic_recs[:3]  # Top 3 strategic recommendations
    
    def _extract_pipeline_recommendations(self, analysis_text: str) -> List[str]:
        """Extract pipeline improvement recommendations"""
        lines = analysis_text.split('\n')
        pipeline_recs = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['pipeline', 'conversion', 'process', 'improve']):
                pipeline_recs.append(line.strip())
        
        return pipeline_recs[:4]  # Top 4 pipeline recommendations

# Usage example
async def demo_vp_sales():
    """Demo VP-Sales capabilities"""
    vp_sales = VPSalesAgent()
    
    # Example lead analysis
    lead = SalesLead(
        company="ACME Manufacturing",
        contact_person="John Smith",
        email="john@acme.com",
        industry="automotive",
        notes="Interested in PF1 series, budget around $200K"
    )
    
    lead_analysis = await vp_sales.analyze_lead(lead)
    print("🎯 Lead Analysis:", lead_analysis["analysis"])
    
    # Example competitive intelligence
    competitor_intel = await vp_sales.competitor_intelligence("https://competitor.com")
    print("🔍 Competitive Intelligence:", competitor_intel["analysis"])
    
    # Pipeline health check
    pipeline_health = await vp_sales.pipeline_health_check()
    print("📊 Pipeline Health:", pipeline_health["health_analysis"])

if __name__ == "__main__":
    asyncio.run(demo_vp_sales())
