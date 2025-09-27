import { Deal, DealScore, ScoreFactor } from '@/types/deal'

export class DealAnalyzer {
  static calculateROI(deal: Deal): number {
    const totalInvestment = deal.purchase_price + deal.repair_costs
    const annualCashFlow = (deal.monthly_rent - deal.monthly_expenses) * 12
    
    if (deal.deal_type === 'flip') {
      const profit = deal.after_repair_value - totalInvestment
      return (profit / totalInvestment) * 100
    } else {
      return (annualCashFlow / totalInvestment) * 100
    }
  }

  static calculateCapRate(deal: Deal): number {
    const netOperatingIncome = (deal.monthly_rent - deal.monthly_expenses) * 12
    return (netOperatingIncome / deal.after_repair_value) * 100
  }

  static calculateCashOnCashReturn(deal: Deal, downPayment: number): number {
    const annualCashFlow = (deal.monthly_rent - deal.monthly_expenses) * 12
    return (annualCashFlow / downPayment) * 100
  }

  static calculateDealScore(deal: Deal): DealScore {
    const factors: ScoreFactor[] = []
    
    // Financial Score (40% weight)
    const roiScore = Math.min(deal.roi / 20 * 100, 100) // 20% ROI = perfect score
    factors.push({
      name: 'ROI Potential',
      weight: 0.25,
      score: roiScore,
      explanation: `ROI of ${deal.roi.toFixed(1)}% ${roiScore >= 80 ? 'is excellent' : roiScore >= 60 ? 'is good' : 'needs improvement'}`
    })

    const profitScore = Math.min((deal.profit_potential / 50000) * 100, 100) // $50k profit = perfect
    factors.push({
      name: 'Profit Potential',
      weight: 0.15,
      score: profitScore,
      explanation: `Projected profit of $${deal.profit_potential.toLocaleString()}`
    })

    // Market Score (30% weight)
    const marketScore = this.calculateMarketScore(deal)
    factors.push({
      name: 'Market Conditions',
      weight: 0.30,
      score: marketScore,
      explanation: 'Based on comparable sales and market trends'
    })

    // Risk Score (20% weight)
    const riskScore = this.calculateRiskScore(deal)
    factors.push({
      name: 'Risk Assessment',
      weight: 0.20,
      score: riskScore,
      explanation: 'Property condition, location, and market stability'
    })

    // Time Sensitivity (10% weight)
    const timeSensitivityScore = this.calculateTimeSensitivityScore(deal)
    factors.push({
      name: 'Time Sensitivity',
      weight: 0.10,
      score: timeSensitivityScore,
      explanation: 'Deal availability and competition level'
    })

    // Calculate weighted overall score
    const overallScore = factors.reduce((total, factor) => {
      return total + (factor.score * factor.weight)
    }, 0)

    return {
      overall_score: Math.round(overallScore),
      financial_score: Math.round((roiScore * 0.625 + profitScore * 0.375)),
      market_score: Math.round(marketScore),
      risk_score: Math.round(riskScore),
      time_sensitivity_score: Math.round(timeSensitivityScore),
      factors
    }
  }

  private static calculateMarketScore(deal: Deal): number {
    // Simplified market scoring - would integrate with ATTOM Data API
    let score = 70 // Base score
    
    // Adjust based on deal type
    if (deal.deal_type === 'rental') {
      const capRate = this.calculateCapRate(deal)
      if (capRate > 8) score += 20
      else if (capRate > 6) score += 10
    }
    
    return Math.min(score, 100)
  }

  private static calculateRiskScore(deal: Deal): number {
    let score = 80 // Base score (lower is riskier)
    
    // Adjust based on repair costs
    const repairRatio = deal.repair_costs / deal.purchase_price
    if (repairRatio > 0.3) score -= 30
    else if (repairRatio > 0.2) score -= 20
    else if (repairRatio > 0.1) score -= 10
    
    return Math.max(score, 0)
  }

  private static calculateTimeSensitivityScore(deal: Deal): number {
    // This would integrate with market data for competition analysis
    return 75 // Base score for now
  }

  static doesDealMatchBuyBox(deal: Deal, buyBox: any): boolean {
    if (deal.purchase_price > buyBox.max_purchase_price) return false
    if (deal.roi < buyBox.min_roi) return false
    if (buyBox.min_cap_rate && deal.deal_type === 'rental') {
      const capRate = this.calculateCapRate(deal)
      if (capRate < buyBox.min_cap_rate) return false
    }
    if (deal.repair_costs > buyBox.max_repair_costs) return false
    if (!buyBox.deal_types.includes(deal.deal_type)) return false
    
    return true
  }
}