import { NextRequest, NextResponse } from 'next/server'
import { DealService } from '@/services/deal.service'
import { AIAnalysisService } from '@/services/ai-analysis.service'

export async function POST(request: NextRequest) {
  try {
    const { dealId, analysisType = 'full' } = await request.json()

    if (!dealId) {
      return NextResponse.json({ error: 'Deal ID is required' }, { status: 400 })
    }

    if (analysisType === 'quick') {
      // Quick AI scoring
      const deal = await DealService.getDealById(dealId)
      if (!deal) {
        return NextResponse.json({ error: 'Deal not found' }, { status: 404 })
      }

      const score = await AIAnalysisService.quickScore({
        id: deal.id,
        title: deal.title,
        property_address: deal.property_address,
        purchase_price: deal.purchase_price,
        after_repair_value: deal.after_repair_value,
        repair_costs: deal.repair_costs,
        monthly_rent: deal.monthly_rent,
        monthly_expenses: deal.monthly_expenses,
        deal_type: deal.deal_type
      })

      // Update deal score
      await DealService.updateDeal(dealId, { deal_score: score })

      return NextResponse.json({ 
        success: true, 
        score,
        message: 'Quick AI analysis completed' 
      })
    } else {
      // Full AI analysis
      await DealService.reAnalyzeDeal(dealId)
      
      const analysis = await DealService.getAIAnalysis(dealId)
      const scores = await DealService.getDealScores(dealId)

      return NextResponse.json({ 
        success: true, 
        analysis,
        scores,
        message: 'Full AI analysis completed' 
      })
    }

  } catch (error) {
    console.error('AI Analysis API Error:', error)
    
    return NextResponse.json({ 
      error: 'AI analysis failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const dealId = searchParams.get('dealId')

    if (!dealId) {
      return NextResponse.json({ error: 'Deal ID is required' }, { status: 400 })
    }

    const analysis = await DealService.getAIAnalysis(dealId)
    const scores = await DealService.getDealScores(dealId)

    return NextResponse.json({ 
      success: true,
      analysis,
      scores
    })

  } catch (error) {
    console.error('Get AI Analysis Error:', error)
    
    return NextResponse.json({ 
      error: 'Failed to retrieve AI analysis',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}