import React from 'react'
import { cn } from '@/lib/utils'

/**
 * Card component for content containers
 * Provides consistent styling with shadow and border
 */
const Card = React.forwardRef(({ className, variant = 'default', ...props }, ref) => {
  const variants = {
    default: "rounded-xl border-2 border-transparent bg-card-gradient shadow-brand hover:shadow-brand-lg transition-all duration-300 hover:scale-[1.02] relative overflow-hidden",
    gradient: "rounded-xl border-2 border-brand-mid/20 bg-brand-subtle shadow-brand hover:shadow-brand-lg transition-all duration-300 hover:scale-[1.02] relative overflow-hidden",
    outlined: "rounded-xl border-2 border-brand-gradient bg-white shadow-brand hover:shadow-brand-lg transition-all duration-300 hover:scale-[1.02] relative overflow-hidden",
    elevated: "rounded-xl border-0 bg-white shadow-brand-lg hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] relative overflow-hidden"
  }
  
  return (
    <div
      ref={ref}
      className={cn(variants[variant], className)}
      {...props}
    />
  )
})
Card.displayName = "Card"

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef(({ className, gradient = false, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      gradient ? "bg-brand-gradient bg-clip-text text-transparent" : "text-gray-900",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-gray-500", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
