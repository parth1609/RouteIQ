import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

/**
 * About Us page component
 * Showcases company information, team, and values
 */
const AboutPage = () => {
  const teamMembers = [
    {
      name: "Alex Johnson",
      role: "CEO & Founder",
      description: "10+ years in enterprise software and AI solutions.",
      avatar: "👨‍💼"
    },
    {
      name: "Sarah Chen",
      role: "CTO",
      description: "Former ML engineer at top tech companies, AI specialist.",
      avatar: "👩‍💻"
    },
    {
      name: "Michael Rodriguez",
      role: "Head of Product",
      description: "Expert in customer support systems and UX design.",
      avatar: "👨‍🎨"
    },
    {
      name: "Emily Davis",
      role: "Lead Engineer",
      description: "Full-stack developer with expertise in scalable systems.",
      avatar: "👩‍🔬"
    }
  ]

  const values = [
    {
      title: "Innovation First",
      description: "We leverage cutting-edge AI to solve real-world support challenges.",
      icon: "💡"
    },
    {
      title: "Customer Success",
      description: "Your success is our success. We're committed to your growth.",
      icon: "🎯"
    },
    {
      title: "Transparency",
      description: "Open communication and honest relationships with our clients.",
      icon: "🔍"
    },
    {
      title: "Reliability",
      description: "99.9% uptime and enterprise-grade security you can trust.",
      icon: "🛡️"
    }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 px-4 text-center bg-gradient-to-br from-brand-start/5 via-brand-mid/5 to-brand-end/5">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            About <span className="brand-text">RouteIQ</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            We're on a mission to revolutionize IT support through intelligent automation, 
            helping teams resolve issues faster and more efficiently than ever before.
          </p>
        </div>
      </section>

      {/* Story Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
              <p className="text-gray-600 mb-4">
                Founded in 2023, RouteIQ emerged from a simple observation: support teams 
                were drowning in tickets while customers waited for resolutions. Traditional 
                ticketing systems weren't keeping up with the complexity of modern IT environments.
              </p>
              <p className="text-gray-600 mb-6">
                Our founders, having experienced these challenges firsthand at scale, decided 
                to build something better. By combining advanced AI with deep integrations, 
                we created a platform that doesn't just manage tickets—it understands them.
              </p>
              <Button>Learn More About Our Technology</Button>
            </div>
            <div className="bg-gradient-to-br from-brand-start/10 via-brand-mid/10 to-brand-end/10 rounded-2xl p-8 text-center">
              <div className="text-6xl mb-4">🚀</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Our Mission</h3>
              <p className="text-gray-600">
                Empower support teams with AI-driven insights to deliver exceptional 
                customer experiences while reducing operational overhead.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Values
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              The principles that guide everything we do and every decision we make.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {values.map((value, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="text-4xl mb-4">{value.icon}</div>
                  <CardTitle className="text-lg">{value.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm">
                    {value.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Meet Our Team
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Passionate experts dedicated to transforming the future of IT support.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {teamMembers.map((member, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="text-6xl mb-4">{member.avatar}</div>
                  <CardTitle className="text-lg">{member.name}</CardTitle>
                  <CardDescription className="text-brand-end font-medium">
                    {member.role}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">
                    {member.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-brand-start via-brand-mid to-brand-end">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Join Our Journey?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Whether you're looking to transform your support operations or join our team, 
            we'd love to hear from you.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button variant="secondary" size="lg">
              Contact Us
            </Button>
            <Button variant="outline" size="lg" className="bg-transparent border-white text-white hover:bg-white hover:text-brand-end">
              View Careers
            </Button>
          </div>
        </div>
      </section>
    </div>
  )
}

export { AboutPage }
