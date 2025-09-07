import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { cn } from '@/lib/utils'

/**
 * Metric Card Component
 * Displays key performance indicators and statistics
 */
const MetricCard = ({ 
  title, 
  value, 
  description, 
  icon, 
  trend, 
  trendValue, 
  className 
}) => {
  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up': return 'text-green-600'
      case 'down': return 'text-red-600'
      case 'neutral': return 'text-gray-600'
      default: return 'text-gray-600'
    }
  }

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return '↗️'
      case 'down': return '↘️'
      case 'neutral': return '➡️'
      default: return ''
    }
  }

  return (
    <Card className={cn("hover:shadow-lg transition-shadow", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">
          {title}
        </CardTitle>
        {icon && <span className="text-2xl">{icon}</span>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900 mb-1">
          {value}
        </div>
        {description && (
          <CardDescription className="text-xs">
            {description}
          </CardDescription>
        )}
        {trend && trendValue && (
          <div className={cn("flex items-center text-xs mt-2", getTrendColor(trend))}>
            <span className="mr-1">{getTrendIcon(trend)}</span>
            <span>{trendValue}</span>
            <span className="ml-1 text-gray-500">from last period</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export { MetricCard }
