# 🔨 Vectorpenter

```
                    ╭─────────────────────────────────────────╮
                    │              🔨 VP 🔨                   │
                    │        The Carpenter of Context         │
                    │                                         │
                    │  ⚡ Local-First • 🧠 AI-Powered         │
                    │  🔍 Hybrid Search • 🌍 Multi-Language   │
                    ╰─────────────────────────────────────────╯
```

<div align="center">

**🔨 Turn your file chaos into instant answers 🔨**

*Meet VP - Your AI Document Carpenter!*

*Transforms any document into searchable knowledge with precision and care*

[![GitHub stars](https://img.shields.io/github/stars/doshirush1901/Vectorpenter?style=social)](https://github.com/doshirush1901/Vectorpenter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

</div>

---

## 🎨 **What is Vectorpenter?**

```
    📚 Your Documents          🔨 VP's Workshop          🤖 Organized Knowledge
         ↓                           ↓                        ↓
   ┌─────────────┐            ┌─────────────┐         ┌─────────────┐
   │  📄 PDFs    │   ────→    │  🧠 Smart   │  ────→  │ 💬 Natural  │
   │  📊 Excel   │            │  Processing │         │   Language  │
   │  🖼️ Images  │            │             │         │   Answers   │
   │  🌐 Websites│            │  🔨 VP's    │         │             │
   └─────────────┘            │   Magic     │         └─────────────┘
        Drop files             └─────────────┘           Ask questions
```

**VP** is your **local AI carpenter** who transforms scattered documents into an organized, searchable knowledge base. Like a master craftsman, VP knows exactly which tool to use for each task - local processing for privacy and speed, cloud services when they add real value.

---

# ℹ️ About

Vectorpenter helps you turn your everyday files — PDFs, Excel sheets, reports, contracts — into a **searchable knowledge base** you can ask questions in plain language.

Instead of opening 50 files and running Ctrl+F, you just ask and get the answer (with source).

---

## 🏭 Use Cases

### 👥 Recruitment

* Store CVs, test reports, and interview notes.
* Ask: *"Who has experience with SolidWorks and CNC programming?"*
* Find the right candidate instantly.

### 💼 Sales

* Keep all quotes, proposals, and client emails indexed.
* Ask: *"What price did we quote to Company X last year?"*
* See past deals in seconds.

### 📢 Marketing

* Collect brochures, campaign reports, and presentations.
* Ask: *"Which campaigns gave us the most leads in 2024?"*
* Compare results without digging through folders.

### 🛒 Purchase & Procurement

* Index supplier contracts, price lists, and order records.
* Ask: *"Which supplier had the most delivery delays last year?"*
* Get answers across all supplier files at once.

### 📦 Inventory & Stores

* Pull together stock sheets and material logs.
* Ask: *"Do we have more than 200 units of sheet X left?"*
* Get quick status updates across multiple records.

### ⚙️ Operations & Production

* Store machine manuals, downtime logs, shift reports.
* Ask: *"Top 3 causes of downtime in 2024?"*
* Spot patterns that were hidden across files.

### ✅ Quality Control

* Index inspection sheets, rejection reports, and audits.
* Ask: *"Which part had the highest defect rate last quarter?"*
* Get the data without flipping through pages.

---

## 🎯 The Point

Every small business already has tons of data — it's just stuck in files.
Vectorpenter wakes it up, makes it searchable, and saves you hours of manual digging.

---

## 🚀 **Quick Start with VP**

### **⚡ 3-Minute Setup**

```bash
# 🎯 Step 1: Get VP's workshop
git clone https://github.com/doshirush1901/Vectorpenter.git
cd vectorpenter

# 🔧 Step 2: Setup VP's tools
cp env.example .env
# ✏️ Edit .env with your OpenAI + Pinecone keys

# 📦 Step 3: Install VP's dependencies
pip install -e .

# 🐳 Step 4: Start VP's services (optional)
make up  # Starts Typesense for hybrid search

# 🎉 Step 5: Meet VP!
python -m apps.cursor_chat
```

### **🔨 VP's First Project**

```
    🗂️ Gather Materials      ⚡ VP Works His Magic      🤔 Ask VP Questions
         ↓                           ↓                        ↓
   📁 data/inputs/           vectorpenter ingest        "What's the main
   ├── report.pdf           vectorpenter index          topic here?"
   ├── notes.md                     ↓                        ↓
   └── image.png            🧠 VP Builds Memory       💬 VP's Expert Answer
                           "Ready for questions!"      with citations
```

---

## 🔨 **VP's Superpowers**

<div align="center">

### 🔍 **Hybrid Vision**
*VP sees with both vector similarity and keyword precision*

### 🌍 **Universal Understanding** 
*VP reads any language and translates for perfect comprehension*

### 📸 **Web Capture Mastery**
*VP can capture and analyze any webpage instantly*

### 🧠 **Smart Decision Making**
*VP chooses local or cloud processing based on what works best*

### 🔗 **Context Weaving**
*VP connects related information for complete understanding*

</div>

---

## 🏗️ **VP's Workshop Architecture**

```
                         🏗️ VP'S VECTORPENTER WORKSHOP 🏗️
                                      
    📄 Document Arrives                    🤖 You Ask VP
         ↓                                      ↓
    ┌─────────────┐                    ┌─────────────┐
    │ 🔨 Smart    │                    │ 🎯 Hybrid   │
    │   Parser    │ ──┐            ┌── │   Search    │
    │             │   │            │   │             │
    │ • Local     │   │            │   │ • Vector    │
    │ • DocAI     │   │            │   │ • Keyword   │
    │ • OCR       │   │            │   │ • Rerank    │
    └─────────────┘   │            │   └─────────────┘
                      ↓            ↑
    ┌─────────────┐   │            │   ┌─────────────┐
    │ 🌍 Auto     │   │            │   │ 🔗 Context  │
    │ Translate   │ ──┤    🧠 VP   ├── │ Expansion   │
    │             │   │   MEMORY   │   │             │
    │ • Detect    │   │            │   │ • Neighbors │
    │ • Convert   │   │  (SQLite)  │   │ • Flow      │
    │ • Preserve  │   │            │   │ • Continuity│
    └─────────────┘   │            │   └─────────────┘
                      ↓            ↑
    ┌─────────────┐   │            │   ┌─────────────┐
    │ ⚡ Embed &  │   │            │   │ 🌐 Web      │
    │   Store     │ ──┤            ├── │ Grounding   │
    │             │   │            │   │             │
    │ • OpenAI    │   │            │   │ • Google    │
    │ • Cache     │   │            │   │ • Fallback  │
    │ • Index     │   │            │   │ • Current   │
    └─────────────┘   │            │   └─────────────┘
                      ↓            ↑
    ┌─────────────┐                    ┌─────────────┐
    │ 📦 Archive  │                    │ 💬 Craft    │
    │   (GCS)     │                    │   Answer    │
    │             │                    │             │
    │ • Raw       │                    │ • OpenAI    │
    │ • Translated│                    │ • Vertex    │
    │ • Audit     │                    │ • Citations │
    └─────────────┘                    └─────────────┘
```

---

## 🎯 **VP's Workshop Modes**

<table>
<tr>
<td width="33%" align="center">

### 🏠 **Local Workshop**
*VP's private studio*

```
🔒 Private
⚡ Fast  
💰 Free
🔨 Precise
```

**VP says**: *"Your secrets stay in your workshop"*

</td>
<td width="33%" align="center">

### ☁️ **Cloud-Enhanced Workshop** 
*VP's expanded capabilities*

```
🌍 Global
🧠 Smart
📈 Scalable
🎯 Intelligent
```

**VP says**: *"I use cloud tools when they make me better"*

</td>
<td width="33%" align="center">

### 🏢 **Enterprise Forge**
*VP's professional operation*

```
🛡️ Secure
📊 Analytics
🎯 Professional
⚖️ Compliant
```

**VP says**: *"Built for serious work, serious results"*

</td>
</tr>
</table>

---

## 🔨 **VP's Tool Belt**

### **📚 Knowledge Management**

```bash
# 📥 VP ingests your documents
vectorpenter ingest ./data/inputs

# ⚡ VP builds his memory index
vectorpenter index

# 🔍 Ask VP anything
vectorpenter ask "What's the summary?"
```

### **🌟 VP's Advanced Techniques**

```bash
# 🎯 VP's hybrid vision + reranking
vectorpenter ask "complex query" \
  --hybrid --rerank --k 20

# 📸 VP captures the web
vectorpenter snap --url "https://example.com"

# 💬 Chat with VP directly
python -m apps.cursor_chat
```

---

## 🎪 **VP's Workshop Interfaces**

<table>
<tr>
<td width="33%" align="center">

### 💬 **Chat with VP**
*Direct conversation mode*

```bash
python -m apps.cursor_chat
```

```
🔨 VP: What can I help you build today?

You: What's our revenue?

🔨 VP: Based on Q3 report [#1], 
revenue increased 23% to $2.4M...

📚 Sources: 3 chunks
```

</td>
<td width="33%" align="center">

### 🌐 **VP's API Workshop**
*RESTful service interface*

```bash
uvicorn apps.api:app --reload
```

```json
POST /query
{
  "q": "What's our strategy?",
  "hybrid": true,
  "rerank": true
}
```

</td>
<td width="33%" align="center">

### ⚡ **VP's Command Center** 
*Direct command interface*

```bash
vectorpenter ask \
  "competitive analysis" \
  --hybrid --rerank
```

```
🔨 VP's ANSWER (hybrid+rerank):
Our competitive advantages...
📚 Local Sources: 5 chunks
🌐 External Sources: 2 Google results
```

</td>
</tr>
</table>

---

## 🎯 **VP's Masterwork Examples**

### **🏢 Business Intelligence with VP**
```bash
# VP captures competitor intelligence
vectorpenter snap --url "https://competitor.com/pricing"

# VP analyzes with your internal docs
vectorpenter ask "How do their prices compare to ours?" --hybrid --rerank
```

### **📚 VP's Research Assistant Mode**
```bash
# VP processes research papers (any language)
vectorpenter ingest ./research_papers/  # VP auto-translates

# VP provides insights with web grounding
vectorpenter ask "What are the latest trends?" --hybrid
# VP combines your docs + current web information
```

### **🌍 VP's Global Team Support**
```bash
# Tokyo team uploads Japanese docs
vectorpenter ingest ./japanese_docs/  # VP translates

# US team asks questions in English  
vectorpenter ask "What did the Tokyo team report?"
# VP seamlessly searches translated content
```

---

## 🏗️ **VP's Technical Blueprint**

### **🔨 The VP Architecture**

```
                          🏗️ VP'S WORKSHOP BLUEPRINT 🏗️
                                     
    🚪 interfaces/        🧠 core/               🎯 rag/
    ├── 💬 cli.py         ├── ⚙️ config.py       ├── 🔍 retriever.py
    ├── 🌐 api.py         ├── 📊 monitoring.py   ├── ⚡ reranker.py  
    ├── 🎮 cursor_chat.py ├── 🛡️ resilience.py   ├── 🧠 generator.py
    └── 🔧 admin.py       └── 🔒 validation.py   └── 🔗 context_builder.py
                                     
    🌍 gcp/               🔍 search/             📁 ingest/
    ├── 📄 docai.py       ├── 🔤 typesense.py    ├── 📂 loaders.py
    ├── 🌐 vertex.py      └── 🤝 hybrid.py       ├── 🔨 parsers.py
    ├── 🌍 translation.py                        ├── ✂️ chunkers.py
    ├── 🔍 search.py                             └── ⚡ pipeline.py
    └── 📦 gcs.py
```

### **🎨 VP's Data Flow Masterpiece**

```
🔨 VP'S VECTORPENTER JOURNEY 🔨

📄 Document → 🔍 Parse → 🌍 Translate → ✂️ Chunk → ⚡ Embed → 🧠 Store
    ↓             ↓          ↓            ↓         ↓        ↓
   Any         Smart      Auto-Lang    Intelligent OpenAI   Vector
  Format      DocAI      Detection     Splitting   Magic   Memory
                                                            
🤔 Question → ⚡ Embed → 🔍 Search → 🔗 Expand → 🌐 Ground → 💬 Answer
    ↓           ↓         ↓          ↓          ↓         ↓
  Natural    OpenAI    Hybrid    Late      Google   VP's
  Language   Magic     Vector+   Window    Search   Wisdom
                      Keyword   Context   Fallback  +Citations
```

---

## 🌟 **VP's Success Stories**

<div align="center">

### 🏢 **"VP transformed our workflow!"**
*"VP processes our multilingual contracts automatically. True craftsmanship!"*
**— Manufacturing Company CEO**

### 📚 **"VP makes research effortless!"**
*"I drop PDFs, ask questions, VP delivers insights with citations. Pure magic!"*
**— Graduate Student**

### 🌐 **"VP provides competitive intelligence!"**
*"VP captures competitor sites, analyzes with our docs, delivers strategy!"*
**— Marketing Director**

</div>

---

## 🎁 **VP's Service Tiers**

### **🔨 Apprentice Tier (Free)** 
```
✅ All core features
✅ Local processing  
✅ Community support
✅ MIT License
```

### **🏗️ Craftsman Tier (Professional)** 
```
✅ Hybrid search
✅ Smart reranking
✅ Cloud features
✅ Email support
```

### **🏛️ Master Builder Tier (Enterprise)**
```
✅ All features
✅ Priority support
✅ Custom integrations
✅ SLA guarantees
```

[**🚀 Start Free →**](https://github.com/doshirush1901/Vectorpenter) | [**🏗️ Go Pro →**](mailto:sales@machinecraft.tech) | [**🏛️ Enterprise →**](mailto:enterprise@machinecraft.tech)

---

## 🤝 **Join VP's Workshop**

<div align="center">

### 🔨 **Become VP's Apprentice**

[![GitHub Issues](https://img.shields.io/github/issues/doshirush1901/Vectorpenter)](https://github.com/doshirush1901/Vectorpenter/issues)
[![GitHub PRs](https://img.shields.io/github/issues-pr/doshirush1901/Vectorpenter)](https://github.com/doshirush1901/Vectorpenter/pulls)

**🔨 Contributing**: Read our [Contribution Guide](CONTRIBUTING.md)  
**🛡️ Security**: Report issues via [Security Policy](SECURITY.md)  
**💰 Commercial**: Check our [Pricing Guide](PRICING.md)

</div>

---

## 🔨 **VP's Philosophy**

<div align="center">

> *"Like a master carpenter who knows exactly which tool to use for each task,*  
> *I intelligently choose the right AI service for each document.*  
> *Local when possible, cloud when beneficial, always with respect for your privacy."*
> 
> **— VP, The Carpenter of Context**

**🔨 Built with precision by [Machinecraft Technologies](https://machinecraft.tech)**

</div>

---

## 🎯 **VP's Workshop Commands**

<details>
<summary>🔨 <strong>VP's Tool Belt</strong></summary>

```bash
# 🐳 WORKSHOP SERVICES
make up                             # Start Typesense (hybrid search)
make up-all                         # Start all services
make down                           # Stop all services

# 📥 DOCUMENT INGESTION
vectorpenter ingest ./docs          # VP processes documents
vectorpenter snap --url "site.com"  # VP captures webpage

# 🔍 KNOWLEDGE SEARCH  
vectorpenter ask "question"          # Basic search
vectorpenter ask "question" --hybrid # Vector + keyword
vectorpenter ask "question" --rerank # VP's reranking (Voyage AI only)
vectorpenter ask "question" --hybrid --rerank --k 20  # Full power

# 🛠️ WORKSHOP MANAGEMENT
vectorpenter index                   # Build search indexes
python -m apps.cursor_chat          # Chat with VP directly
uvicorn apps.api:app --reload       # Start VP's API workshop

# 🔧 DEVELOPMENT WITH VP
make dev-setup                      # Setup VP's environment
make test                          # Test VP's capabilities
make eval                          # Evaluate VP's performance
```

</details>

---

## ⚡ **Local Quickstart (Copy-Paste Ready)**

```bash
# 1. Clone VP's workshop
git clone https://github.com/doshirush1901/Vectorpenter.git
cd vectorpenter
cp env.example .env

# 2. Give VP his essential keys (minimum required):
# OPENAI_API_KEY=sk-your-key-here
# PINECONE_API_KEY=your-pinecone-key

# 3. Install VP and start his services
pip install -e .
make up  # Starts Typesense for hybrid search

# 4. Give VP something to work with
echo "Vectorpenter is amazing for document search!" > data/inputs/test.txt
vectorpenter ingest data/inputs
vectorpenter index
vectorpenter ask "What is Vectorpenter?" --hybrid --rerank

# 5. Start chatting with VP
python -m apps.cursor_chat
```

### **🌟 Advanced Setup (All VP's Powers)**

```bash
# Enable all of VP's cloud abilities in .env:
USE_GOOGLE_DOC_AI=true        # Smart PDF parsing
USE_TRANSLATION=true          # Multi-language support  
USE_GOOGLE_GROUNDING=true     # Web search fallback
USE_SCREENSHOTONE=true        # Webpage capture
USE_GCS=true                  # Audit archival

# Then follow GCP_SETUP.md to give VP his cloud tools
```

---

<div align="center">

### 🔨 **Ready to Build with VP?**

**VP is waiting in his workshop, tools ready, eager to help you organize your knowledge!**

**🔨 Start building vectors into memory with VP today! ✨**

---

*Crafted with 🔨 Care • Built with ❤️ Love • Powered by ⚡ Innovation*

**© 2025 Machinecraft Technologies • VP - The Carpenter of Context**

</div>