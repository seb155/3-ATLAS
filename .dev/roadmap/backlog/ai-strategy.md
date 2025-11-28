# AI Strategy - Local First with Cloud Fallback

**Updated:** 2025-11-22  
**Hardware:** RTX 3080 Ti + Ollama + LiteLLM  
**Priority:** Data confidentiality (enterprise)

---

## 🎯 Key Requirements

1. ✅ **Data Confidentiality** (critical for enterprise projects)
2. ✅ **Local-first AI** (minimize cloud dependencies)
3. ✅ **Cost-effective** (no per-use API costs)
4. ✅ **Flexible routing** (switch models based on task)
5. ✅ **Cloud fallback** (for complex tasks)

---

## 🏗️ Your Current AI Infrastructure

### Hardware
- **GPU:** RTX 3080 Ti (12GB VRAM)
- **Sufficient for:**
  - YOLO v8 (P&ID ingestion)
  - LLaMA 3.1 70B (quantized)
  - Mistral 7B
  - Multiple concurrent requests

### Software Stack
- **Ollama** - Local LLM runtime
- **OpenWebUI** - Chat interface
- **LiteLLM** - AI router/proxy

**Perfect setup for SYNAPSE!** ✅

---

## 🤖 AI Model Strategy

### Tier 1: Local AI (Default - Confidential)

**Use Cases:**
- P&ID ingestion assistance (OCR validation)
- Chatbot navigation ("Show motors in area 210")
- Simple queries ("What's voltage for Greece?")
- Code completion (dev tools)
- Documentation search

**Models (via Ollama):**
- **LLaMA 3.1 70B** (quantized 4-bit) - Best quality local
- **Mistral 7B** - Fast, efficient
- **CodeLlama 34B** - Code-specific tasks

**Routing via LiteLLM:**
```yaml
# litellm_config.yaml
model_list:
  - model_name: llama3
    litellm_params:
      model: ollama/llama3.1:70b-instruct-q4_K_M
      api_base: http://localhost:11434
  
  - model_name: mistral
    litellm_params:
      model: ollama/mistral:7b-instruct
      api_base: http://localhost:11434
  
  - model_name: codellama
    litellm_params:
      model: ollama/codellama:34b
      api_base: http://localhost:11434
```

**Advantages:**
- ✅ 100% private (data never leaves server)
- ✅ No API costs
- ✅ Low latency (local)
- ✅ Unlimited usage

**Limitations:**
- ⚠️ Less capable than GPT-4/Claude
- ⚠️ May struggle with complex reasoning

---

### Tier 2: Cloud AI (Optional - Non-Confidential)

**Use Cases:**
- Complex P&ID analysis (rare edge cases)
- Advanced reasoning tasks
- Quality validation
- Demo/testing with latest models

**Models:**
- **OpenAI GPT-4 Turbo** - Best reasoning
- **Google Gemini 1.5 Pro** - Good vision + reasoning
- **Anthropic Claude 3.5 Sonnet** - Best for engineering tasks

**Data Confidentiality Strategy:**

**CRITICAL RULES:**
1. ❌ **NEVER send confidential project data to cloud**
   - No client names
   - No proprietary specs
   - No actual P&IDs
2. ✅ **Only send anonymized/sanitized data**
   - Generic examples
   - Test data
   - Public documentation
3. ✅ **User consent required**
   - Explicit opt-in for cloud AI
   - Clear warning about data leaving server

**Implementation:**
```python
# backend/app/services/ai_service.py
from typing import Literal

AIProvider = Literal["local", "openai", "gemini"]

class AIService:
    def __init__(self, litellm_url: str):
        self.litellm = litellm_url
        self.default_provider = "local"  # Always default to local
    
    async def query(
        self,
        prompt: str,
        context: dict,
        provider: AIProvider = "local",
        allow_cloud: bool = False
    ):
        # Check data sensitivity
        if self._contains_confidential_data(context):
            if provider != "local":
                raise ValueError(
                    "Confidential data detected. "
                    "Cloud AI not allowed for this query."
                )
        
        # Route based on provider
        if provider == "local":
            return await self._query_local(prompt, context)
        elif provider in ["openai", "gemini"] and allow_cloud:
            # Anonymize data first
            sanitized = self._sanitize_context(context)
            return await self._query_cloud(prompt, sanitized, provider)
        else:
            raise ValueError("Cloud AI requires explicit consent")
    
    def _contains_confidential_data(self, context: dict) -> bool:
        # Check for confidential markers
        confidential_fields = [
            "client_name",
            "project_name",
            "proprietary_spec",
            "custom_rule"
        ]
        return any(field in context for field in confidential_fields)
    
    def _sanitize_context(self, context: dict) -> dict:
        # Remove/anonymize confidential fields
        sanitized = context.copy()
        
        # Replace actual values with placeholders
        if "client_name" in sanitized:
            sanitized["client_name"] = "CLIENT_XXX"
        if "project_name" in sanitized:
            sanitized["project_name"] = "PROJECT_YYY"
        
        return sanitized
```

