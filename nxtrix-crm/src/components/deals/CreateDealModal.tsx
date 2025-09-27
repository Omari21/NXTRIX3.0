import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DealService } from '@/services/deal.service'
import { X, Save } from 'lucide-react'

interface CreateDealModalProps {
  onClose: () => void
  onSuccess: () => void
}

export default function CreateDealModal({ onClose, onSuccess }: CreateDealModalProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    property_address: '',
    purchase_price: '',
    after_repair_value: '',
    repair_costs: '',
    monthly_rent: '',
    monthly_expenses: '',
    deal_type: 'flip' as const,
    profit_potential: ''
  })

  const handleInputChange = (key: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const dealData = {
        ...formData,
        purchase_price: parseFloat(formData.purchase_price) || 0,
        after_repair_value: parseFloat(formData.after_repair_value) || 0,
        repair_costs: parseFloat(formData.repair_costs) || 0,
        monthly_rent: parseFloat(formData.monthly_rent) || 0,
        monthly_expenses: parseFloat(formData.monthly_expenses) || 0,
        profit_potential: parseFloat(formData.profit_potential) || 0,
        status: 'analyzing' as const,
        created_by: 'current-user' // This would come from auth context
      }

      await DealService.createDeal(dealData)
      onSuccess()
    } catch (error) {
      console.error('Failed to create deal:', error)
      alert('Failed to create deal. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Create New Deal</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deal Title *
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. 123 Main St Fix & Flip"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Property Address *
                </label>
                <input
                  type="text"
                  required
                  value={formData.property_address}
                  onChange={(e) => handleInputChange('property_address', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="123 Main St, City, State 12345"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deal Type *
                </label>
                <select
                  required
                  value={formData.deal_type}
                  onChange={(e) => handleInputChange('deal_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="flip">Fix & Flip</option>
                  <option value="rental">Buy & Hold Rental</option>
                  <option value="wholesale">Wholesale</option>
                  <option value="brrrr">BRRRR</option>
                </select>
              </div>
            </div>

            {/* Financial Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Purchase Price *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  step="1000"
                  value={formData.purchase_price}
                  onChange={(e) => handleInputChange('purchase_price', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="250000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  After Repair Value (ARV)
                </label>
                <input
                  type="number"
                  min="0"
                  step="1000"
                  value={formData.after_repair_value}
                  onChange={(e) => handleInputChange('after_repair_value', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="320000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Repair Costs
                </label>
                <input
                  type="number"
                  min="0"
                  step="500"
                  value={formData.repair_costs}
                  onChange={(e) => handleInputChange('repair_costs', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="25000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Profit Potential
                </label>
                <input
                  type="number"
                  min="0"
                  step="1000"
                  value={formData.profit_potential}
                  onChange={(e) => handleInputChange('profit_potential', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="45000"
                />
              </div>
            </div>

            {/* Rental Specific Fields */}
            {(formData.deal_type === 'rental' || formData.deal_type === 'brrrr') && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Rent
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="50"
                    value={formData.monthly_rent}
                    onChange={(e) => handleInputChange('monthly_rent', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="2500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Expenses
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="50"
                    value={formData.monthly_expenses}
                    onChange={(e) => handleInputChange('monthly_expenses', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="800"
                  />
                </div>
              </div>
            )}

            {/* Submit Buttons */}
            <div className="flex space-x-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={loading}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={loading}
                className="flex-1"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                Create Deal
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}