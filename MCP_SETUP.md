# 🔨 VP MCP Setup Guide

## 🎯 **VP as MCP Server for Machinecraft**

VP (Vectorpenter) is now designed as a **Model Context Protocol (MCP) server** that provides document intelligence capabilities to specialized department agents.

---

## 🏗️ **Architecture Overview**

```
                    🔨 VP MCP ECOSYSTEM 🔨
                                      
    🖥️ VP Core MCP Server              📱 Department Agents (MCP Clients)
    (Always Running)                   (Connect as Needed)
           │                                    │
           │ ◄─────── MCP Protocol ─────────► │
           │                                    │
    ┌─────────────────┐                ┌─────────────────┐
    │ 🔨 VP Core      │                │ 🎯 VP-Sales     │
    │                 │                │ 🏢 VP-Finance   │
    │ • Search        │                │ 📈 VP-Marketing │
    │ • Ingest        │                │ 🔧 VP-Engineering│
    │ • Translate     │                │ 👥 VP-HR        │
    │ • OCR           │                │ 📦 VP-Supply    │
    │ • Web Capture   │                │                 │
    │ • Generate      │                │ (Each specialized│
    └─────────────────┘                │  for department) │
                                       └─────────────────┘
```

---

## 🚀 **Quick Start**

### **Step 1: Install VP with MCP Support**

```bash
# Install VP with MCP capabilities
pip install -e .[gcp]  # Include Google Cloud features
```

### **Step 2: Start VP Core MCP Server**

```bash
# Terminal 1: Start VP Core (runs continuously)
vp-server

# Or manually:
python -m mcp.vp_server
```

### **Step 3: Use Department Agents**

```bash
# Terminal 2: Use VP-Sales agent
vp-sales

# Or manually:
python -m agents.vp_sales
```

---

## 🔨 **VP Core MCP Tools**

VP provides these tools via MCP for any client to use:

### **🔍 Document Intelligence**
```python
# Search across all Machinecraft documents
search_documents(
    query="Q3 financial results",
    department="finance",  # Optional filter
    k=12,
    hybrid=True,
    rerank=True
)
```

### **📥 Document Processing**
```python
# Ingest new documents with department tagging
ingest_documents(
    path="./new_contracts/",
    department="sales",
    force_reindex=False
)
```

### **🌍 Language Services**
```python
# Auto-translate any content
translate_content(
    text="Hola, necesitamos una cotización",
    target_language="en"
)
```

### **📸 Web Intelligence**
```python
# Capture competitor websites
capture_webpage(
    url="https://competitor.com/pricing",
    format="png",
    device="desktop"
)
```

### **🔍 OCR Services**
```python
# Extract text from images/PDFs
ocr_document(
    file_path="./scanned_contract.pdf",
    use_docai=True
)
```

### **🧠 Answer Generation**
```python
# Generate department-specific answers
generate_answer(
    question="What's our pricing strategy?",
    context="Sales team analysis",
    department_focus="sales strategy"
)
```

### **📊 Analytics**
```python
# Get knowledge base statistics
get_document_stats(
    department="sales",
    include_details=True
)
```

### **🏥 Health Monitoring**
```python
# Check VP's health and capabilities
health_check(detailed=True)
```

---

## 🎯 **Department Agent Examples**

### **💰 VP-Finance Usage**
```python
from agents.vp_finance import VPFinanceAgent

vp_finance = VPFinanceAgent()
await vp_finance.connect_to_vp_core()

# Analyze cost overruns
cost_analysis = await vp_finance.analyze_costs(
    period="Q3 2025",
    focus="production overruns"
)

# Budget variance analysis
budget_report = await vp_finance.budget_variance_analysis()
```

