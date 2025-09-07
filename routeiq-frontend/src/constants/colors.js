/**
 * RouteIQ Brand Colors
 * Extracted from the company logo gradient
 */
export const BRAND_COLORS = {
  // Primary brand gradient colors from logo
  PRIMARY: {
    START: '#FF7A18',  // Orange
    MID: '#E61E73',    // Magenta
    END: '#1976D2',    // Blue
  },
  
  // Gradient CSS strings for easy use
  GRADIENTS: {
    DEFAULT: 'linear-gradient(135deg, #FF7A18 0%, #E61E73 50%, #1976D2 100%)',
    HORIZONTAL: 'linear-gradient(to right, #FF7A18, #E61E73, #1976D2)',
    VERTICAL: 'linear-gradient(to bottom, #FF7A18, #E61E73, #1976D2)',
    DIAGONAL: 'linear-gradient(to bottom right, #FF7A18, #E61E73, #1976D2)',
  },
  
  // Semantic colors
  SEMANTIC: {
    SUCCESS: '#10B981',
    WARNING: '#F59E0B',
    ERROR: '#EF4444',
    INFO: '#3B82F6',
  },
  
  // Neutral colors
  NEUTRAL: {
    WHITE: '#FFFFFF',
    GRAY_50: '#FAFAFA',
    GRAY_100: '#F5F5F5',
    GRAY_200: '#E5E7EB',
    GRAY_300: '#D1D5DB',
    GRAY_400: '#9CA3AF',
    GRAY_500: '#6B7280',
    GRAY_600: '#4B5563',
    GRAY_700: '#374151',
    GRAY_800: '#1F2937',
    GRAY_900: '#111827',
  }
}

/**
 * Status colors for tickets and system health
 */
export const STATUS_COLORS = {
  ONLINE: BRAND_COLORS.SEMANTIC.SUCCESS,
  OFFLINE: BRAND_COLORS.SEMANTIC.ERROR,
  WARNING: BRAND_COLORS.SEMANTIC.WARNING,
  PENDING: BRAND_COLORS.SEMANTIC.INFO,
  
  // Ticket priorities
  HIGH: BRAND_COLORS.SEMANTIC.ERROR,
  MEDIUM: BRAND_COLORS.SEMANTIC.WARNING,
  LOW: BRAND_COLORS.SEMANTIC.INFO,
  NORMAL: BRAND_COLORS.SEMANTIC.INFO,
}
