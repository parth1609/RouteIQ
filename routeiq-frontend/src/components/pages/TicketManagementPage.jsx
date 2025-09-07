import React, { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { TicketCreationForm } from '@/components/forms/TicketCreationForm'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { zammadAPI, zendeskAPI, handleAPIError } from '@/services/api'
import { cn } from '@/lib/utils'

/**
 * Ticket Management Page
 * Provides ticket creation, listing, and management functionality
 */
const TicketManagementPage = () => {
  const [activeTab, setActiveTab] = useState('create')
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    platform: 'all',
    status: 'all',
    search: ''
  })

  useEffect(() => {
    if (activeTab === 'list') {
      loadTickets()
    }
  }, [activeTab, filters])

  const loadTickets = async () => {
    setLoading(true)
    try {
      const allTickets = []
      
      // Load Zammad tickets
      if (filters.platform === 'all' || filters.platform === 'zammad') {
        try {
          const zammadResponse = await zammadAPI.listTickets({ limit: 50 })
          if (zammadResponse.data?.tickets) {
            const zammadTickets = zammadResponse.data.tickets.map(ticket => ({
              ...ticket,
              platform: 'zammad',
              customer: ticket.customer || 'Unknown'
            }))
            allTickets.push(...zammadTickets)
          }
        } catch (error) {
          console.error('Failed to load Zammad tickets:', handleAPIError(error))
        }
      }

      // Load Zendesk tickets (when available)
      if (filters.platform === 'all' || filters.platform === 'zendesk') {
        try {
          const zendeskResponse = await zendeskAPI.listTickets({ limit: 50 })
          if (zendeskResponse.data?.tickets) {
            const zendeskTickets = zendeskResponse.data.tickets.map(ticket => ({
              ...ticket,
              platform: 'zendesk',
              customer: ticket.requester?.name || 'Unknown'
            }))
            allTickets.push(...zendeskTickets)
          }
        } catch (error) {
          console.error('Failed to load Zendesk tickets:', handleAPIError(error))
        }
      }

      // Apply filters
      let filteredTickets = allTickets
      
      if (filters.status !== 'all') {
        filteredTickets = filteredTickets.filter(ticket => 
          ticket.state?.toLowerCase() === filters.status.toLowerCase()
        )
      }
      
      if (filters.search) {
        const searchLower = filters.search.toLowerCase()
        filteredTickets = filteredTickets.filter(ticket =>
          ticket.title?.toLowerCase().includes(searchLower) ||
          ticket.subject?.toLowerCase().includes(searchLower) ||
          ticket.customer?.toLowerCase().includes(searchLower)
        )
      }

      setTickets(filteredTickets)
    } catch (error) {
      console.error('Failed to load tickets:', handleAPIError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleTicketCreated = (newTicket) => {
    // Show success message and refresh list if on list tab
    if (activeTab === 'list') {
      loadTickets()
    }
    // Could add toast notification here
  }

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'open': return 'bg-yellow-100 text-yellow-800'
      case 'closed': return 'bg-green-100 text-green-800'
      case 'pending': return 'bg-blue-100 text-blue-800'
      case 'resolved': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPlatformColor = (platform) => {
    switch (platform) {
      case 'zammad': return 'bg-purple-100 text-purple-800'
      case 'zendesk': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Ticket Management</h1>
            <p className="text-gray-600">Create and manage support tickets across platforms</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('create')}
              className={cn(
                "py-2 px-1 border-b-2 font-medium text-sm",
                activeTab === 'create'
                  ? "border-brand-end text-brand-end"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              )}
            >
              Create Ticket
            </button>
            <button
              onClick={() => setActiveTab('list')}
              className={cn(
                "py-2 px-1 border-b-2 font-medium text-sm",
                activeTab === 'list'
                  ? "border-brand-end text-brand-end"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              )}
            >
              Ticket List
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'create' && (
          <TicketCreationForm onSuccess={handleTicketCreated} />
        )}

        {activeTab === 'list' && (
          <div className="space-y-6">
            {/* Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Filters</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Platform
                    </label>
                    <select
                      value={filters.platform}
                      onChange={(e) => setFilters(prev => ({ ...prev, platform: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                    >
                      <option value="all">All Platforms</option>
                      <option value="zammad">Zammad</option>
                      <option value="zendesk">Zendesk</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={filters.status}
                      onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                    >
                      <option value="all">All Status</option>
                      <option value="open">Open</option>
                      <option value="pending">Pending</option>
                      <option value="closed">Closed</option>
                      <option value="resolved">Resolved</option>
                    </select>
                  </div>
                  
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Search
                    </label>
                    <input
                      type="text"
                      value={filters.search}
                      onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                      placeholder="Search tickets..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-end focus:border-transparent"
                    />
                  </div>
                </div>
                
                <div className="mt-4 flex space-x-2">
                  <Button onClick={loadTickets} disabled={loading}>
                    {loading ? 'Loading...' : 'Refresh'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setFilters({ platform: 'all', status: 'all', search: '' })}
                  >
                    Clear Filters
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Ticket List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Tickets ({tickets.length})</span>
                  <Button variant="outline" size="sm" onClick={loadTickets}>
                    🔄 Refresh
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    ))}
                  </div>
                ) : tickets.length > 0 ? (
                  <div className="space-y-4">
                    {tickets.map((ticket) => (
                      <div key={`${ticket.platform}-${ticket.id}`} className="border rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <h3 className="font-medium text-gray-900">
                                #{ticket.id} - {ticket.title || ticket.subject}
                              </h3>
                              <span className={cn(
                                "px-2 py-1 rounded-full text-xs font-medium",
                                getPlatformColor(ticket.platform)
                              )}>
                                {ticket.platform}
                              </span>
                            </div>
                            
                            <div className="text-sm text-gray-600 mb-2">
                              Customer: {ticket.customer}
                            </div>
                            
                            <div className="text-sm text-gray-500">
                              Created: {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'Unknown'}
                              {ticket.updated_at && (
                                <span className="ml-4">
                                  Updated: {new Date(ticket.updated_at).toLocaleDateString()}
                                </span>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <span className={cn(
                              "px-2 py-1 rounded-full text-xs font-medium",
                              getStatusColor(ticket.state)
                            )}>
                              {ticket.state || 'unknown'}
                            </span>
                            
                            {ticket.priority && (
                              <span className={cn(
                                "px-2 py-1 rounded-full text-xs font-medium",
                                ticket.priority === 'high' ? 'bg-red-100 text-red-800' :
                                ticket.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-green-100 text-green-800'
                              )}>
                                {ticket.priority}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-4">📭</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No tickets found</h3>
                    <p className="text-gray-500">
                      {filters.search || filters.status !== 'all' || filters.platform !== 'all'
                        ? 'Try adjusting your filters'
                        : 'Create your first ticket to get started'
                      }
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

export { TicketManagementPage }
