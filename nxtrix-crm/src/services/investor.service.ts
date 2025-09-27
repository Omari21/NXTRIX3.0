import { supabase } from '@/lib/supabase'
import { Investor, BuyBoxCriteria } from '@/types/deal'
import { DealAnalyzer } from '@/lib/deal-analyzer'

export class InvestorService {
  static async createInvestor(investorData: Partial<Investor>): Promise<Investor> {
    const investor = {
      ...investorData,
      created_at: new Date().toISOString()
    }

    const { data, error } = await supabase
      .from('investors')
      .insert([investor])
      .select()
      .single()

    if (error) throw error
    return data
  }

  static async getInvestors(): Promise<Investor[]> {
    const { data, error } = await supabase
      .from('investors')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) throw error
    return data || []
  }

  static async getInvestorById(id: string): Promise<Investor | null> {
    const { data, error } = await supabase
      .from('investors')
      .select('*')
      .eq('id', id)
      .single()

    if (error) throw error
    return data
  }

  static async updateInvestor(id: string, updates: Partial<Investor>): Promise<Investor> {
    const { data, error } = await supabase
      .from('investors')
      .update(updates)
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  }

  static async findMatchingInvestors(deal: any): Promise<Investor[]> {
    const investors = await this.getInvestors()
    
    return investors.filter(investor => {
      if (!investor.notifications_enabled) return false
      return DealAnalyzer.doesDealMatchBuyBox(deal, investor.investment_criteria)
    })
  }

  static async updateBuyBoxCriteria(investorId: string, criteria: BuyBoxCriteria): Promise<void> {
    const { error } = await supabase
      .from('investors')
      .update({ investment_criteria: criteria })
      .eq('id', investorId)

    if (error) throw error
  }
}