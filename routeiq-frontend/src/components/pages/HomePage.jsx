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
      <section className="relative py-20 px-4 text-center overflow-hidden">
        <div className="absolute inset-0 bg-brand-animated opacity-30 animate-gradient-shift" style={{backgroundSize: '400% 400%'}}></div>
        <div className="absolute inset-0 bg-page-gradient"></div>
        <div className="relative max-w-4xl mx-auto z-10">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="text-gray-900">Intelligent Ticket</span>
            <span className="block bg-brand-gradient bg-clip-text text-transparent drop-shadow-sm">Routing & Management</span>
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
              <Card key={index} variant="gradient" className="text-center group">
                <CardHeader>
                  <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">{feature.icon}</div>
                  <CardTitle gradient className="text-lg">{feature.title}</CardTitle>
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
            <div className="group">
              <div className="text-4xl font-bold bg-brand-gradient bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">99.9%</div>
              <div className="text-gray-600">Uptime Guarantee</div>
            </div>
            <div className="group">
              <div className="text-4xl font-bold bg-brand-gradient bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">50%</div>
              <div className="text-gray-600">Faster Resolution</div>
            </div>
            <div className="group">
              <div className="text-4xl font-bold bg-brand-gradient bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">24/7</div>
              <div className="text-gray-600">AI-Powered Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-brand-gradient relative overflow-hidden">
        <div className="absolute inset-0 bg-brand-animated opacity-20 animate-gradient-shift" style={{backgroundSize: '400% 400%'}}></div>
        <div className="max-w-4xl mx-auto text-center text-white relative z-10">
          <h2 className="text-3xl md:text-4xl font-bold mb-6 drop-shadow-md">
            Ready to Transform Your Support Operations?
          </h2>
          <p className="text-xl mb-8 opacity-90 drop-shadow-sm">
            Join thousands of teams already using RouteIQ to streamline their ticket management.
          </p>
          <Button variant="secondary" size="lg" className="text-lg px-8 py-4 shadow-brand-lg hover:shadow-2xl">
            Get Started Today
          </Button>
        </div>
      </section>
    </div>
  )
}

export { HomePage }
