import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

/**
 * Features page component
 * Detailed showcase of RouteIQ capabilities and benefits
 */
const FeaturesPage = () => {
  const mainFeatures = [
    {
      title: "AI-Powered Classification",
      description: "Advanced machine learning algorithms automatically categorize tickets by type, priority, and department with 95%+ accuracy.",
      benefits: ["Reduce manual sorting time", "Improve accuracy", "Scale with volume"],
      icon: "🤖"
    },
    {
      title: "Multi-Platform Integration",
      description: "Seamlessly connect with Zammad and Zendesk through our unified API, managing all tickets from one interface.",
      benefits: ["Unified dashboard", "Consistent workflows", "Reduced context switching"],
      icon: "🔗"
    },
    {
      title: "Smart Routing Engine",
      description: "Intelligently route tickets to the right teams based on content analysis, urgency, and team capacity.",
      benefits: ["Faster resolution times", "Balanced workloads", "Improved SLA compliance"],
      icon: "🎯"
    },
    {
      title: "Real-Time Analytics",
      description: "Comprehensive dashboards and reports provide insights into team performance, trends, and bottlenecks.",
      benefits: ["Data-driven decisions", "Performance optimization", "Predictive insights"],
      icon: "📊"
    }
  ]

  const additionalFeatures = [
    { title: "24/7 System Monitoring", description: "Continuous health checks and alerts", icon: "🔍" },
    { title: "Custom Workflows", description: "Tailor processes to your team's needs", icon: "⚙️" },
    { title: "API-First Architecture", description: "Integrate with your existing tools", icon: "🔌" },
    { title: "Enterprise Security", description: "SOC 2 compliant with end-to-end encryption", icon: "🛡️" },
    { title: "Automated Escalation", description: "Smart escalation based on SLA rules", icon: "⏰" },
    { title: "Knowledge Base Integration", description: "AI-powered solution suggestions", icon: "📚" }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 px-4 text-center bg-gradient-to-br from-brand-start/5 via-brand-mid/5 to-brand-end/5">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Powerful Features for
            <span className="block brand-text">Modern Support Teams</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Discover how RouteIQ's intelligent features can transform your support operations 
            and deliver exceptional customer experiences.
          </p>
          <Button size="lg">
            Start Your Free Trial
          </Button>
        </div>
      </section>

      {/* Main Features */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Core Capabilities
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              The essential features that make RouteIQ the intelligent choice for ticket management.
            </p>
          </div>
          
          <div className="space-y-16">
            {mainFeatures.map((feature, index) => (
              <div key={index} className={`grid md:grid-cols-2 gap-12 items-center ${index % 2 === 1 ? 'md:grid-flow-col-dense' : ''}`}>
                <div className={index % 2 === 1 ? 'md:col-start-2' : ''}>
                  <div className="text-5xl mb-6">{feature.icon}</div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{feature.title}</h3>
                  <p className="text-gray-600 mb-6 text-lg">{feature.description}</p>
                  <div className="space-y-2">
                    {feature.benefits.map((benefit, benefitIndex) => (
                      <div key={benefitIndex} className="flex items-center text-gray-700">
                        <div className="w-2 h-2 bg-brand-end rounded-full mr-3"></div>
                        {benefit}
                      </div>
                    ))}
                  </div>
                </div>
                <div className={`bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-8 ${index % 2 === 1 ? 'md:col-start-1' : ''}`}>
                  <div className="aspect-video bg-white rounded-lg shadow-sm flex items-center justify-center">
                    <div className="text-gray-400 text-lg">Feature Demo</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Additional Features Grid */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Additional features designed to support your team's success.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {additionalFeatures.map((feature, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="text-3xl mb-2">{feature.icon}</div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Integration Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Seamless Integrations
          </h2>
          <p className="text-lg text-gray-600 mb-12">
            RouteIQ works with the tools you already use and love.
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 items-center">
            <div className="bg-gray-100 rounded-lg p-6 aspect-square flex items-center justify-center">
              <span className="font-bold text-gray-600">Zammad</span>
            </div>
            <div className="bg-gray-100 rounded-lg p-6 aspect-square flex items-center justify-center">
              <span className="font-bold text-gray-600">Zendesk</span>
            </div>
            <div className="bg-gray-100 rounded-lg p-6 aspect-square flex items-center justify-center">
              <span className="font-bold text-gray-600">Slack</span>
            </div>
            <div className="bg-gray-100 rounded-lg p-6 aspect-square flex items-center justify-center">
              <span className="font-bold text-gray-600">Teams</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-brand-start via-brand-mid to-brand-end">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Experience These Features?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            See how RouteIQ can transform your support operations with a personalized demo.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button variant="secondary" size="lg">
              Schedule Demo
            </Button>
            <Button variant="outline" size="lg" className="bg-transparent border-white text-white hover:bg-white hover:text-brand-end">
              Start Free Trial
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}

export { FeaturesPage }
