import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Filter, X } from 'lucide-react'

interface DealFiltersProps {
  onFiltersChange: (filters: any) => void
}

export default function DealFilters({ onFiltersChange }: DealFiltersProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [filters, setFilters] = useState({
    status: '',
    deal_type: '',
    min_score: '',
    min_roi: ''
  })

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    
    // Convert to API format
    const apiFilters: any = {}
    if (newFilters.status) apiFilters.status = newFilters.status
    if (newFilters.deal_type) apiFilters.deal_type = newFilters.deal_type
    if (newFilters.min_score) apiFilters.min_score = parseInt(newFilters.min_score)
    
    onFiltersChange(apiFilters)
  }

  const clearFilters = () => {
    setFilters({
      status: '',
      deal_type: '',
      min_score: '',
      min_roi: ''
    })
    onFiltersChange({})
  }

  const activeFiltersCount = Object.values(filters).filter(Boolean).length

  return (
    <div className="relative">
      <div className="p-4 border-b border-gray-200">
        <Button
          variant="outline"
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-2"
        >
          <Filter className="w-4 h-4" />
          <span>Filters</span>
          {activeFiltersCount > 0 && (
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {activeFiltersCount}
            </span>
          )}
        </Button>
      </div>

      {isOpen && (
        <div className="p-6 border-b border-gray-200 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="analyzing">Analyzing</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {/* Deal Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Deal Type
              </label>
              <select
                value={filters.deal_type}
                onChange={(e) => handleFilterChange('deal_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                <option value="flip">Flip</option>
                <option value="rental">Rental</option>
                <option value="wholesale">Wholesale</option>
                <option value="brrrr">BRRRR</option>
              </select>
            </div>

            {/* Minimum Score Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Deal Score
              </label>
              <select
                value={filters.min_score}
                onChange={(e) => handleFilterChange('min_score', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Any Score</option>
                <option value="80">80+ (Excellent)</option>
                <option value="70">70+ (Good)</option>
                <option value="60">60+ (Fair)</option>
              </select>
            </div>

            {/* Minimum ROI Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min ROI (%)
              </label>
              <input
                type="number"
                value={filters.min_roi}
                onChange={(e) => handleFilterChange('min_roi', e.target.value)}
                placeholder="e.g. 15"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Clear Filters */}
          {activeFiltersCount > 0 && (
            <div className="mt-4 flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={clearFilters}
                className="flex items-center space-x-2"
              >
                <X className="w-4 h-4" />
                <span>Clear Filters</span>
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}