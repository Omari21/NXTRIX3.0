import OpenAI from 'openai';

// Initialize OpenAI client only when needed (server-side)
const getOpenAIClient = () => {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error('OpenAI API key is not configured');
  }
  
  return new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });
};

export interface AIAnalysisResult {
  overall_score: number;
  financial_score: number;
  market_score: number;
  risk_score: number;
  time_sensitivity_score: number;
  factors: string[];
  recommendations: string[];
  confidence: number;
  reasoning: string;
}

export interface DealAnalysisInput {
  id: string;
  title: string;
  property_address: string;
  purchase_price: number;
  after_repair_value: number;
  repair_costs: number;
  monthly_rent?: number;
  monthly_expenses?: number;
  deal_type: 'flip' | 'rental' | 'wholesale' | 'brrrr';
  property_details?: any;
  market_analysis?: any;
}

export class AIAnalysisService {
  /**
   * Analyze a real estate deal using OpenAI GPT-4
   */
  static async analyzeDeal(deal: DealAnalysisInput): Promise<AIAnalysisResult> {
    try {
      const openai = getOpenAIClient();
      const prompt = this.buildAnalysisPrompt(deal);
      
      const completion = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are an expert real estate investment analyst with 20+ years of experience in creative real estate deals, fix & flips, rentals, BRRRR strategy, and wholesale deals. Analyze deals with precision and provide actionable insights."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: 0.3, // Lower temperature for more consistent analysis
        max_tokens: 1500,
        response_format: { type: "json_object" }
      });

      const response = completion.choices[0]?.message?.content;
      if (!response) {
        throw new Error('No response from OpenAI');
      }

      const analysis = JSON.parse(response) as AIAnalysisResult;
      
      // Save analysis to database
      await this.saveAnalysisToDatabase(deal.id, analysis, {
        model: "gpt-4",
        prompt_used: prompt,
        tokens_used: completion.usage?.total_tokens || 0,
        cost_cents: this.calculateCost(completion.usage?.total_tokens || 0)
      });

