# 🔨 VP Template Usage Guide

## 🎯 **Using VP as a Template for Department Agents**

VP (Vectorpenter) is designed as a **template library** that can be copied and customized for different Machinecraft departments.

## 🏗️ **Template Architecture**

```
📚 VP Template (vectorpenter)
├── 🔨 Core RAG Engine
├── 🔍 Hybrid Search
├── 🌐 Translation & OCR
├── 📸 Web Capture
├── ⚙️ Configurable Framework
└── 🎯 Department Customization Points
```

## 🚀 **Quick Start: Creating a Department Agent**

### **Step 1: Copy VP Template**
```bash
# Copy the entire VP repository
git clone https://github.com/doshirush1901/Vectorpenter.git vp-sales
cd vp-sales
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Customize for Your Department**
```python
# Create your department-specific configuration
from core.vp_core import VPCore
from core.config import VPConfig

class VPSales(VPCore):
    def __init__(self):
        config = VPConfig(
            namespace="machinecraft_sales",
            department="sales",
            specialized_prompts=self.get_sales_prompts(),
            custom_filters=self.get_sales_filters()
        )
        super().__init__(config)
    
    def get_sales_prompts(self):
        return {
            "lead_analysis": "Analyze this lead for sales potential...",
            "proposal_review": "Review this proposal for accuracy...",
            "competitor_intel": "Extract competitive intelligence..."
        }
    
    def get_sales_filters(self):
        return {
            "document_types": ["proposals", "leads", "contracts", "rfp"],
            "priority_keywords": ["sales", "revenue", "customer", "deal"]
        }
    
    # Add sales-specific methods
    def analyze_lead(self, lead_data):
        """Analyze sales lead potential"""
        return self.query_documents(
            query=f"Analyze sales potential: {lead_data}",
            filters={"type": "leads"}
        )
    
    def score_proposal(self, proposal_text):
        """Score proposal win probability"""
        return self.query_documents(
            query=f"Score this proposal: {proposal_text}",
            filters={"type": "proposals"}
        )
```

### **Step 4: Add Department-Specific Integrations**
```python
# Add CRM integration for sales
class VPSales(VPCore):
    def __init__(self):
        super().__init__()
        self.crm = self.setup_crm_integration()
    
    def setup_crm_integration(self):
        # Connect to Salesforce, HubSpot, etc.
        pass
    
    def sync_with_crm(self, lead_data):
        # Sync analysis results with CRM
        pass
```

### **Step 5: Deploy as Standalone Service**
```bash
# Each department agent runs independently
python apps/cli.py --namespace machinecraft_sales
```

## 🎯 **Department Customization Examples**

### **💰 VP-Finance**
```python
class VPFinance(VPCore):
    def __init__(self):
        config = VPConfig(
            namespace="machinecraft_finance",
            specialized_prompts={
                "cost_analysis": "Analyze costs and profitability...",
                "budget_review": "Review budget allocations..."
            }
        )
        super().__init__(config)
    
    def analyze_costs(self, cost_data):
        """Analyze cost structures"""
        pass
    
    def budget_variance(self, budget_data):
        """Calculate budget variances"""
        pass
```

### **🔧 VP-Engineering**
```python
class VPEngineering(VPCore):
    def __init__(self):
        config = VPConfig(
            namespace="machinecraft_engineering",
            specialized_prompts={
                "spec_analysis": "Analyze technical specifications...",
                "design_review": "Review engineering designs..."
            }
        )
        super().__init__(config)
    
    def analyze_specs(self, spec_document):
        """Analyze technical specifications"""
        pass
    
    def design_review(self, design_files):
        """Review engineering designs"""
        pass
```

## 🔧 **Configuration Options**

### **Namespace Isolation**
```python
# Each department gets isolated data
config = VPConfig(
    namespace="machinecraft_sales",  # Isolated Pinecone namespace
    index_name="vp-sales-index"     # Separate search index
)
```

### **Custom Prompts**
```python
# Department-specific AI behavior
specialized_prompts = {
    "default": "You are a sales intelligence assistant...",
    "lead_scoring": "Score this lead from 1-10 based on...",
    "proposal_analysis": "Analyze this proposal for..."
}
```

### **Document Filters**
```python
# Focus on relevant documents
custom_filters = {
    "document_types": ["leads", "proposals", "contracts"],
    "date_range": "last_6_months",
    "priority_keywords": ["sales", "revenue", "customer"]
}
```

## 🚀 **Benefits of Template Approach**

### ✅ **Simplicity**
- No complex server/client setup
- Standard Python deployment
- Familiar development patterns

### ✅ **Independence**
- Each department agent runs standalone
- No single point of failure
- Independent scaling and updates

### ✅ **Customization Freedom**
- Modify VP core as needed
- Add department-specific integrations
- Use different versions per department

### ✅ **Operational Ease**
- Standard monitoring and logging
- Simple debugging and testing
- Easy to deploy and maintain

## 📋 **Next Steps**

1. **Copy VP template** for your department
2. **Customize configuration** for your use case
3. **Add department-specific methods** and integrations
4. **Deploy as standalone service**
5. **Iterate and improve** based on department needs

## 🎯 **Perfect for Machinecraft**

This template approach gives each Machinecraft department:
- **Full control** over their AI agent
- **Easy customization** for specific workflows
- **Independent operation** without dependencies
- **Scalable architecture** that grows with needs

**VP Template = Maximum flexibility with minimum complexity!** 🔨✨
