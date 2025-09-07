# RouteIQ Frontend

A modern React-based frontend application for RouteIQ - an AI-powered ticket management system that integrates with Zammad and Zendesk platforms.

## 🚀 Features

### ✅ Completed Features
- **Modern UI/UX**: Built with React 18, TailwindCSS v4, and responsive design
- **Authentication System**: Complete login/logout with protected routes
- **Dashboard**: Real-time metrics, system health monitoring, and quick actions
- **Ticket Management**: Create, list, filter, and search tickets across platforms
- **AI Classification**: Test AI model, view performance insights, and configuration
- **Analytics Dashboard**: Comprehensive charts, trends, and performance metrics
- **Settings Management**: Integration configuration for Zammad, Zendesk, and AI
- **Error Handling**: Error boundaries and loading states throughout the app
- **Brand Consistency**: RouteIQ gradient colors and professional design

### 🎨 Design System
- **Brand Colors**: Orange to Pink to Blue gradient (#FF7A18 → #E61E73 → #1976D2)
- **Typography**: Inter font family for modern readability
- **Components**: Reusable UI components with consistent styling
- **Responsive**: Mobile-first design with collapsible navigation

## 🛠 Tech Stack

- **React 18** - Modern React with hooks and functional components
- **Vite** - Fast development server and build tool
- **TailwindCSS v4** - Utility-first CSS framework with PostCSS
- **React Router DOM** - Client-side routing
- **Axios** - HTTP client for API communication
- **Context API** - State management for authentication

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RouteIQ/routeiq-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file in the root directory
   VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:5173`

## 🏗 Project Structure

```
src/
├── components/
│   ├── auth/              # Authentication components
│   │   ├── AuthContext.jsx
│   │   ├── LoginPage.jsx
│   │   └── ProtectedRoute.jsx
│   ├── common/            # Shared components
│   │   └── ErrorBoundary.jsx
│   ├── forms/             # Form components
│   │   └── TicketCreationForm.jsx
│   ├── layout/            # Layout components
│   │   ├── DashboardLayout.jsx
│   │   └── Header.jsx
│   ├── pages/             # Page components
│   │   ├── HomePage.jsx
│   │   ├── AboutPage.jsx
│   │   ├── FeaturesPage.jsx
│   │   ├── ContactPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── TicketManagementPage.jsx
│   │   ├── AIClassificationPage.jsx
│   │   ├── AnalyticsPage.jsx
│   │   └── SettingsPage.jsx
│   └── ui/                # UI components
│       ├── Button.jsx
│       ├── Card.jsx
│       ├── MetricCard.jsx
│       └── SystemHealthWidget.jsx
├── constants/             # App constants
│   └── colors.js
├── lib/                   # Utilities
│   └── utils.js
├── services/              # API services
│   └── api.js
├── App.jsx               # Main app component
├── index.css             # Global styles
└── main.jsx              # App entry point
```

## 🔐 Authentication

The app includes a complete authentication system:

### Demo Credentials
- **Admin**: admin@routeiq.com / admin123
- **Support Agent**: support@routeiq.com / support123  
- **Manager**: manager@routeiq.com / manager123

### Features
- Protected routes for dashboard pages
- User profile display with avatar
- Persistent login state via localStorage
- Logout functionality with redirect

## 🎫 Ticket Management

### Create Tickets
- Support for both Zammad and Zendesk platforms
- AI-powered classification preview
- Form validation and error handling
- Real-time priority and department suggestions

### Ticket List
- Filter by platform (Zammad/Zendesk)
- Filter by status (Open/Pending/Closed/Resolved)
- Search by title, description, or customer
- Responsive ticket cards with status indicators

## 🤖 AI Classification

### Performance Insights
- Model accuracy metrics
- Prediction volume tracking
- Priority and department distribution charts
- Real-time performance indicators

### Testing Interface
- Test classification with custom input
- Sample test cases for quick testing
- Confidence score display
- Error handling for API failures

## 📊 Analytics Dashboard

### Key Metrics
- Total tickets, open tickets, resolved tickets
- Average resolution time
- Customer satisfaction scores
- Trend analysis over time

### Visualizations
- Ticket volume trends (bar charts)
- Priority distribution (progress bars)
- Platform comparison metrics
- Department performance statistics

## ⚙️ Settings & Configuration

### Integration Management
- Zammad connection settings (URL, API token)
- Zendesk configuration (subdomain, email, token)
- Connection testing and status indicators
- Settings persistence via localStorage

### AI Configuration
- Model version selection
- Confidence threshold adjustment
- Auto-classification toggle
- Model health monitoring

### Notifications
- Email alert preferences
- Slack integration settings
- Webhook configuration
- Custom notification rules

## 🔧 Development

### Available Scripts
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Code Style
- Functional components with hooks
- JSDoc comments for all components
- Consistent file naming (PascalCase for components)
- Modular component architecture

### API Integration
The frontend communicates with the FastAPI backend through:
- Health check endpoints for system monitoring
- CRUD operations for ticket management
- AI classification prediction endpoints
- Error handling with user-friendly messages

## 🚀 Production Deployment

### Build Optimization
```bash
npm run build
```

### Environment Variables
Set the following for production:
```bash
VITE_API_BASE_URL=https://your-api-domain.com/api/v1
```

### Deployment Options
- **Netlify**: Direct deployment from Git repository
- **Vercel**: Zero-config deployment for React apps
- **Static Hosting**: Deploy the `dist` folder to any static host

## 🔗 Backend Integration

The frontend is designed to work with the RouteIQ FastAPI backend:
- **API Base URL**: Configurable via environment variables
- **Authentication**: Token-based (mock implementation for demo)
- **Error Handling**: Centralized error processing with user feedback
- **Health Checks**: Real-time monitoring of backend services

## 📱 Responsive Design

- **Mobile-first**: Optimized for mobile devices
- **Tablet Support**: Responsive layouts for tablet screens
- **Desktop**: Full-featured experience on desktop
- **Navigation**: Collapsible sidebar for space efficiency

## 🎯 Future Enhancements

### Pending Tasks
- Unit tests for components
- Production build optimization
- Advanced error reporting integration
- Real-time notifications via WebSocket
- Advanced analytics with chart libraries

### Potential Features
- Dark mode support
- Multi-language support
- Advanced filtering and sorting
- Bulk ticket operations
- Custom dashboard widgets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the backend API documentation
- Review the component JSDoc comments
- Test with demo credentials first
- Ensure backend services are running

---

**RouteIQ Frontend** - Built with ❤️ using React, TailwindCSS, and modern web technologies.
