# GCP Setup Guide for Vectorpenter

This guide walks you through setting up Google Cloud Platform services for enhanced PDF parsing and optional Vertex AI chat.

## 🎯 **What You'll Get**

- **Smart PDF Parsing**: Auto-upgrade to Document AI for scanned/low-text PDFs
- **Optional Vertex Chat**: Use Gemini instead of OpenAI for responses
- **Cost Control**: Only uses GCP when local parsing insufficient
- **Embeddings Stay OpenAI**: No change to embedding provider

## 📋 **Prerequisites**

- Google Cloud Platform account
- Billing enabled on your GCP project
- Basic familiarity with GCP Console

## 🚀 **Step-by-Step Setup**

### **Step 1: Create GCP Project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your **Project ID** (you'll need this)

### **Step 2: Enable Required APIs**

```bash
# Using gcloud CLI (recommended)
gcloud services enable documentai.googleapis.com
gcloud services enable aiplatform.googleapis.com  # If using Vertex chat

# Or enable via Console:
# 1. Go to APIs & Services > Library
# 2. Search for "Document AI API" and enable
# 3. Search for "Vertex AI API" and enable (if using chat)
```

### **Step 3: Create Document AI Processor**

1. Go to [Document AI Console](https://console.cloud.google.com/ai/document-ai)
2. Click **"Create Processor"**
3. Select **"Document OCR"** processor type
4. Choose **Region**: `us` (or your preferred region)
5. Give it a name like **"vectorpenter-pdf-parser"**
6. Click **Create**
7. **Copy the Processor ID** (format: `projects/YOUR_PROJECT/locations/us/processors/PROCESSOR_ID`)

### **Step 4: Create Service Account**

```bash
# Using gcloud CLI
gcloud iam service-accounts create vectorpenter-service \
    --display-name="Vectorpenter Service Account"

# Grant required roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:vectorpenter-service@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/documentai.apiUser"

# If using Vertex chat, also grant:
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:vectorpenter-service@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Download credentials
gcloud iam service-accounts keys create ./creds/service-account.json \
    --iam-account=vectorpenter-service@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

**Or via Console:**
1. Go to **IAM & Admin > Service Accounts**
2. Click **"Create Service Account"**
3. Name: `vectorpenter-service`
4. Grant roles:
   - `Document AI API User`
   - `Vertex AI User` (if using chat)
5. Click **"Create Key"** > **JSON**
6. Save as `./creds/service-account.json`

### **Step 5: Configure Environment**

Create or update your `.env` file:

```env
# ==== GCP / DocAI (optional) ====
GOOGLE_APPLICATION_CREDENTIALS=./creds/service-account.json
GCP_PROJECT_ID=your-project-id-here
GCP_LOCATION=us

# PDF parsing
USE_GOOGLE_DOC_AI=false  # Set to true to force DocAI for all PDFs
DOC_AI_PROCESSOR_ID=projects/your-project-id/locations/us/processors/your-processor-id

# ==== Vertex Chat ONLY (optional) ====
USE_VERTEX_CHAT=false  # Set to true to use Gemini instead of OpenAI for chat
VERTEX_CHAT_MODEL=gemini-1.5-pro
```

### **Step 6: Install GCP Dependencies**

```bash
# Install with GCP support
pip install -r requirements.txt

# Verify GCP libraries are installed
python -c "from google.cloud import documentai, aiplatform; print('✅ GCP libraries installed')"
```

### **Step 7: Test Configuration**

```bash
# Test imports and configuration
python tests/smoke_test.py

# Test Document AI connection
python -c "
from gcp.docai import test_docai_connection
result = test_docai_connection()
print(f'DocAI connection: {\"✅ Success\" if result else \"❌ Failed\"}')
"

# Test Vertex AI connection (if enabled)
python -c "
from gcp.vertex import test_vertex_connection
result = test_vertex_connection()
print(f'Vertex AI connection: {\"✅ Success\" if result else \"❌ Failed\"}')
"
```

## 🔧 **Usage Examples**

### **Default Behavior (Local-First)**
```bash
# Uses local parsers for all documents
vectorpenter ingest ./data/inputs
vectorpenter ask "What are the main topics?"
```

### **Auto-Upgrade for Scanned PDFs**
```bash
# Automatically uses DocAI for PDFs with poor local extraction
# Configure GCP as above, then:
vectorpenter ingest ./data/inputs  # Will auto-upgrade problematic PDFs
```

### **Force DocAI for All PDFs**
```bash
# Set in .env: USE_GOOGLE_DOC_AI=true
vectorpenter ingest ./data/inputs  # All PDFs use DocAI
```

### **Use Vertex Chat**
```bash
# Set in .env: USE_VERTEX_CHAT=true
vectorpenter ask "Explain this document"  # Uses Gemini for response
# Note: Embeddings still use OpenAI
```

## 💰 **Cost Management**

### **Document AI Pricing**
- **Document OCR**: ~$0.015 per page
- **Typical PDF**: 10-20 pages = $0.15-$0.30 per document
- **Auto-upgrade only**: Costs only apply to scanned/problematic PDFs

### **Vertex AI Pricing**
- **Gemini 1.5 Pro**: ~$0.0025 per 1K input chars, ~$0.005 per 1K output chars
- **Typical query**: $0.01-$0.05 per response

### **Cost Estimation**
```python
# Check estimated costs before processing
from gcp.docai import get_docai_usage_estimate
from gcp.vertex import estimate_vertex_cost

# For a 2MB PDF
pdf_estimate = get_docai_usage_estimate(2 * 1024 * 1024)
print(f"Estimated cost: ${pdf_estimate['estimated_cost_usd']}")

# For a chat response
chat_estimate = estimate_vertex_cost(1000, 500)  # 1K input, 500 output chars
print(f"Chat cost: ${chat_estimate['total_cost_usd']}")
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **"Permission denied" errors**
   - Verify service account has correct roles
   - Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct

2. **"Processor not found" errors**
   - Verify `DOC_AI_PROCESSOR_ID` format is correct
   - Ensure processor exists in the specified region

3. **"Import errors" for Google Cloud libraries**
   - Run: `pip install google-cloud-documentai google-cloud-aiplatform`

4. **"Project not found" errors**
   - Verify `GCP_PROJECT_ID` matches your actual project ID
   - Ensure billing is enabled on the project

### **Debugging Commands**

```bash
# Check configuration
python -c "
from core.config import settings
print(f'Project: {settings.gcp_project_id}')
print(f'DocAI enabled: {settings.use_google_doc_ai}')
print(f'Vertex enabled: {settings.use_vertex_chat}')
"

# Test credentials
python -c "
import os
from google.auth import default
creds, project = default()
print(f'Authenticated as: {project}')
"

# Verbose logging
export LOG_LEVEL=DEBUG
vectorpenter ingest ./data/inputs  # Will show detailed parsing decisions
```

## 🛡️ **Security Best Practices**

1. **Credentials Security**
   - Never commit `service-account.json` to git
   - Use least-privilege IAM roles
   - Rotate service account keys regularly

2. **Data Privacy**
   - Document AI processes file contents in Google Cloud
   - Consider data residency requirements
   - Review Google's data processing agreements

3. **Cost Controls**
   - Set up billing alerts in GCP Console
   - Monitor usage in Cloud Console
   - Use auto-upgrade (not manual override) to minimize costs

## 📊 **Monitoring Usage**

### **GCP Console Monitoring**
- **Document AI**: Console > Document AI > Usage
- **Vertex AI**: Console > Vertex AI > Model Garden > Usage

### **Vectorpenter Logs**
```bash
# Monitor parsing decisions
tail -f vectorpenter.log | grep "PDF parser:"

# Sample output:
# PDF parser: PdfReader (local)
# PDF parser: DocAI (auto-upgrade)
# PDF parser: DocAI failed, falling back to local
```

## ✅ **Verification Checklist**

- [ ] GCP project created with billing enabled
- [ ] Document AI and Vertex AI APIs enabled
- [ ] Document OCR processor created
- [ ] Service account created with correct roles
- [ ] Credentials downloaded to `./creds/service-account.json`
- [ ] Environment variables configured in `.env`
- [ ] GCP dependencies installed (`pip install -r requirements.txt`)
- [ ] Connection tests pass (`python tests/smoke_test.py`)
- [ ] Test PDF processing with auto-upgrade

## 🎉 **You're Ready!**

Vectorpenter will now intelligently use Google Cloud services to enhance PDF parsing while maintaining its local-first approach. The system will:

- ✅ **Try local parsing first** (fast, free, private)
- ✅ **Auto-upgrade to DocAI** only when needed (scanned PDFs)
- ✅ **Gracefully fallback** if GCP services unavailable
- ✅ **Log all decisions** for transparency and debugging

Your documents will be processed more accurately while keeping costs minimal! 🔨✨
