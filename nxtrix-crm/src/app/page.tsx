'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { DealService } from '@/services/deal.service'
import { Deal } from '@/types/deal'
import DealCard from '@/components/deals/DealCard'
import DealFilters from '@/components/deals/DealFilters'
import CreateDealModal from '@/components/deals/CreateDealModal'
import { Button } from '@/components/ui/button'
import { Plus, TrendingUp, DollarSign, Target, Clock, Brain } from 'lucide-react'

export default function Dashboard() {
  const [deals, setDeals] = useState<Deal[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({})
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    loadDeals()
  }, [filters])

  const loadDeals = async () => {
    try {
      setLoading(true)
      const data = await DealService.getDeals(filters)
      setDeals(data)
    } catch (error) {
      console.error('Failed to load deals:', error)
    } finally {
      setLoading(false)
    }
  }

  const highValueDeals = deals.filter(deal => deal.deal_score >= 80)
  const totalROI = deals.reduce((sum, deal) => sum + deal.roi, 0) / deals.length || 0
  const totalProfit = deals.reduce((sum, deal) => sum + deal.profit_potential, 0)
  const pendingDeals = deals.filter(deal => deal.status === 'pending').length
  const aiAnalyzedDeals = deals.filter(deal => deal.deal_score > 0).length
  const avgDealScore = deals.reduce((sum, deal) => sum + deal.deal_score, 0) / deals.length || 0

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">NxTrix Deal Analyzer</h1>
              <p className="text-gray-600">Enterprise Real Estate CRM</p>
            </div>
            <Button 
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Deal
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg ROI</p>
                <p className="text-2xl font-bold text-gray-900">{totalROI.toFixed(1)}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Profit Potential</p>
                <p className="text-2xl font-bold text-gray-900">${totalProfit.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">High-Value Deals</p>
                <p className="text-2xl font-bold text-gray-900">{highValueDeals.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Review</p>
                <p className="text-2xl font-bold text-gray-900">{pendingDeals}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Brain className="w-6 h-6 text-indigo-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">AI Score Avg</p>
                <p className="text-2xl font-bold text-gray-900">{avgDealScore.toFixed(0)}/100</p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6">
          <DealFilters onFiltersChange={setFilters} />
        </div>

        {/* Deals Grid */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Deal Pipeline ({deals.length})
            </h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading deals...</p>
            </div>
          ) : deals.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-600">No deals found. Create your first deal to get started!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 p-6">
              {deals.map((deal) => (
                <DealCard key={deal.id} deal={deal} onUpdate={loadDeals} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create Deal Modal */}
      {showCreateModal && (
        <CreateDealModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            loadDeals()
          }}
        />
      )}
    </div>
  )
}
