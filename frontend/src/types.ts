// Core entities
export interface Review {
  id: number;
  location: string;
  rating: number;
  text: string;
  date: string;
  sentiment?: string | null;
  topic?: string | null;
}

// API Request/Response types
export interface ReviewFilters {
  page?: number;
  page_size?: number;
  location?: string;
  sentiment?: string;
  q?: string;
  min_rating?: number;
  max_rating?: number;
  date_from?: string;
  date_to?: string;
  topic?: string;
}

export interface PaginationInfo {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface ReviewsResponse {
  reviews: Review[];
  pagination: PaginationInfo;
}

export interface AIReplyResponse {
  reply: string;
  tags: AITags;
  reasoning_log: string;
}

export interface AITags {
  sentiment: string;
  topic: string;
}

export interface AnalyticsResponse {
  total: number;
  average_rating: number;
  sentiment_counts: Record<string, number>;
  topic_counts: Record<string, number>;
  location_counts: Record<string, number>;
  rating_distribution: Record<string, number>;
}

export interface SearchResult {
  id: number;
  score: number;
}

// Bulk operations
export interface BulkReplyRequest {
  review_ids: number[];
  temperature?: number;
}

export interface BulkReplyResponse {
  processed: number;
  successful: number;
  failed: number;
  results: BulkReplyResult[];
}

export interface BulkReplyResult {
  review_id: number;
  success: boolean;
  reply?: string;
  tags?: AITags;
  reasoning_log?: string;
  error?: string;
}

// Export types
export type ExportFormat = 'csv' | 'json';

// Streaming types
export interface StreamingChunk {
  type: 'metadata' | 'content' | 'complete' | 'error';
  content?: string;
  sentiment?: string;
  topic?: string;
  reply?: string;
  tags?: AITags;
  reasoning_log?: string;
  error?: string;
}

// Utility types
export type Sentiment = 'positive' | 'negative' | 'neutral';
export type Rating = 1 | 2 | 3 | 4 | 5;

// API Error types
export interface APIError {
  detail: string;
  status_code?: number;
}
