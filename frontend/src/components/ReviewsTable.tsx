import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, handleApiError, type ReviewFilters } from '../api/client';
import type { Review } from '../types';

export default function ReviewsTable() {
  const navigate = useNavigate();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  // Filters
  const [location, setLocation] = useState('');
  const [sentiment, setSentiment] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [locations, setLocations] = useState<string[]>([]);

  const pageSize = 10;

  // Fetch unique locations for filter
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        // Fetch multiple pages to get all locations (respecting 100 limit per page)
        const allReviews = [];
        let page = 1;
        let hasMore = true;
        
        while (hasMore && page <= 10) { // Limit to 10 pages (1000 reviews max)
          const data = await api.getReviews({ page, page_size: 100 });
          allReviews.push(...data.reviews);
          hasMore = page < data.pagination.total_pages;
          page++;
        }
        
        const uniqueLocations = Array.from(new Set(allReviews.map(r => r.location)));
        setLocations(uniqueLocations.sort());
      } catch (err) {
        console.error('Failed to fetch locations:', err);
      }
    };
    fetchLocations();
  }, []);

  // Fetch reviews with filters
  useEffect(() => {
    const fetchReviews = async () => {
      setLoading(true);
      setError(null);
      try {
        const filters: ReviewFilters = {
          page,
          page_size: pageSize,
        };
        if (location) filters.location = location;
        if (sentiment) filters.sentiment = sentiment;
        if (searchQuery) filters.q = searchQuery;

        const data = await api.getReviews(filters);
        setReviews(data.reviews);
        setTotalPages(data.pagination.total_pages);
        setTotal(data.pagination.total);
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, [page, location, sentiment, searchQuery]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1); // Reset to first page on new search
  };

  const getSentimentColor = (sentiment?: string | null) => {
    switch (sentiment) {
      case 'positive': return 'green';
      case 'negative': return 'red';
      case 'neutral': return 'gray';
      default: return 'lightgray';
    }
  };

  const getRatingStars = (rating: number) => {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating);
  };

  if (loading && reviews.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Loading reviews...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>Customer Reviews Inbox</h2>
      
      {/* Filters */}
      <div style={{ 
        marginBottom: '20px', 
        padding: '15px', 
        backgroundColor: '#f5f5f5', 
        borderRadius: '8px',
        display: 'flex',
        gap: '15px',
        flexWrap: 'wrap',
        alignItems: 'flex-end'
      }}>
        {/* Location Filter */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Location:
          </label>
          <select 
            value={location} 
            onChange={(e) => { setLocation(e.target.value); setPage(1); }}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', minWidth: '150px' }}
          >
            <option value="">All Locations</option>
            {locations.map(loc => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </div>

        {/* Sentiment Filter */}
        <div>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Sentiment:
          </label>
          <select 
            value={sentiment} 
            onChange={(e) => { setSentiment(e.target.value); setPage(1); }}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc', minWidth: '150px' }}
          >
            <option value="">All Sentiments</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
          </select>
        </div>

        {/* Text Search */}
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', flex: 1 }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Search:
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search review text..."
              style={{ 
                padding: '8px', 
                borderRadius: '4px', 
                border: '1px solid #ccc',
                width: '100%'
              }}
            />
          </div>
          <button 
            type="submit"
            style={{ 
              padding: '8px 16px', 
              backgroundColor: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer',
              alignSelf: 'flex-end'
            }}
          >
            Search
          </button>
        </form>

        {/* Clear Filters */}
        {(location || sentiment || searchQuery) && (
          <button
            onClick={() => {
              setLocation('');
              setSentiment('');
              setSearchQuery('');
              setPage(1);
            }}
            style={{
              padding: '8px 16px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              alignSelf: 'flex-end'
            }}
          >
            Clear All
          </button>
        )}
      </div>

      {/* Results Count */}
      <div style={{ marginBottom: '10px', color: '#666' }}>
        Showing {reviews.length} of {total} reviews
        {loading && <span> (loading...)</span>}
      </div>

      {/* Error Display */}
      {error && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#f8d7da', 
          color: '#721c24',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          Error: {error}
        </div>
      )}

      {/* Reviews Table */}
      {reviews.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
          No reviews found. Try adjusting your filters.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ 
            width: '100%', 
            borderCollapse: 'collapse',
            backgroundColor: 'white',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <thead>
              <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>ID</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Location</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Rating</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Review</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Sentiment</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Topic</th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 'bold' }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr 
                  key={review.id}
                  onClick={() => navigate(`/review/${review.id}`)}
                  style={{ 
                    borderBottom: '1px solid #dee2e6',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f8f9fa'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
                >
                  <td style={{ padding: '12px' }}>{review.id}</td>
                  <td style={{ padding: '12px', fontWeight: 'bold' }}>{review.location}</td>
                  <td style={{ padding: '12px', fontSize: '14px', color: '#ffc107' }}>
                    {getRatingStars(review.rating)} ({review.rating})
                  </td>
                  <td style={{ padding: '12px', maxWidth: '400px' }}>
                    <div style={{ 
                      overflow: 'hidden', 
                      textOverflow: 'ellipsis', 
                      whiteSpace: 'nowrap' 
                    }}>
                      {review.text}
                    </div>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: getSentimentColor(review.sentiment),
                      color: 'white',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}>
                      {review.sentiment || 'unknown'}
                    </span>
                  </td>
                  <td style={{ padding: '12px', fontSize: '14px' }}>
                    {review.topic || 'N/A'}
                  </td>
                  <td style={{ padding: '12px', fontSize: '14px', color: '#666' }}>
                    {new Date(review.date).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ 
          marginTop: '20px', 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          gap: '10px'
        }}>
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            style={{
              padding: '8px 16px',
              backgroundColor: page === 1 ? '#e9ecef' : '#007bff',
              color: page === 1 ? '#6c757d' : 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: page === 1 ? 'not-allowed' : 'pointer'
            }}
          >
            Previous
          </button>
          
          <span style={{ padding: '0 15px', fontWeight: 'bold' }}>
            Page {page} of {totalPages}
          </span>
          
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            style={{
              padding: '8px 16px',
              backgroundColor: page === totalPages ? '#e9ecef' : '#007bff',
              color: page === totalPages ? '#6c757d' : 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: page === totalPages ? 'not-allowed' : 'pointer'
            }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
