export interface Deal {
  id: string
  title: string
  property_address: string
  purchase_price: number
  after_repair_value: number
  repair_costs: number
  monthly_rent: number
  monthly_expenses: number
  deal_type: 'flip' | 'rental' | 'wholesale' | 'brrrr'
  status: 'analyzing' | 'approved' | 'rejected' | 'pending'
  roi: number
  cap_rate?: number
  cash_on_cash_return?: number
  profit_potential: number
  deal_score: number
  created_at: string
  updated_at: string
  created_by: string
  assigned_to?: string
  property_details?: PropertyDetails
  financial_analysis?: FinancialAnalysis
  market_analysis?: MarketAnalysis
}

export interface PropertyDetails {
  bedrooms: number
  bathrooms: number
  square_feet: number
  lot_size: number
  year_built: number
  property_type: string
  condition: 'excellent' | 'good' | 'fair' | 'poor'
  neighborhood: string
  school_district?: string
  nearby_amenities: string[]
  photos: string[]
}

export interface FinancialAnalysis {
  cash_needed: number
  down_payment: number
  closing_costs: number
  monthly_cash_flow: number
  total_investment: number
  break_even_months: number
  five_year_projection: number
  ten_year_projection: number
}

export interface MarketAnalysis {
  comparable_sales: ComparableSale[]
  market_trends: MarketTrend[]
  appreciation_rate: number
  days_on_market: number
  price_per_sqft: number
}

export interface ComparableSale {
  address: string
  sale_price: number
  sale_date: string
  square_feet: number
  price_per_sqft: number
  distance_miles: number
}

export interface MarketTrend {
  period: string
  average_price: number
  inventory_level: number
  absorption_rate: number
}

export interface Investor {
  id: string
  name: string
  email: string
  phone: string
  investment_criteria: BuyBoxCriteria
  notifications_enabled: boolean
  preferred_contact_method: 'email' | 'sms' | 'both'
  investment_budget: {
    min_amount: number
    max_amount: number
  }
  experience_level: 'beginner' | 'intermediate' | 'expert'
  created_at: string
}

export interface BuyBoxCriteria {
  max_purchase_price: number
  min_roi: number
  min_cap_rate?: number
  min_cash_flow?: number
  preferred_locations: string[]
  property_types: string[]
  max_repair_costs: number
  deal_types: Deal['deal_type'][]
}

export interface DealScore {
  overall_score: number
  financial_score: number
  market_score: number
  risk_score: number
  time_sensitivity_score: number
  factors: ScoreFactor[]
}

export interface ScoreFactor {
  name: string
  weight: number
  score: number
  explanation: string
}