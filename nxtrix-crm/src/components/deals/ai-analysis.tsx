'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Brain, TrendingUp, AlertTriangle, Clock, DollarSign, Lightbulb, RefreshCw } from 'lucide-react'

interface AIAnalysisProps {
  dealId: string
  onAnalysisComplete?: () => void
}

interface AIAnalysisResult {
  overall_score: number
  financial_score: number
  market_score: number
  risk_score: number
  time_sensitivity_score: number
  factors: string[]
  recommendations: string[]
  confidence: number
  reasoning: string
}

interface AnalysisData {
  analysis: {
    analysis_result: AIAnalysisResult
    confidence_score: number
    tokens_used: number
    cost_cents: number
    created_at: string
  }
  scores: {
    overall_score: number
    financial_score: number
    market_score: number
    risk_score: number
    time_sensitivity_score: number
    factors: string[]
    ai_analysis: {
      recommendations: string[]
      reasoning: string
      confidence: number
    }
  }
}

export function AIAnalysisComponent({ dealId, onAnalysisComplete }: AIAnalysisProps) {
  const [loading, setLoading] = useState(false)
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runAnalysis = async (type: 'quick' | 'full' = 'full') => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/ai/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dealId, analysisType: type })
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.details || result.error)
      }

      if (type === 'full') {
        setAnalysisData(result)
      }

      onAnalysisComplete?.()
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const loadExistingAnalysis = async () => {
    try {
      const response = await fetch(`/api/ai/analyze?dealId=${dealId}`)
      const result = await response.json()

      if (response.ok && result.analysis) {
        setAnalysisData(result)
      }
    } catch (err) {
      console.error('Failed to load existing analysis:', err)
    }
  }

  // Load existing analysis on mount
  useEffect(() => {
    loadExistingAnalysis()
  }, [dealId])

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBadgeVariant = (score: number) => {
    if (score >= 80) return 'default'
    if (score >= 60) return 'secondary'
    return 'destructive'
  }

  return (
    <div className="space-y-6">
      {/* Analysis Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            AI Deal Analysis
          </CardTitle>
          <CardDescription>
            Get intelligent insights and scoring powered by OpenAI GPT-4
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Button 
              onClick={() => runAnalysis('quick')} 
              disabled={loading}
              variant="outline"
            >
              {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : null}
              Quick Score
            </Button>
            <Button 
              onClick={() => runAnalysis('full')} 
              disabled={loading}
            >
              {loading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : null}
              Full Analysis
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Analysis Results */}
      {analysisData && (
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="detailed">Detailed Scores</TabsTrigger>
            <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
            <TabsTrigger value="insights">AI Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            {/* Overall Score */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Overall Deal Score</span>
                  <Badge variant={getScoreBadgeVariant(analysisData.scores.overall_score)}>
                    {analysisData.scores.overall_score}/100
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Progress 
                  value={analysisData.scores.overall_score} 
                  className="h-3"
                />
                <p className="text-sm text-muted-foreground mt-2">
                  Confidence: {analysisData.scores.ai_analysis.confidence}%
                </p>
              </CardContent>
            </Card>

            {/* Score Breakdown */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Financial</span>
                  </div>
                  <div className={`text-2xl font-bold ${getScoreColor(analysisData.scores.financial_score)}`}>
                    {analysisData.scores.financial_score}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">Market</span>
                  </div>
                  <div className={`text-2xl font-bold ${getScoreColor(analysisData.scores.market_score)}`}>
                    {analysisData.scores.market_score}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <span className="text-sm font-medium">Risk</span>
                  </div>
                  <div className={`text-2xl font-bold ${getScoreColor(analysisData.scores.risk_score)}`}>
                    {analysisData.scores.risk_score}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-orange-600" />
                    <span className="text-sm font-medium">Timing</span>
                  </div>
                  <div className={`text-2xl font-bold ${getScoreColor(analysisData.scores.time_sensitivity_score)}`}>
                    {analysisData.scores.time_sensitivity_score}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="detailed" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Detailed Score Breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { name: 'Financial Score', score: analysisData.scores.financial_score, icon: DollarSign },
                  { name: 'Market Score', score: analysisData.scores.market_score, icon: TrendingUp },
                  { name: 'Risk Score', score: analysisData.scores.risk_score, icon: AlertTriangle },
                  { name: 'Time Sensitivity', score: analysisData.scores.time_sensitivity_score, icon: Clock }
                ].map((item) => (
                  <div key={item.name} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <item.icon className="h-4 w-4" />
                        <span className="font-medium">{item.name}</span>
                      </div>
                      <span className={`font-bold ${getScoreColor(item.score)}`}>
                        {item.score}/100
                      </span>
                    </div>
                    <Progress value={item.score} className="h-2" />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="recommendations" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  AI Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysisData.scores.ai_analysis.recommendations.map((rec, index) => (
                    <Alert key={index}>
                      <AlertDescription>{rec}</AlertDescription>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Key Factors */}
            <Card>
              <CardHeader>
                <CardTitle>Key Factors</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {analysisData.scores.factors.map((factor, index) => (
                    <Badge key={index} variant="outline">
                      {factor}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="insights" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>AI Analysis Reasoning</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed">
                  {analysisData.scores.ai_analysis.reasoning}
                </p>
              </CardContent>
            </Card>

            {/* Analysis Metadata */}
            {analysisData.analysis && (
              <Card>
                <CardHeader>
                  <CardTitle>Analysis Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Tokens Used:</span>
                    <span>{analysisData.analysis.tokens_used}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Cost:</span>
                    <span>${(analysisData.analysis.cost_cents / 100).toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Analyzed:</span>
                    <span>{new Date(analysisData.analysis.created_at).toLocaleString()}</span>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}