**LiteLLM Config (with cloud):**
```yaml
# litellm_config.yaml
model_list:
  # Local models (default)
  - model_name: llama3
    litellm_params:
      model: ollama/llama3.1:70b
      api_base: http://localhost:11434
  
  # Cloud models (opt-in only)
  - model_name: gpt4
    litellm_params:
      model: gpt-4-turbo
      api_key: ${OPENAI_API_KEY}
  
  - model_name: gemini
    litellm_params:
      model: gemini-1.5-pro
      api_key: ${GOOGLE_API_KEY}

router_settings:
  default_model: llama3  # Always default to local
  fallback_model: mistral  # Local fallback
```

---

## 🔀 LiteLLM Routing Strategy

### Automatic Routing Based on Task

```python
# backend/app/services/litellm_router.py
from litellm import Router

class SynapseLLMRouter:
    def __init__(self):
        self.router = Router(
            model_list=[
                # Fast local (simple queries)
                {
                    "model_name": "fast",
                    "litellm_params": {
                        "model": "ollama/mistral:7b",
                        "api_base": "http://localhost:11434"
                    }
                },
                # Quality local (complex queries)
                {
                    "model_name": "quality",
                    "litellm_params": {
                        "model": "ollama/llama3.1:70b",
                        "api_base": "http://localhost:11434"
                    }
                },
                # Code-specific
                {
                    "model_name": "code",
                    "litellm_params": {
                        "model": "ollama/codellama:34b",
                        "api_base": "http://localhost:11434"
                    }
                }
            ],
            default_model="quality"
        )
    
    async def route_query(self, query: str, query_type: str):
        # Route based on query type
        routing = {
            "navigation": "fast",      # "Show motors area 210"
            "explanation": "quality",  # "Explain this rule"
            "code_help": "code",       # "Debug this Python"
            "complex": "quality"       # Complex reasoning
        }
        
        model = routing.get(query_type, "quality")
        
        response = await self.router.acompletion(
            model=model,
            messages=[{"role": "user", "content": query}]
        )
        
        return response
```

---

## 📊 AI Use Cases in SYNAPSE

### 1. Chatbot Navigation (Local - Fast)

**Model:** Mistral 7B (fast)

**Examples:**
```
User: "Show me all motors in area 210"
AI: [Queries DB] → Returns 12 motors → Generates response

User: "Go to package IN-P040"
AI: [Navigate to WBS tab] → Selects IN-P040

User: "What's the voltage for Greece project?"
AI: [Queries rules] → "400V (COUNTRY-GR rule priority 30)"
```

**Context Provided:**
- Current user view (FBS/LBS/WBS/etc.)
- Selected items
- Recent actions
- Database schema (for queries)

---

### 2. P&ID Ingestion Assistance (Local - OCR)

**Model:** LLaMA 3.1 70B

**Use Case:** Validate YOLO detections

**Flow:**
```
1. YOLO detects symbol at (x, y) → "PUMP" confidence 92%
2. EasyOCR reads text nearby → "210-PP-0O1" (OCR error: O vs 0)
3. AI validates: "This looks like '210-PP-001' (corrected O→0)"
4. Create asset with corrected tag
```

**Why Local:**
- P&ID contains proprietary project data
- Must stay on server

---

### 3. Documentation Search (Local)

**Model:** LLaMA 3.1 70B + Embeddings

**Setup:**
- Embed all documentation in ChromaDB
- Semantic search via embeddings
- LLM summarizes results

**Example:**
```
User: "How do I create a package?"
AI: 
  1. Searches docs for "package creation"
  2. Finds relevant sections
  3. Summarizes: "To create package: 
     - Go to WBS tab
     - Click 'New Package'
     - Select type (IN-P001, etc.)
     - Assign assets"
```

---

### 4. Rule Explanation (Local)

**Model:** LLaMA 3.1 70B

**Example:**
```
User: "Why was this VFD created?"

AI analyzes rule execution trace:
  "VFD created because:
   1. Motor 210-M-001 has HP=100
   2. Rule 'FIRM: VFDs for Motors >15HP' matched
   3. Condition: HP > 15 ✅
   4. Action: CREATE_CHILD type=VFD
   5. Result: 210-VFD-001 created"
```

---

### 5. Debug Assistance (Local - Code)

**Model:** CodeLlama 34B

