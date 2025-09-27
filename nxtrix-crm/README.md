# NxTrix Deal Analyzer CRM 🏢

**Enterprise-Level Real Estate Deal Analysis & Investment Matching Platform**

A comprehensive CRM built for creative real estate professionals to analyze deals, track portfolios, score investments, and automatically match high-ROI opportunities with qualified investors.

## 🌟 **Key Features**

### **Phase 1: Core Foundation** ✅
- **Next.js 15** with TypeScript & Tailwind CSS
- **Supabase** integration for authentication & database
- **Stripe** for payments & subscriptions  
- **Real-time deal analysis** with automated ROI calculations
- **Deal scoring algorithm** (0-100 scale)
- **Professional dashboard** with key metrics

### **Phase 2: Advanced Analytics** 🚧
- **AI-powered deal scoring** using OpenAI GPT
- **Market analysis** integration with ATTOM Data API
- **Portfolio tracking** and performance metrics
- **Automated investor notifications** via Twilio SMS
- **BuyBox criteria matching**

### **Phase 3: Enterprise Features** 📋
- **Role-based access control** (Admin, Analyst, Investor, Agent)
- **Advanced reporting** and data visualization
- **Mobile optimization**
- **API integrations** for MLS and market data
- **White-label options**

## 🏗️ **Project Structure**

```
nxtrix-crm/
├── src/
│   ├── app/                    # Next.js App Router pages
│   ├── components/
│   │   ├── deals/             # Deal management components
│   │   ├── ui/                # Reusable UI components
│   │   └── ...
│   ├── lib/                   # Utilities and configurations
│   ├── services/              # API services and business logic
│   ├── types/                 # TypeScript type definitions
│   └── ...
├── database/
│   └── schema.sql             # Supabase database schema
├── .env.local                 # Environment variables
└── ...
```

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 18+ and npm
- Supabase account (database & auth)
- Stripe account (payments)
- OpenAI API key (AI features)
- Twilio account (SMS notifications)
- ATTOM Data API key (real estate data)

### **Installation**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd nxtrix-crm
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   Copy `.env.local` and configure with your API keys:
   
   ```bash
   # Supabase
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

   # Stripe
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_public_key
   STRIPE_SECRET_KEY=your_stripe_secret_key

   # OpenAI
   OPENAI_API_KEY=your_openai_api_key

   # Twilio
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_phone

   # ATTOM Data
   ATTOM_API_KEY=your_attom_api_key
   ```

4. **Set up the database:**
   - Run the SQL schema in your Supabase dashboard:
   ```bash
   # Copy contents of database/schema.sql to Supabase SQL Editor
   ```

5. **Start the development server:**
   ```bash
   npm run dev
   ```

6. **Open your browser:**
   Navigate to `http://localhost:3000`
