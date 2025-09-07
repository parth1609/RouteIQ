import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { cn } from '@/lib/utils'

/**
 * Metric Card Component
 * Displays key performance indicators and statistics with gradient styling
 */
const MetricCard = ({ 
  title, 
  value, 
  description, 
  icon, 
  trend, 
  trendValue, 
  variant = 'default',
  className 
}) => {
  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up': return 'text-success-600 bg-success-50'
      case 'down': return 'text-error-600 bg-error-50'
      case 'neutral': return 'text-info-600 bg-info-50'
      default: return 'text-gray-600 bg-gray-50'
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

  const getVariantStyles = (variant) => {
    switch (variant) {
      case 'primary':
        return 'bg-brand-gradient border-0 text-white shadow-brand-lg'
      case 'success':
        return 'bg-success-gradient border-0 text-white shadow-success-lg'
      case 'warning':
        return 'bg-warning-gradient border-0 text-white shadow-warning-lg'
      case 'error':
        return 'bg-error-gradient border-0 text-white shadow-error-lg'
      case 'info':
        return 'bg-info-gradient border-0 text-white shadow-info-lg'
      default:
        return 'bg-white border border-gray-200 hover:border-brand-300 hover:shadow-brand transition-all duration-300'
    }
  }

  const getTextStyles = (variant) => {
    if (['primary', 'success', 'warning', 'error', 'info'].includes(variant)) {
      return {
        title: 'text-white/90',
        value: 'text-white',
        description: 'text-white/80'
      }
    }
    return {
      title: 'text-gray-600',
      value: 'text-gray-900',
      description: 'text-gray-500'
    }
  }

  const textStyles = getTextStyles(variant)

  return (
    <Card className={cn(
      "relative overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-brand-lg group",
      getVariantStyles(variant),
      className
    )}>
      {/* Animated gradient overlay for default variant */}
      {variant === 'default' && (
        <div className="absolute inset-0 bg-brand-animated opacity-0 group-hover:opacity-5 transition-opacity duration-300" 
             style={{backgroundSize: '400% 400%'}} />
      )}
      
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
        <CardTitle className={cn("text-sm font-medium", textStyles.title)}>
          {title}
        </CardTitle>
        {icon && (
          <div className={cn(
            "p-2 rounded-xl transition-all duration-300",
            variant === 'default' 
              ? "bg-brand-50 text-brand-600 group-hover:bg-brand-100 group-hover:scale-110" 
              : "bg-white/20 backdrop-blur-sm group-hover:bg-white/30 group-hover:scale-110"
          )}>
            <span className="text-xl">{icon}</span>
          </div>
        )}
      </CardHeader>
      <CardContent className="relative z-10">
        <div className={cn("text-3xl font-bold mb-1 bg-gradient-to-r bg-clip-text", 
          variant === 'default' 
            ? "from-gray-900 to-gray-700" 
            : "text-white drop-shadow-sm"
        )}>
          {value}
        </div>
        {description && (
          <CardDescription className={cn("text-xs", textStyles.description)}>
            {description}
          </CardDescription>
        )}
        {trend && trendValue && (
          <div className={cn(
            "flex items-center text-xs mt-3 px-2 py-1 rounded-full transition-all duration-300",
            getTrendColor(trend)
          )}>
            <span className="mr-1 text-sm">{getTrendIcon(trend)}</span>
            <span className="font-medium">{trendValue}</span>
            <span className="ml-1 opacity-80">from last period</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export { MetricCard }
