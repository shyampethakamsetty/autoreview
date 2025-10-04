import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { api, handleApiError } from '../api/client';
import type { AnalyticsResponse } from '../types';

export default function Analytics() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const analyticsData = await api.getAnalytics();
        setData(analyticsData);
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#f8d7da', 
          color: '#721c24',
          borderRadius: '8px'
        }}>
          Error: {error}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ padding: '20px' }}>
        <div>No analytics data available</div>
      </div>
    );
  }

  // Transform data for charts
  const sentimentData = Object.entries(data.sentiment_counts).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    fill: name === 'positive' ? '#28a745' : name === 'negative' ? '#dc3545' : '#6c757d'
  }));

  const topicData = Object.entries(data.topic_counts)
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value
    }));

  const locationData = Object.entries(data.location_counts)
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({
      name,
      value
    }));

  const ratingData = Object.entries(data.rating_distribution)
    .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
    .map(([name, value]) => ({
      name: `${name} Star${name === '1' ? '' : 's'}`,
      value
    }));

  return (
    <div style={{ padding: '20px' }}>
      <h2>Analytics Dashboard</h2>

      {/* Summary Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        marginBottom: '30px'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
            Total Reviews
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#007bff' }}>
            {data.total}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
            Average Rating
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#ffc107' }}>
            {data.average_rating.toFixed(2)}
            <span style={{ fontSize: '18px', marginLeft: '5px' }}>/ 5</span>
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
            Positive Reviews
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#28a745' }}>
            {data.sentiment_counts.positive || 0}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
            Negative Reviews
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc3545' }}>
            {data.sentiment_counts.negative || 0}
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '20px'
      }}>
        {/* Sentiment Distribution */}
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Sentiment Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sentimentData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Topic Distribution */}
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Topic Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topicData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#007bff" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Location Distribution */}
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Location Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={locationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#17a2b8" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Rating Distribution */}
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Rating Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={ratingData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#ffc107" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Breakdown Tables */}
      <div style={{ marginTop: '30px' }}>
        <h3>Detailed Breakdown</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px'
        }}>
          {/* Sentiment Table */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h4 style={{ marginTop: 0 }}>Sentiments</h4>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                {Object.entries(data.sentiment_counts).map(([sentiment, count]) => (
                  <tr key={sentiment} style={{ borderBottom: '1px solid #dee2e6' }}>
                    <td style={{ padding: '10px', textTransform: 'capitalize' }}>{sentiment}</td>
                    <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold' }}>{count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Topic Table */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h4 style={{ marginTop: 0 }}>Topics</h4>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                {Object.entries(data.topic_counts)
                  .sort((a, b) => b[1] - a[1])
                  .map(([topic, count]) => (
                    <tr key={topic} style={{ borderBottom: '1px solid #dee2e6' }}>
                      <td style={{ padding: '10px', textTransform: 'capitalize' }}>{topic}</td>
                      <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold' }}>{count}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>

          {/* Location Table */}
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h4 style={{ marginTop: 0 }}>Locations</h4>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                {Object.entries(data.location_counts)
                  .sort((a, b) => b[1] - a[1])
                  .map(([location, count]) => (
                    <tr key={location} style={{ borderBottom: '1px solid #dee2e6' }}>
                      <td style={{ padding: '10px' }}>{location}</td>
                      <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold' }}>{count}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
