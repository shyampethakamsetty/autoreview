import axios, { AxiosError } from 'axios';
import type { Review, ReviewsResponse, AIReplyResponse, AnalyticsResponse, SearchResult } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || 'supersecret';

const client = axios.create({
  baseURL: API_URL,
  timeout: 180000, // 3 minutes for OpenAI requests
  headers: {
    'x-api-key': API_KEY,
    'Content-Type': 'application/json',
  },
});

export interface ReviewFilters {
  location?: string;
  sentiment?: string;
  q?: string;
  page?: number;
  page_size?: number;
}

export const api = {
  // Get reviews with filters and pagination
  getReviews: async (filters: ReviewFilters = {}): Promise<ReviewsResponse> => {
    const { data } = await client.get<ReviewsResponse>('/reviews', { params: filters });
    return data;
  },

  // Get single review by ID
  getReview: async (id: number): Promise<Review> => {
    const { data } = await client.get<Review>(`/reviews/${id}`);
    return data;
  },

  // Generate AI reply suggestion
  suggestReply: async (id: number, temperature: number = 0.2): Promise<AIReplyResponse> => {
    const { data } = await client.post<AIReplyResponse>(`/reviews/${id}/suggest-reply`, { temperature });
    return data;
  },

  // Get analytics data
  getAnalytics: async (): Promise<AnalyticsResponse> => {
    const { data } = await client.get<AnalyticsResponse>('/analytics');
    return data;
  },

  // Search similar reviews
  searchReviews: async (query: string, k: number = 5): Promise<SearchResult[]> => {
    const { data } = await client.get<SearchResult[]>('/search', { params: { q: query, k } });
    return data;
  },

  // Ingest reviews
  ingestReviews: async (reviews: Omit<Review, 'sentiment' | 'topic'>[]): Promise<any> => {
    const { data } = await client.post('/ingest', reviews);
    return data;
  },

  // Health check
  health: async (): Promise<{ status: string }> => {
    const { data } = await client.get('/health');
    return data;
  },
};

export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string }>;
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    if (axiosError.response?.status === 401) {
      return 'Unauthorized. Please check your API key.';
    }
    if (axiosError.response?.status === 404) {
      return 'Resource not found.';
    }
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  return 'An unexpected error occurred.';
};
