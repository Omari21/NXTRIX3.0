# NXTRIX CRM - Real Estate Deal Management Platform

🏢 **Professional Real Estate CRM built with Streamlit and Supabase**

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Omari21/NXTRIX3.0.git
cd NXTRIX3.0
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
   - Add your Supabase credentials

4. **Run the application:**
```bash
streamlit run streamlit_app.py
```

## 🎯 Core Features

### 🔐 **User Authentication**
- Secure user registration and login
- Password hashing with bcrypt
- Session management

### 💼 **Deal Management**
- Add, edit, view, and delete deals
- Deal filtering and search
- Status tracking (Active, Pending, Closed, Cancelled)
- Property value and investor tracking

### 📊 **Analytics Dashboard**
- Total portfolio value tracking
- Deal count metrics
- Average deal size analysis
- Visual charts and graphs

### � **Investor Management**
- Investor portfolio summaries
- Deal count per investor
- Investment value tracking
- Contact information management
- 🔒 Enterprise-grade security
- ⚡ 100% efficiency optimizations
- 🌐 Supabase cloud database integration

### Tech Stack:
- **Frontend**: Streamlit
- **Backend**: Python, Supabase
- **AI**: OpenAI GPT integration
- **Analytics**: Plotly, Pandas, NumPy

## 🛠️ Setup for Streamlit Cloud

### 1. Repository Settings
- **Main file**: `streamlit_app.py`
- **Python version**: 3.9+
- **Dependencies**: `requirements.txt`

### 2. Required Secrets
Add these to your Streamlit Cloud secrets:

```toml
[SUPABASE]
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_anon_key"

[OPENAI]
OPENAI_API_KEY = "your_openai_api_key"
```

### 3. Deployment URL
- Recommended: `https://nxtrix-crm.streamlit.app`

## 📁 File Structure
```
├── streamlit_app.py              # Main application
├── requirements.txt              # Dependencies
├── .streamlit/
│   └── secrets.toml.example     # Secrets template
├── ai_prediction_engine.py       # AI analytics
├── auto_optimization_loader.py   # Performance system
├── database_service.py           # Database wrapper
├── performance_optimizer.py      # Core optimizations
└── [other optimization modules]   # Additional features
```

## 🎯 Core Modules
- **CRM Engine**: Complete deal and contact management
- **AI Analytics**: Predictive market analysis
- **Performance System**: 11 optimization modules for 100% efficiency
- **Security Suite**: Enterprise-grade protection
- **Database Integration**: Seamless Supabase connectivity

## 🚀 Getting Started
1. Deploy to Streamlit Cloud with this repository
2. Add your API keys in Streamlit Cloud secrets
3. Access your live CRM at the deployed URL
4. Start managing deals and contacts immediately!

---

**Built by NXTRIX** - Enterprise CRM Solutions