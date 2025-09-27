import { supabase } from '@/lib/supabase'
import { Deal } from '@/types/deal'
import { DealAnalyzer } from '@/lib/deal-analyzer'
import { AIAnalysisService, DealAnalysisInput } from './ai-analysis.service'

export class DealService {
  static async createDeal(dealData: Partial<Deal>, useAI: boolean = true): Promise<Deal> {
    // Calculate basic financial metrics
    const roi = DealAnalyzer.calculateROI(dealData as Deal)
    let dealScore = DealAnalyzer.calculateDealScore({ ...dealData, roi } as Deal).overall_score
    
    const deal = {
      ...dealData,
      roi,
      deal_score: dealScore,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    // Create deal in database first
    const { data, error } = await supabase
      .from('deals')
      .insert([deal])
      .select()
      .single()

    if (error) throw error

    // Run AI analysis if enabled and deal is created successfully
    if (useAI && data) {
      try {
        await this.runAIAnalysis(data.id, data as Deal)
      } catch (aiError) {
        console.warn('AI analysis failed, using fallback scoring:', aiError)
      }
    }

    return data
  }

  static async getDeals(filters?: {
    status?: string
    deal_type?: string
    min_score?: number
    assigned_to?: string
  }): Promise<Deal[]> {
    let query = supabase.from('deals').select('*')

    if (filters?.status) {
      query = query.eq('status', filters.status)
    }
    if (filters?.deal_type) {
      query = query.eq('deal_type', filters.deal_type)
    }
    if (filters?.min_score) {
      query = query.gte('deal_score', filters.min_score)
    }
    if (filters?.assigned_to) {
      query = query.eq('assigned_to', filters.assigned_to)
    }

    const { data, error } = await query.order('deal_score', { ascending: false })
    
    if (error) throw error
    return data || []
  }

  static async getDealById(id: string): Promise<Deal | null> {
    const { data, error } = await supabase
      .from('deals')
      .select('*')
      .eq('id', id)
      .single()

    if (error) throw error
    return data
  }

  static async updateDeal(id: string, updates: Partial<Deal>): Promise<Deal> {
    // Recalculate metrics if financial data changed
    if (updates.purchase_price || updates.repair_costs || updates.monthly_rent || updates.monthly_expenses) {
      const currentDeal = await this.getDealById(id)
      if (currentDeal) {
        const updatedDeal = { ...currentDeal, ...updates }
        updates.roi = DealAnalyzer.calculateROI(updatedDeal)
        updates.deal_score = DealAnalyzer.calculateDealScore(updatedDeal).overall_score
      }
    }

    updates.updated_at = new Date().toISOString()

    const { data, error } = await supabase
      .from('deals')
      .update(updates)
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  }

  static async deleteDeal(id: string): Promise<void> {
    const { error } = await supabase
      .from('deals')
      .delete()
      .eq('id', id)

    if (error) throw error
  }

  static async getHighValueDeals(minScore: number = 80): Promise<Deal[]> {
    return this.getDeals({ min_score: minScore })
  }

  static async getDealsByType(dealType: Deal['deal_type']): Promise<Deal[]> {
    return this.getDeals({ deal_type: dealType })
  }

  /**
   * Run AI analysis on a deal and update the database
   */
  static async runAIAnalysis(dealId: string, deal: Deal): Promise<void> {
    try {
      const analysisInput: DealAnalysisInput = {
        id: dealId,
        title: deal.title,
        property_address: deal.property_address,
        purchase_price: deal.purchase_price,
        after_repair_value: deal.after_repair_value,
        repair_costs: deal.repair_costs,
        monthly_rent: deal.monthly_rent,
        monthly_expenses: deal.monthly_expenses,
        deal_type: deal.deal_type,
        property_details: deal.property_details,
        market_analysis: deal.market_analysis
      }

      const analysis = await AIAnalysisService.analyzeDeal(analysisInput)

      // Update deal with AI scores
      await supabase
        .from('deals')
        .update({
          deal_score: analysis.overall_score,
          updated_at: new Date().toISOString()
        })
        .eq('id', dealId)

      // Save detailed scores to deal_scores table
      await supabase
        .from('deal_scores')
        .insert({
          deal_id: dealId,
          overall_score: analysis.overall_score,
          financial_score: analysis.financial_score,
          market_score: analysis.market_score,
          risk_score: analysis.risk_score,
          time_sensitivity_score: analysis.time_sensitivity_score,
          factors: analysis.factors,
          ai_analysis: {
            recommendations: analysis.recommendations,
            reasoning: analysis.reasoning,
            confidence: analysis.confidence
          }
        })

    } catch (error) {
      console.error('AI analysis failed for deal:', dealId, error)
      throw error
    }
  }

  /**
   * Re-analyze an existing deal with AI
   */
  static async reAnalyzeDeal(dealId: string): Promise<void> {
    const deal = await this.getDealById(dealId)
    if (!deal) throw new Error('Deal not found')
    
    await this.runAIAnalysis(dealId, deal)
  }

  /**
   * Get AI analysis results for a deal
   */
  static async getAIAnalysis(dealId: string) {
    const { data, error } = await supabase
      .from('ai_deal_analysis')
      .select('*')
      .eq('deal_id', dealId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    if (error && error.code !== 'PGRST116') throw error // PGRST116 = no rows
    return data
  }

  /**
   * Get detailed deal scores
   */
  static async getDealScores(dealId: string) {
    const { data, error } = await supabase
      .from('deal_scores')
      .select('*')
      .eq('deal_id', dealId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    if (error && error.code !== 'PGRST116') throw error
    return data
  }

  /**
   * Bulk AI analysis for multiple deals
   */
  static async bulkAnalyzeDeals(dealIds: string[]): Promise<void> {
    const promises = dealIds.map(async (dealId) => {
      try {
        await this.reAnalyzeDeal(dealId)
      } catch (error) {
        console.error(`Failed to analyze deal ${dealId}:`, error)
      }
    })

    await Promise.allSettled(promises)
  }
}