### **🎯 VP-Sales Usage**
```python
from agents.vp_sales import VPSalesAgent, SalesLead

vp_sales = VPSalesAgent()
await vp_sales.connect_to_vp_core()

# Analyze a sales lead
lead = SalesLead(
    company="ACME Manufacturing",
    contact_person="John Smith", 
    email="john@acme.com",
    industry="automotive"
)

lead_analysis = await vp_sales.analyze_lead(lead)
print(f"Lead Quality: {lead_analysis['recommendations']}")
```

### **📈 VP-Marketing Usage**
```python
from agents.vp_marketing import VPMarketingAgent

vp_marketing = VPMarketingAgent()
await vp_marketing.connect_to_vp_core()

# Campaign performance analysis
campaign_analysis = await vp_marketing.analyze_campaign(
    campaign_id="K-Show-2025",
    metrics=["leads", "conversions", "roi"]
)
```

---

## 🔧 **Development Setup**

### **For VP Core Development**
```bash
# Start VP Core in development mode
export LOG_LEVEL=DEBUG
python -m mcp.vp_server

# Test VP Core tools
python -c "
import asyncio
from mcp.client.stdio import stdio_client
from mcp.client import StdioServerParameters

async def test_vp():
    params = StdioServerParameters(
        command='python',
        args=['-m', 'mcp.vp_server']
    )
    
    async with stdio_client(params) as client:
        tools = await client.list_tools()
        print(f'VP provides {len(tools.tools)} tools')
        
        # Test search
        result = await client.call_tool(
            'search_documents',
            {'query': 'test', 'k': 5}
        )
        print('Search test successful')

asyncio.run(test_vp())
"
```

### **For Department Agent Development**
```bash
# Create new department agent
cp agents/vp_sales.py agents/vp_finance.py
# Customize for finance-specific logic

# Test the new agent
python -m agents.vp_finance
```

---

## 🌐 **MCP Client Integration**

### **External Tools Can Connect to VP**

Any MCP-compatible client can connect to VP Core:

```python
# Claude Desktop, Cursor, or any MCP client
{
  "mcpServers": {
    "vp-core": {
      "command": "python",
      "args": ["-m", "mcp.vp_server"],
      "cwd": "/path/to/vectorpenter"
    }
  }
}
```

### **VP Tools Available to All MCP Clients**
- **search_documents**: Search Machinecraft knowledge base
- **ingest_documents**: Add new documents to VP's memory
- **translate_content**: Multi-language translation
- **capture_webpage**: Screenshot and OCR web content
- **ocr_document**: Extract text from images/PDFs
- **generate_answer**: AI-powered responses with citations
- **get_document_stats**: Knowledge base analytics
- **health_check**: System status and capabilities

---

## 🎯 **Production Deployment**

### **Single VP Core, Multiple Agents**

```bash
# Production setup
docker-compose up -d  # Start supporting services

# Start VP Core MCP Server (runs continuously)
vp-server &

# Department agents connect as needed
vp-sales &      # Sales intelligence
vp-finance &    # Financial analysis
vp-marketing &  # Marketing insights
```

### **Scaling Strategy**
- **One VP Core** handles all document intelligence
- **Unlimited agents** can connect via MCP
- **Department isolation** via Pinecone namespaces
- **Shared capabilities** with specialized logic

---

## 🏆 **Business Value**

### **🔨 VP as Universal Foundation**
- **Unified Knowledge**: All departments share Machinecraft's complete document intelligence
- **Consistent Quality**: Same high-quality search, translation, and analysis across all agents
- **Cost Efficient**: One VP core serves unlimited specialized agents
- **Easy Maintenance**: Update VP core, all agents benefit immediately

### **🎭 Department Specialization**
- **VP-Sales**: CRM integration, lead scoring, proposal optimization
- **VP-Finance**: ERP integration, cost analysis, budget tracking
- **VP-Marketing**: Analytics integration, campaign performance
- **VP-Engineering**: CAD integration, quality analysis, design optimization

**VP is now the perfect MCP server for Machinecraft's AI transformation!** 🔨✨

Users can connect any MCP client to VP and get access to all of Vectorpenter's document intelligence capabilities!
