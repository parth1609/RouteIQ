import React from 'react'
import { cn } from '@/lib/utils'

/**
 * Button component with RouteIQ brand variants
 * Supports different sizes, variants, and states
 */
const Button = React.forwardRef(({ 
  className, 
  variant = 'default', 
  size = 'default', 
  disabled = false,
  children, 
  ...props 
}, ref) => {
  const baseStyles = "inline-flex items-center justify-center rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
  
  const variants = {
    default: "bg-brand-gradient text-white hover:shadow-brand-lg hover:scale-105 transform transition-all duration-300 focus-visible:ring-brand-mid shadow-brand",
    secondary: "bg-gradient-to-r from-gray-100 to-gray-200 text-gray-900 hover:from-gray-200 hover:to-gray-300 hover:shadow-lg transform hover:scale-105 transition-all duration-300 focus-visible:ring-gray-500",
    outline: "border-2 border-brand-mid bg-white text-brand-mid hover:bg-brand-subtle hover:border-brand-mid hover:shadow-brand transform hover:scale-105 transition-all duration-300 focus-visible:ring-brand-end",
    ghost: "text-brand-mid hover:bg-brand-subtle hover:text-brand-start transform hover:scale-105 transition-all duration-300 focus-visible:ring-brand-end",
    destructive: "bg-gradient-to-r from-error to-error-dark text-white hover:shadow-error hover:scale-105 transform transition-all duration-300 focus-visible:ring-error",
    success: "bg-gradient-to-r from-success to-success-dark text-white hover:shadow-success hover:scale-105 transform transition-all duration-300 focus-visible:ring-success",
    warning: "bg-gradient-to-r from-warning to-warning-dark text-white hover:shadow-warning hover:scale-105 transform transition-all duration-300 focus-visible:ring-warning",
    info: "bg-gradient-to-r from-info to-info-dark text-white hover:shadow-info hover:scale-105 transform transition-all duration-300 focus-visible:ring-info",
  }
  
  const sizes = {
    default: "h-10 px-4 py-2 text-sm",
    sm: "h-8 px-3 py-1 text-xs",
    lg: "h-12 px-6 py-3 text-base",
    icon: "h-10 w-10",
  }
  
  return (
    <button
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      ref={ref}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
})

Button.displayName = "Button"

export { Button }
