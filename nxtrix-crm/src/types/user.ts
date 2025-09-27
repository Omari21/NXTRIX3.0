export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  company?: string
  phone?: string
  avatar_url?: string
  created_at: string
  last_login?: string
  subscription_tier: SubscriptionTier
  preferences: UserPreferences
}

export type UserRole = 'admin' | 'analyst' | 'investor' | 'agent'

export type SubscriptionTier = 'free' | 'pro' | 'enterprise'

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  notifications: {
    email: boolean
    sms: boolean
    push: boolean
  }
  dashboard_layout: string[]
  default_filters: Record<string, any>
}

export interface Session {
  user: User
  access_token: string
  refresh_token: string
  expires_at: number
}