**Example:**
```
User: "Why didn't cable generate?"

AI analyzes:
  1. Checks rule execution log
  2. Finds: Motor voltage = NULL
  3. Cable sizing requires voltage
  4. Suggests: "Set motor voltage to 400V (COUNTRY-GR default)"
  5. Offers: [Auto-Fix] button
```

---

## 🔒 Data Confidentiality Tiers

### Tier 0: Public (Any AI)
- Documentation
- Generic examples
- Public tutorials
- Opensource code

### Tier 1: Internal (Local AI Only)
- Project data (tags, specs)
- Custom rules
- P&IDs
- Client information

### Tier 2: Highly Confidential (No AI)
- Passwords
- API keys
- Commercial terms
- Proprietary algorithms

**Implementation:**
```python
# backend/app/models/models.py
class Asset(Base):
    # ...
    confidentiality_level = Column(
        Enum("public", "internal", "confidential"),
        default="internal"
    )

# AI service checks before processing
def can_use_ai(data, ai_provider):
    if data.confidentiality_level == "confidential":
        return False  # No AI
    elif data.confidentiality_level == "internal":
        return ai_provider == "local"  # Local only
    else:
        return True  # Any AI
```

---

## 🐋 Docker Deployment (Updated with AI)

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ... existing services ...
  
  # Ollama (AI runtime)
  ollama:
    image: ollama/ollama:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - synapse_network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  # LiteLLM (AI router)
  litellm:
    image: ghcr.io/berriai/litellm:latest
    depends_on:
      - ollama
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    command: --config /app/config.yaml
    ports:
      - "4000:4000"
    networks:
      - synapse_network
  
  # ChromaDB (embeddings for doc search)
  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - chroma_data:/chroma/chroma
    ports:
      - "8001:8000"
    networks:
      - synapse_network
  
  # OpenWebUI (optional - chat interface)
  openwebui:
    image: ghcr.io/open-webui/open-webui:latest
    depends_on:
      - ollama
    environment:
      - OLLAMA_API_BASE_URL=http://ollama:11434
    ports:
      - "8082:8080"
    volumes:
      - openwebui_data:/app/backend/data
    networks:
      - synapse_network

volumes:
  ollama_data:
  chroma_data:
  openwebui_data:

networks:
  synapse_network:
    driver: bridge
```

---

## 💰 Cost Comparison

### Local AI (Your Setup)
**Hardware:** RTX 3080 Ti (already owned)  
**Software:** Free (Ollama, LiteLLM)  
**Usage Cost:** $0/month  
**Electricity:** ~$20-30/month (GPU running)

**Total:** ~$20-30/month

### Cloud AI (If used)
**OpenAI GPT-4:**
- $0.01 per 1K input tokens
- $0.03 per 1K output tokens
- Avg query: ~2K tokens = $0.08
- 1000 queries/month = $80

**Google Gemini:**
- $0.00125 per 1K tokens (cheaper)
- 1000 queries/month = $2.50

**Recommendation:** 
- Default: Local (free)
- Fallback: Gemini (if needed, cheaper than GPT-4)

---

## 🎯 Recommended AI Architecture

```
USER QUESTION
    ↓
SYNAPSE BACKEND
    ↓
[Confidentiality Check]
    ↓
├─ Confidential? → LOCAL AI ONLY
│   ↓
│   LiteLLM Router
│   ↓
│   ├─ Simple → Mistral 7B (fast)
│   ├─ Complex → LLaMA 3.1 70B (quality)
│   └─ Code → CodeLlama 34B
│   ↓
│   Ollama (RTX 3080 Ti)
│
└─ Public + User Consent? → CLOUD AI (OPTIONAL)
    ↓
    LiteLLM Router
    ↓
    ├─ Gemini 1.5 Pro (cost-effective)
    └─ GPT-4 Turbo (complex reasoning)
```

---

## ✅ Summary

**Your Setup Advantages:**
- ✅ RTX 3080 Ti perfect for YOLO + LLaMA 70B
- ✅ Ollama + LiteLLM already configured
- ✅ 100% local = 100% confidential
- ✅ Zero API costs
- ✅ Cloud fallback available (Gemini/GPT-4)

**Recommendation:**
1. **Default:** Local AI (LLaMA 3.1 70B via Ollama)
2. **Routing:** LiteLLM (fast vs quality models)
3. **Confidentiality:** Strict local-only for project data
4. **Cloud:** Optional Gemini (cheaper) for non-confidential
5. **UI:** Toggle in settings (Enable Cloud AI: Yes/No)

**Cost:** ~$20-30/month (electricity only)

**Best of both worlds: Enterprise privacy + AI capabilities**