      return analysis;
      
    } catch (error) {
      console.error('AI Analysis Error:', error);
      throw new Error(`AI analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Build comprehensive analysis prompt
   */
  private static buildAnalysisPrompt(deal: DealAnalysisInput): string {
    const { 
      title, 
      property_address, 
      purchase_price, 
      after_repair_value, 
      repair_costs, 
      monthly_rent, 
      monthly_expenses, 
      deal_type 
    } = deal;

    // Calculate basic metrics
    const profit_potential = after_repair_value - purchase_price - repair_costs;
    const roi = purchase_price > 0 ? ((profit_potential / purchase_price) * 100) : 0;
    const cash_flow = (monthly_rent || 0) - (monthly_expenses || 0);
    const cap_rate = monthly_rent && purchase_price > 0 ? 
      (((monthly_rent * 12) - (monthly_expenses || 0) * 12) / purchase_price) * 100 : 0;

    return `
Analyze this ${deal_type.toUpperCase()} real estate deal and provide a comprehensive investment analysis:

**DEAL OVERVIEW:**
- Property: ${title}
- Address: ${property_address}
- Deal Type: ${deal_type}

**FINANCIAL DETAILS:**
- Purchase Price: $${purchase_price.toLocaleString()}
- After Repair Value (ARV): $${after_repair_value.toLocaleString()}
- Repair Costs: $${repair_costs.toLocaleString()}
- Monthly Rent: $${monthly_rent || 'N/A'}
- Monthly Expenses: $${monthly_expenses || 'N/A'}

**CALCULATED METRICS:**
- Profit Potential: $${profit_potential.toLocaleString()}
- ROI: ${roi.toFixed(2)}%
- Monthly Cash Flow: $${cash_flow.toFixed(2)}
- Cap Rate: ${cap_rate.toFixed(2)}%

**ANALYSIS REQUIREMENTS:**
1. **Financial Score (0-100)**: Evaluate profit margins, ROI, cash flow potential
2. **Market Score (0-100)**: Assess location, comparable sales, market trends
3. **Risk Score (0-100)**: Identify potential risks, market volatility, exit strategies
4. **Time Sensitivity Score (0-100)**: Urgency level, market timing, opportunity window
5. **Overall Score (0-100)**: Weighted average considering all factors

**EVALUATION CRITERIA:**
- ${deal_type === 'flip' ? 'Focus on profit margins, repair costs accuracy, market demand for flips' : ''}
- ${deal_type === 'rental' ? 'Analyze cash flow, cap rate, tenant demand, long-term appreciation' : ''}
- ${deal_type === 'wholesale' ? 'Evaluate spread potential, buyer demand, quick exit viability' : ''}
- ${deal_type === 'brrrr' ? 'Assess refinance potential, rental income, equity capture' : ''}

**REQUIRED JSON RESPONSE FORMAT:**
{
  "overall_score": number (0-100),
  "financial_score": number (0-100),
  "market_score": number (0-100), 
  "risk_score": number (0-100),
  "time_sensitivity_score": number (0-100),
  "factors": ["key positive factors", "key concerns"],
  "recommendations": ["specific actionable recommendations"],
  "confidence": number (0-100),
  "reasoning": "detailed explanation of scoring rationale"
}

Provide specific, actionable insights based on the deal type and financial metrics.`;
  }

  /**
   * Quick deal scoring without full AI analysis (for bulk operations)
   */
  static async quickScore(deal: DealAnalysisInput): Promise<number> {
    const prompt = `
Score this ${deal.deal_type} deal from 0-100 based on these metrics:
- Purchase: $${deal.purchase_price.toLocaleString()}
- ARV: $${deal.after_repair_value.toLocaleString()}
- Repairs: $${deal.repair_costs.toLocaleString()}
- ROI: ${((deal.after_repair_value - deal.purchase_price - deal.repair_costs) / deal.purchase_price * 100).toFixed(2)}%

Return only the numerical score (0-100) with no explanation.`;

    try {
      const openai = getOpenAIClient();
      const completion = await openai.chat.completions.create({
        model: "gpt-3.5-turbo",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.1,
        max_tokens: 10
      });

      const score = parseInt(completion.choices[0]?.message?.content || '0');
      return Math.min(100, Math.max(0, score));
      
    } catch (error) {
      console.error('Quick scoring error:', error);
      // Fallback to basic algorithmic scoring
      return this.fallbackScoring(deal);
    }
  }

  /**
   * Fallback scoring algorithm if AI fails
   */
  private static fallbackScoring(deal: DealAnalysisInput): number {
    const profit = deal.after_repair_value - deal.purchase_price - deal.repair_costs;
    const roi = (profit / deal.purchase_price) * 100;
    
    let score = 50; // Base score
    
    // ROI scoring
    if (roi >= 30) score += 25;
    else if (roi >= 20) score += 15;
    else if (roi >= 10) score += 5;
    else if (roi < 0) score -= 20;
    
    // Repair cost ratio
    const repairRatio = deal.repair_costs / deal.purchase_price;
    if (repairRatio <= 0.1) score += 15;
    else if (repairRatio <= 0.2) score += 10;
    else if (repairRatio > 0.5) score -= 15;
    
    // Deal type bonuses
    if (deal.deal_type === 'rental' && deal.monthly_rent) {
      const capRate = ((deal.monthly_rent * 12) / deal.purchase_price) * 100;
      if (capRate >= 10) score += 10;
    }
    
    return Math.min(100, Math.max(0, score));
  }

  /**
   * Save AI analysis to database
   */
  private static async saveAnalysisToDatabase(
    dealId: string, 
    analysis: AIAnalysisResult,
    metadata: {
      model: string;
      prompt_used: string;
      tokens_used: number;
      cost_cents: number;
    }
  ) {
    // This will be implemented with your Supabase client
    const { supabase } = await import('@/lib/supabase');
    
    try {
      await supabase.from('ai_deal_analysis').insert({
        deal_id: dealId,
        analysis_type: 'scoring',
        ai_model: metadata.model,
        prompt_used: metadata.prompt_used,
        analysis_result: analysis,
        confidence_score: analysis.confidence,
        tokens_used: metadata.tokens_used,
        cost_cents: metadata.cost_cents
      });
    } catch (error) {
      console.error('Failed to save AI analysis:', error);
    }
  }

  /**
   * Calculate OpenAI API cost in cents
   */
  private static calculateCost(tokens: number): number {
    // GPT-4 pricing (as of 2024): $0.03/1K input tokens, $0.06/1K output tokens
    // Simplified calculation assuming 50/50 split
    const costPer1K = 0.045; // Average
    return Math.round((tokens / 1000) * costPer1K * 100);
  }

  /**
   * Analyze market trends for a location
   */
  static async analyzeMarket(address: string, zipCode?: string): Promise<any> {
    const prompt = `
Analyze the real estate market for: ${address}${zipCode ? ` (ZIP: ${zipCode})` : ''}

Provide insights on:
1. Current market trends
2. Appreciation potential  
3. Rental demand
4. Investment risks
5. Comparable sales activity

Return detailed market analysis in JSON format.`;

    try {
      const completion = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.3,
        max_tokens: 800,
        response_format: { type: "json_object" }
      });

      return JSON.parse(completion.choices[0]?.message?.content || '{}');
    } catch (error) {
      console.error('Market analysis error:', error);
      return null;
    }
  }
}