# 🔨 Vectorpenter
```
                    ╭─────────────────────────────────────────╮
                    │  🏗️  The Carpenter of Context           │
                    │     Building Vectors into Memory        │
                    │                                         │
                    │  ⚡ Local-First • 🧠 AI-Powered         │
                    │  🔍 Hybrid Search • 🌍 Multi-Language   │
                    ╰─────────────────────────────────────────╯
```

<div align="center">

**🎌 Konnichiwa! Meet your AI document companion!**

*Transform any document into searchable knowledge with the power of AI*

[![GitHub stars](https://img.shields.io/github/stars/doshirush1901/Vectorpenter?style=social)](https://github.com/doshirush1901/Vectorpenter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

</div>

---

## 🌸 **What is Vectorpenter?**

```
    📚 Your Documents          🔨 Vectorpenter          🤖 AI Knowledge
         ↓                           ↓                        ↓
   ┌─────────────┐            ┌─────────────┐         ┌─────────────┐
   │  📄 PDFs    │   ────→    │  🧠 Smart   │  ────→  │ 💬 Natural  │
   │  📊 Excel   │            │     AI      │         │   Language  │
   │  🖼️ Images  │            │  Processing │         │   Answers   │
   │  🌐 Websites│            │             │         │             │
   └─────────────┘            └─────────────┘         └─────────────┘
        Drop files              Magic happens           Ask questions
```

Vectorpenter is your **local AI companion** that transforms documents into intelligent, searchable knowledge. Think of it as having a super-smart librarian who reads everything and can answer any question about your documents! 📖✨

---

## 🚀 **Quick Start Adventure**

### **⚡ 3-Minute Setup**

```bash
# 🎯 Step 1: Get Vectorpenter
git clone https://github.com/doshirush1901/Vectorpenter.git
cd vectorpenter

# 🔧 Step 2: Setup (copy-paste magic!)
cp env.example .env
# ✏️ Edit .env with your OpenAI + Pinecone keys

# 📦 Step 3: Install
pip install -e .  # Installs vectorpenter command

# 🐳 Step 4: Start local services (optional)
make up  # Starts Typesense for hybrid search

# 🎉 Step 5: Start chatting!
python -m apps.cursor_chat
```

### **🎌 Your First Journey**

```
    🗂️ Drop Documents        ⚡ Process        🤔 Ask Questions
         ↓                      ↓                  ↓
   📁 data/inputs/         vectorpenter      "What's the main
   ├── report.pdf          ingest + index     topic here?"
   ├── notes.md                 ↓                  ↓
   └── image.png          🧠 AI Magic        💬 Smart Answer
                         happening...        with citations!
```

---

## 🌟 **Superpowers Unlocked**

<div align="center">

### 🔍 **Hybrid Search Sensei**
*Combines vector similarity + keyword matching for perfect results*

### 🌍 **Multilingual Ninja** 
*Auto-translates any language → English for better understanding*

### 📸 **Web Snapshot Wizard**
*Capture any webpage directly into your knowledge base*

### 🧠 **Smart PDF Samurai**
*Automatically upgrades to cloud OCR for scanned documents*

### 🔗 **Context Expansion Master**
*Includes neighboring text chunks for complete understanding*

</div>

---

## 🎨 **The Magic Behind the Scenes**

```
                     🎌 VECTORPENTER PROCESSING DOJO 🎌
                                      
    📄 Document Arrives                    🤖 User Asks Question
         ↓                                        ↓
    ┌─────────────┐                      ┌─────────────┐
    │ 🔍 Smart    │                      │ 🎯 Hybrid   │
    │   Parser    │ ──┐              ┌── │   Search    │
    │             │   │              │   │             │
    │ • Local     │   │              │   │ • Vector    │
    │ • DocAI     │   │              │   │ • Keyword   │
    │ • OCR       │   │              │   │ • Rerank    │
    └─────────────┘   │              │   └─────────────┘
                      ↓              ↑
    ┌─────────────┐   │              │   ┌─────────────┐
    │ 🌍 Auto     │   │              │   │ 🔗 Late     │
    │ Translate   │ ──┤              ├── │ Windowing   │
    │             │   │              │   │             │
    │ • Detect    │   │              │   │ • Neighbors │
    │ • Convert   │   │              │   │ • Context   │
    │ • Preserve  │   │              │   │ • Flow      │
    └─────────────┘   │              │   └─────────────┘
                      ↓              ↑
    ┌─────────────┐   │   🧠 BRAIN   │   ┌─────────────┐
    │ ⚡ Chunk &  │   │              │   │ 🌐 Google   │
    │   Embed     │ ──┤   VECTOR     ├── │ Grounding   │
    │             │   │   MEMORY     │   │             │
    │ • OpenAI    │   │              │   │ • Fallback  │
    │ • Cache     │   │   (SQLite)   │   │ • External  │
    │ • Store     │   │              │   │ • Current   │
    └─────────────┘   │              │   └─────────────┘
                      ↓              ↑
    ┌─────────────┐                      ┌─────────────┐
    │ 📦 Archive  │                      │ 💬 Generate │
    │   (GCS)     │                      │   Answer    │
    │             │                      │             │
    │ • Raw       │                      │ • OpenAI    │
    │ • Translated│                      │ • Vertex    │
    │ • Audit     │                      │ • Citations │
    └─────────────┘                      └─────────────┘
```

---

## 🎯 **Choose Your Adventure**

<table>
<tr>
<td width="33%" align="center">

### 🏠 **Local Sensei**
*Privacy-first, runs on your laptop*

```
🔒 Private
⚡ Fast  
💰 Free
```

**Perfect for**: Personal projects, sensitive data, offline work

</td>
<td width="33%" align="center">

### ☁️ **Cloud Ninja** 
*Smart cloud features when needed*

```
🌍 Global
🧠 Smart
📈 Scalable
```

**Perfect for**: Teams, multi-language docs, web content

</td>
<td width="33%" align="center">

### 🏢 **Enterprise Samurai**
*Production-ready with full features*

```
🛡️ Secure
📊 Analytics
🎯 Professional
```

**Perfect for**: Companies, compliance, commercial use

</td>
</tr>
</table>

---

## 🎌 **Meet Your AI Companions**

<div align="center">

### 🤖 **Vecto-chan** 
*Your friendly embedding specialist*
> *"I turn your words into mathematical magic! ✨"*

### 🔍 **Search-kun**
*The hybrid search master*
> *"I find exactly what you're looking for! 🎯"*

### 🌸 **Context-san**
*The wise context builder*
> *"I weave your knowledge into beautiful stories! 📚"*

</div>

---

## 🎮 **Command Palette**

<table>
<tr>
<td width="50%">

### 📚 **Knowledge Management**

```bash
# 📥 Ingest documents
vectorpenter ingest ./data/inputs

# ⚡ Build search index  
vectorpenter index

# 🔍 Ask questions
vectorpenter ask "What's the summary?"
```

</td>
<td width="50%">

### 🌟 **Advanced Techniques**

```bash
# 🥷 Hybrid search + reranking
vectorpenter ask "complex query" \
  --hybrid --rerank --k 20

# 📸 Capture webpage
vectorpenter snap --url "https://example.com"

# 💬 Interactive chat
python -m apps.cursor_chat
```

</td>
</tr>
</table>

---

## 🎯 **Power-Up Examples**

### **🏢 Business Intelligence**
```bash
# Capture competitor website
vectorpenter snap --url "https://competitor.com/pricing"

# Analyze with your internal docs
vectorpenter ask "How do their prices compare to ours?" --hybrid --rerank
```

### **📚 Research Assistant**
```bash
# Process research papers (any language)
vectorpenter ingest ./research_papers/  # Auto-translates to English

# Get insights with web grounding
vectorpenter ask "What are the latest trends?" --hybrid
# Combines your docs + current web information
```

### **🌍 Global Team Collaboration**
```bash
# Team in Japan uploads Japanese docs
vectorpenter ingest ./japanese_docs/  # Auto-translates

# Team in US asks questions in English
vectorpenter ask "What did the Tokyo team report?"
# Seamlessly searches translated content
```

---

## 🎪 **Interactive Modes**

<table>
<tr>
<td width="33%" align="center">

### 💬 **Chat Dojo**
*Interactive conversation mode*

```bash
python -m apps.cursor_chat
```

```
🤖 Ask me anything: What's our revenue?

📖 ANSWER:
Based on Q3 report [#1], revenue 
increased 23% to $2.4M...

📚 Sources: 3 chunks
```

</td>
<td width="33%" align="center">

### 🌐 **API Shrine**
*RESTful web service*

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

### ⚡ **CLI Temple** 
*Command-line interface*

```bash
vectorpenter ask \
  "competitive analysis" \
  --hybrid --rerank
```

```
=== ANSWER (hybrid+rerank) ===
Our competitive advantages...
📚 Local Sources: 5 chunks
🌐 External Sources: 2 Google results
```

</td>
</tr>
</table>

---

## 🏗️ **Technical Dojo**

### **🎌 The Sacred Architecture**

```
                          🏯 VECTORPENTER CASTLE 🏯
                                     
    🚪 apps/              🏛️ core/               🎯 rag/
    ├── 💬 cli.py         ├── ⚙️ config.py       ├── 🔍 retriever.py
    ├── 🌐 api.py         ├── 📊 monitoring.py   ├── ⚡ reranker.py  
    └── 🎮 cursor_chat.py ├── 🛡️ resilience.py   ├── 🧠 generator.py
                          └── 🔒 validation.py   └── 🔗 context_builder.py
                                     
    🌍 gcp/               🔍 search/             📁 ingest/
    ├── 📄 docai.py       ├── 🔤 typesense.py    ├── 📂 loaders.py
    ├── 🌐 vertex.py      └── 🤝 hybrid.py       ├── 🔨 parsers.py
    ├── 🌍 translation.py                        ├── ✂️ chunkers.py
    ├── 🔍 search.py                             └── ⚡ pipeline.py
    └── 📦 gcs.py
```

### **🎨 Data Flow Masterpiece**

```
🎌 THE VECTORPENTER JOURNEY 🎌

📄 Document → 🔍 Parse → 🌍 Translate → ✂️ Chunk → ⚡ Embed → 🧠 Store
    ↓             ↓          ↓            ↓         ↓        ↓
   Any         Smart      Auto-Lang    Intelligent OpenAI   Vector
  Format      DocAI      Detection     Splitting   Magic   Memory
                                                            
🤔 Question → ⚡ Embed → 🔍 Search → 🔗 Expand → 🌐 Ground → 💬 Answer
    ↓           ↓         ↓          ↓          ↓         ↓
  Natural    OpenAI    Hybrid    Late      Google   Smart
  Language   Magic     Vector+   Window    Search   Response
                      Keyword   Context   Fallback  +Citations
```

---

## 🌟 **Superpowers Unlocked**

<div align="center">

### 🔍 **Hybrid Search Sensei**
*Combines vector similarity + keyword matching for perfect results*

### 🌍 **Multilingual Ninja** 
*Auto-translates any language → English for better understanding*

### 📸 **Web Snapshot Wizard**
*Capture any webpage directly into your knowledge base*

### 🧠 **Smart PDF Samurai**
*Automatically upgrades to cloud OCR for scanned documents*

### 🔗 **Context Expansion Master**
*Includes neighboring text chunks for complete understanding*

</div>

---

## 🎯 **Choose Your Adventure**

<table>
<tr>
<td width="33%" align="center">

### 🏠 **Local Sensei**
*Privacy-first, runs on your laptop*

```
🔒 Private
⚡ Fast  
💰 Free
```

**Perfect for**: Personal projects, sensitive data, offline work

</td>
<td width="33%" align="center">

### ☁️ **Cloud Ninja** 
*Smart cloud features when needed*

```
🌍 Global
🧠 Smart
📈 Scalable
```

**Perfect for**: Teams, multi-language docs, web content

</td>
<td width="33%" align="center">

### 🏢 **Enterprise Samurai**
*Production-ready with full features*

```
🛡️ Secure
📊 Analytics
🎯 Professional
```

**Perfect for**: Companies, compliance, commercial use

</td>
</tr>
</table>

---

## 🎌 **Meet Your AI Companions**

<div align="center">

### 🤖 **Vecto-chan** 
*Your friendly embedding specialist*
> *"I turn your words into mathematical magic! ✨"*

### 🔍 **Search-kun**
*The hybrid search master*
> *"I find exactly what you're looking for! 🎯"*

### 🌸 **Context-san**
*The wise context builder*
> *"I weave your knowledge into beautiful stories! 📚"*

</div>

---

## 🎮 **Command Palette**

<table>
<tr>
<td width="50%">

### 📚 **Knowledge Management**

```bash
# 📥 Ingest documents
vectorpenter ingest ./data/inputs

# ⚡ Build search index  
vectorpenter index

# 🔍 Ask questions
vectorpenter ask "What's the summary?"
```

</td>
<td width="50%">

### 🌟 **Advanced Techniques**

```bash
# 🥷 Hybrid search + reranking
vectorpenter ask "complex query" \
  --hybrid --rerank --k 20

# 📸 Capture webpage
vectorpenter snap --url "https://example.com"

# 💬 Interactive chat
python -m apps.cursor_chat
```

</td>
</tr>
</table>

---

## 🎯 **Power-Up Examples**

### **🏢 Business Intelligence**
```bash
# Capture competitor website
vectorpenter snap --url "https://competitor.com/pricing"

# Analyze with your internal docs
vectorpenter ask "How do their prices compare to ours?" --hybrid --rerank
```

### **📚 Research Assistant**
```bash
# Process research papers (any language)
vectorpenter ingest ./research_papers/  # Auto-translates to English

# Get insights with web grounding
vectorpenter ask "What are the latest trends?" --hybrid
# Combines your docs + current web information
```

### **🌍 Global Team Collaboration**
```bash
# Team in Japan uploads Japanese docs
vectorpenter ingest ./japanese_docs/  # Auto-translates

# Team in US asks questions in English
vectorpenter ask "What did the Tokyo team report?"
# Seamlessly searches translated content
```

---

## 🎪 **Interactive Modes**

<table>
<tr>
<td width="33%" align="center">

### 💬 **Chat Dojo**
*Interactive conversation mode*

```bash
python -m apps.cursor_chat
```

```
🤖 Ask me anything: What's our revenue?

📖 ANSWER:
Based on Q3 report [#1], revenue 
increased 23% to $2.4M...

📚 Sources: 3 chunks
```

</td>
<td width="33%" align="center">

### 🌐 **API Shrine**
*RESTful web service*

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

### ⚡ **CLI Temple** 
*Command-line interface*

```bash
vectorpenter ask \
  "competitive analysis" \
  --hybrid --rerank
```

```
=== ANSWER (hybrid+rerank) ===
Our competitive advantages...
📚 Local Sources: 5 chunks
🌐 External Sources: 2 Google results
```

</td>
</tr>
</table>

---

## 🌈 **Special Abilities**

### 📸 **Web Capture Jutsu**

```bash
# 🌸 Capture the essence of any webpage
vectorpenter snap --url "https://news.ycombinator.com"

# 🔍 Make it searchable instantly
vectorpenter ingest data/inputs
vectorpenter ask "What's trending in tech?"
```

### 🌍 **Universal Language Mastery**

```bash
# 🎋 Process documents in any language
# Vectorpenter automatically detects and translates!

vectorpenter ingest ./japanese_docs/    # 日本語 → English
vectorpenter ingest ./spanish_reports/  # Español → English  
vectorpenter ask "What did all teams report?"  # 🌍 Global insights
```

---

## 🏗️ **Technical Dojo**

### **🎌 The Sacred Architecture**

```
                          🏯 VECTORPENTER CASTLE 🏯
                                     
    🚪 apps/              🏛️ core/               🎯 rag/
    ├── 💬 cli.py         ├── ⚙️ config.py       ├── 🔍 retriever.py
    ├── 🌐 api.py         ├── 📊 monitoring.py   ├── ⚡ reranker.py  
    └── 🎮 cursor_chat.py ├── 🛡️ resilience.py   ├── 🧠 generator.py
                          └── 🔒 validation.py   └── 🔗 context_builder.py
                                     
    🌍 gcp/               🔍 search/             📁 ingest/
    ├── 📄 docai.py       ├── 🔤 typesense.py    ├── 📂 loaders.py
    ├── 🌐 vertex.py      └── 🤝 hybrid.py       ├── 🔨 parsers.py
    ├── 🌍 translation.py                        ├── ✂️ chunkers.py
    ├── 🔍 search.py                             └── ⚡ pipeline.py
    └── 📦 gcs.py
```

---

## 🌟 **Success Stories**

<div align="center">

### 🏢 **"Transformed our document workflow!"**
*"Vectorpenter processes our multilingual contracts automatically. Game changer!"*
**— Manufacturing Company CEO**

### 📚 **"Research made simple!"**
*"I drop PDFs, ask questions, get instant insights with citations. Magic!"*
**— Graduate Student**

### 🌐 **"Competitive intelligence on autopilot!"**
*"Snap competitor sites, analyze with our docs, get strategic insights!"*
**— Marketing Director**

</div>

---

## 🎁 **Getting Started Gifts**

### **🎌 Free Tier** 
```
✅ All core features
✅ Local processing  
✅ Community support
✅ MIT License
```

### **💼 Professional** 
```
✅ Hybrid search
✅ Smart reranking
✅ Cloud features
✅ Email support
```

### **🏢 Enterprise**
```
✅ All features
✅ Priority support
✅ Custom integrations
✅ SLA guarantees
```

[**🚀 Start Free →**](https://github.com/doshirush1901/Vectorpenter) | [**💼 Go Pro →**](mailto:sales@machinecraft.tech) | [**🏢 Enterprise →**](mailto:enterprise@machinecraft.tech)

---

## 🎪 **Community Dojo**

<div align="center">

### 🤝 **Join the Adventure**

[![GitHub Issues](https://img.shields.io/github/issues/doshirush1901/Vectorpenter)](https://github.com/doshirush1901/Vectorpenter/issues)
[![GitHub PRs](https://img.shields.io/github/issues-pr/doshirush1901/Vectorpenter)](https://github.com/doshirush1901/Vectorpenter/pulls)
[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-7289da)](https://discord.gg/vectorpenter)

**🌸 Contributing**: Read our [Contribution Guide](CONTRIBUTING.md)  
**🛡️ Security**: Report issues via [Security Policy](SECURITY.md)  
**💰 Commercial**: Check our [Pricing Guide](PRICING.md)

</div>

---

## 🎌 **The Vectorpenter Philosophy**

<div align="center">

> *"Like a master carpenter who knows exactly which tool to use for each task,*  
> *Vectorpenter intelligently chooses the right AI service for each document.*  
> *Local when possible, cloud when beneficial, always with respect for your privacy."*

**🔨 Built with ❤️ by [Machinecraft Technologies](https://machinecraft.tech)**

</div>

---

## 🌸 **Quick Reference Card**

<details>
<summary>📋 <strong>Command Cheat Sheet</strong></summary>

```bash
# 🐳 SERVICES
make up                             # Start Typesense (hybrid search)
make up-all                         # Start all services (Typesense, PostgreSQL, Redis)
make down                           # Stop all services

# 📥 INGESTION
vectorpenter ingest ./docs          # Process documents
vectorpenter snap --url "site.com"  # Capture webpage

# 🔍 SEARCH & QUERY  
vectorpenter ask "question"          # Basic search
vectorpenter ask "question" --hybrid # Vector + keyword
vectorpenter ask "question" --rerank # Voyage AI reranking (ONLY reranker)
vectorpenter ask "question" --hybrid --rerank --k 20  # Full power

# 🛠️ MANAGEMENT
vectorpenter index                   # Build search indexes
python -m apps.cursor_chat          # Interactive mode
uvicorn apps.api:app --reload       # Start API server

# 🔧 DEVELOPMENT
make dev-setup                      # Setup environment
make test                          # Run tests  
make production-check              # Validate readiness
```

</details>

---

<div align="center">

### 🎉 **Ready to Build Your Knowledge Empire?**

#### **⚡ Local Quickstart (Copy-Paste Ready)**

```bash
# 1. Clone and setup
git clone https://github.com/doshirush1901/Vectorpenter.git
cd vectorpenter
cp env.example .env

# 2. Edit .env with your keys (minimum required):
# OPENAI_API_KEY=sk-your-key-here
# PINECONE_API_KEY=your-pinecone-key

# 3. Install and start services
pip install -e .
make up  # Starts Typesense for hybrid search

# 4. Create sample data and test
echo "Vectorpenter is amazing for document search!" > data/inputs/test.txt
vectorpenter ingest data/inputs
vectorpenter index
vectorpenter ask "What is Vectorpenter?" --hybrid --rerank

# 5. Start interactive chat
python -m apps.cursor_chat
```

#### **🌟 Advanced Setup (All Features)**

```bash
# Enable all Google Cloud features in .env:
USE_GOOGLE_DOC_AI=true        # Smart PDF parsing
USE_TRANSLATION=true          # Multi-language support  
USE_GOOGLE_GROUNDING=true     # Web search fallback
USE_SCREENSHOTONE=true        # Webpage capture
USE_GCS=true                  # Audit archival

# Then follow GCP_SETUP.md for service configuration
```

**🔨 Start building vectors into memory today! ✨**

---

*Made with 🤖 AI • Built with ❤️ Love • Powered by ⚡ Innovation*

**© 2025 Machinecraft Technologies • The Carpenter of Context**

</div>
