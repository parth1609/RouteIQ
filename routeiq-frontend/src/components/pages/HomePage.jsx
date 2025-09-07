import React from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

/**
 * HomePage component - Landing page for RouteIQ
 * Features hero section, benefits, and call-to-action
 */
const HomePage = () => {
  const features = [
    {
      title: "AI-Powered Classification",
      description: "Automatically categorize and prioritize tickets using advanced machine learning algorithms.",
      icon: "🤖"
    },
    {
      title: "Multi-Platform Support",
      description: "Seamlessly integrate with Zammad and Zendesk for unified ticket management.",
      icon: "🔗"
    },
    {
      title: "Real-Time Analytics",
      description: "Monitor system performance and ticket trends with comprehensive dashboards.",
      icon: "📊"
    },
    {
      title: "Smart Routing",
      description: "Intelligently route tickets to the right teams based on content analysis.",
      icon: "🎯"
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 px-4 text-center">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-start/10 via-brand-mid/10 to-brand-end/10"></div>
        <div className="relative max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Intelligent Ticket
            <span className="block brand-text">Routing & Management</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Streamline your IT support workflows with AI-powered ticket classification, 
            smart routing, and unified management across multiple platforms.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="text-lg px-8 py-4">
              Start Free Trial
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8 py-4">
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose RouteIQ?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Transform your support operations with intelligent automation and seamless integrations.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-12">
            Trusted by Support Teams Worldwide
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="text-4xl font-bold brand-text mb-2">99.9%</div>
              <div className="text-gray-600">Uptime Guarantee</div>
            </div>
            <div>
              <div className="text-4xl font-bold brand-text mb-2">50%</div>
              <div className="text-gray-600">Faster Resolution</div>
            </div>
            <div>
              <div className="text-4xl font-bold brand-text mb-2">24/7</div>
              <div className="text-gray-600">AI-Powered Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-brand-start via-brand-mid to-brand-end">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Transform Your Support Operations?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of teams already using RouteIQ to streamline their ticket management.
          </p>
          <Button variant="secondary" size="lg" className="text-lg px-8 py-4">
            Get Started Today
          </Button>
        </div>
      </section>
    </div>
  )
}

export { HomePage }
