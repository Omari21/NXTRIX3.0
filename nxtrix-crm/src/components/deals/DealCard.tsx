import { Deal } from '@/types/deal'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MapPin, DollarSign, TrendingUp, Star, Clock, Edit, Brain, Eye } from 'lucide-react'
import { useState } from 'react'
import { AIAnalysisComponent } from './ai-analysis'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'

interface DealCardProps {
  deal: Deal
  onUpdate: () => void
}

export default function DealCard({ deal, onUpdate }: DealCardProps) {
  const [showAnalysis, setShowAnalysis] = useState(false)

  const getStatusColor = (status: Deal['status']) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-blue-100 text-blue-800'
    }
  }

  const getDealTypeColor = (type: Deal['deal_type']) => {
    switch (type) {
      case 'flip': return 'bg-purple-100 text-purple-800'
      case 'rental': return 'bg-green-100 text-green-800'
      case 'wholesale': return 'bg-orange-100 text-orange-800'
      case 'brrrr': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardHeader className="pb-4">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-900 mb-2">
              {deal.title}
            </CardTitle>
            <div className="flex items-center text-sm text-gray-600 mb-2">
              <MapPin className="w-4 h-4 mr-1" />
              {deal.property_address}
            </div>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <Badge className={getStatusColor(deal.status)}>
              {deal.status}
            </Badge>
            <Badge className={getDealTypeColor(deal.deal_type)}>
              {deal.deal_type.toUpperCase()}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Financial Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center">
            <DollarSign className="w-4 h-4 text-blue-600 mr-2" />
            <div>
              <p className="text-xs text-gray-600">Purchase Price</p>
              <p className="font-semibold">${deal.purchase_price.toLocaleString()}</p>
            </div>
          </div>
          <div className="flex items-center">
            <TrendingUp className="w-4 h-4 text-green-600 mr-2" />
            <div>
              <p className="text-xs text-gray-600">ROI</p>
              <p className="font-semibold text-green-600">{deal.roi.toFixed(1)}%</p>
            </div>
          </div>
        </div>

        {/* Deal Score */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Star className="w-4 h-4 text-yellow-500 mr-2" />
            <span className="text-sm text-gray-600">Deal Score</span>
          </div>
          <span className={`text-xl font-bold ${getScoreColor(deal.deal_score)}`}>
            {deal.deal_score}/100
          </span>
        </div>

        {/* Profit Potential */}
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Profit Potential</span>
            <span className="text-lg font-bold text-green-600">
              ${deal.profit_potential.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2 pt-2">
          <Button variant="outline" size="sm" className="flex-1">
            <Edit className="w-4 h-4 mr-1" />
            Edit
          </Button>
          
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Brain className="w-4 h-4 mr-1" />
                AI Analysis
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>AI Analysis - {deal.title}</DialogTitle>
              </DialogHeader>
              <AIAnalysisComponent 
                dealId={deal.id} 
                onAnalysisComplete={onUpdate}
              />
            </DialogContent>
          </Dialog>

          <Button size="sm" className="flex-1">
            <Eye className="w-4 h-4 mr-1" />
            Details
          </Button>
        </div>

        {/* Time Info */}
        <div className="flex items-center text-xs text-gray-500">
          <Clock className="w-3 h-3 mr-1" />
          Created {new Date(deal.created_at).toLocaleDateString()}
        </div>
      </CardContent>
    </Card>
  )
}