import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api, handleApiError } from '../api/client';
import type { Review, AIReplyResponse } from '../types';

export default function ReviewDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [aiReply, setAiReply] = useState<AIReplyResponse | null>(null);
  const [generatingReply, setGeneratingReply] = useState(false);
  const [replyError, setReplyError] = useState<string | null>(null);
  const [temperature, setTemperature] = useState(0.2);
  const [showReasoning, setShowReasoning] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  useEffect(() => {
    const fetchReview = async () => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const data = await api.getReview(parseInt(id));
        setReview(data);
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setLoading(false);
      }
    };

    fetchReview();
  }, [id]);

  const generateReply = async () => {
    if (!id) return;
    setGeneratingReply(true);
    setReplyError(null);
    try {
      const response = await api.suggestReply(parseInt(id), temperature);
      setAiReply(response);
    } catch (err) {
      setReplyError(handleApiError(err));
    } finally {
      setGeneratingReply(false);
    }
  };

  const copyToClipboard = () => {
    if (aiReply?.reply) {
      navigator.clipboard.writeText(aiReply.reply);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const getSentimentColor = (sentiment?: string | null) => {
    switch (sentiment) {
      case 'positive': return '#28a745';
      case 'negative': return '#dc3545';
      case 'neutral': return '#6c757d';
      default: return '#adb5bd';
    }
  };

  const getRatingStars = (rating: number) => {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating);
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Loading review...</div>
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
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          Error: {error}
        </div>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Back to Inbox
        </button>
      </div>
    );
  }

  if (!review) {
    return (
      <div style={{ padding: '20px' }}>
        <div>Review not found</div>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
        >
          Back to Inbox
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      {/* Back Button */}
      <button
        onClick={() => navigate('/')}
        style={{
          padding: '8px 16px',
          backgroundColor: '#6c757d',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          marginBottom: '20px'
        }}
      >
        ← Back to Inbox
      </button>

      <h2>Review Details</h2>

      {/* Review Card */}
      <div style={{ 
        backgroundColor: 'white', 
        padding: '25px', 
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        {/* Header Info */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'flex-start',
          marginBottom: '20px',
          flexWrap: 'wrap',
          gap: '10px'
        }}>
          <div>
            <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>
              Review ID: #{review.id}
            </div>
            <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '5px' }}>
              {review.location}
            </div>
            <div style={{ fontSize: '20px', color: '#ffc107' }}>
              {getRatingStars(review.rating)} ({review.rating}/5)
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '14px', color: '#666' }}>
              {new Date(review.date).toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
          </div>
        </div>

        {/* Tags */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
          <div>
            <strong>Sentiment:</strong>{' '}
            <span style={{
              padding: '4px 12px',
              borderRadius: '4px',
              backgroundColor: getSentimentColor(review.sentiment),
              color: 'white',
              fontSize: '14px',
              fontWeight: 'bold',
              marginLeft: '5px'
            }}>
              {review.sentiment || 'unknown'}
            </span>
          </div>
          <div>
            <strong>Topic:</strong>{' '}
            <span style={{
              padding: '4px 12px',
              borderRadius: '4px',
              backgroundColor: '#007bff',
              color: 'white',
              fontSize: '14px',
              marginLeft: '5px'
            }}>
              {review.topic || 'N/A'}
            </span>
          </div>
        </div>

        {/* Review Text */}
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#f8f9fa', 
          borderRadius: '8px',
          borderLeft: '4px solid #007bff'
        }}>
          <div style={{ fontSize: '16px', lineHeight: '1.6' }}>
            {review.text}
          </div>
        </div>
      </div>

      {/* AI Reply Generation Section */}
      <div style={{ 
        backgroundColor: 'white', 
        padding: '25px', 
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ marginTop: 0 }}>AI-Powered Reply Suggestion</h3>

        {/* Temperature Control */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
            Temperature: {temperature.toFixed(1)}
            <span style={{ fontSize: '12px', fontWeight: 'normal', marginLeft: '10px', color: '#666' }}>
              (0.0 = Conservative, 1.0 = Creative)
            </span>
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            style={{ width: '100%', maxWidth: '400px' }}
          />
        </div>

        {/* Generate Button */}
        <button
          onClick={generateReply}
          disabled={generatingReply}
          style={{
            padding: '12px 24px',
            backgroundColor: generatingReply ? '#6c757d' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: generatingReply ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 'bold'
          }}
        >
          {generatingReply ? 'Generating Reply...' : '✨ Suggest Reply'}
        </button>

        {/* Reply Error */}
        {replyError && (
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#f8d7da', 
            color: '#721c24',
            borderRadius: '8px',
            marginTop: '20px'
          }}>
            Error: {replyError}
          </div>
        )}

        {/* Generated Reply */}
        {aiReply && (
          <div style={{ marginTop: '20px' }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '10px'
            }}>
              <h4 style={{ margin: 0 }}>Suggested Reply:</h4>
              <button
                onClick={copyToClipboard}
                style={{
                  padding: '8px 16px',
                  backgroundColor: copySuccess ? '#28a745' : '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                {copySuccess ? '✓ Copied!' : '📋 Copy'}
              </button>
            </div>

            <textarea
              value={aiReply.reply}
              readOnly
              style={{
                width: '100%',
                minHeight: '120px',
                padding: '15px',
                borderRadius: '8px',
                border: '2px solid #007bff',
                fontSize: '15px',
                lineHeight: '1.6',
                fontFamily: 'inherit',
                resize: 'vertical'
              }}
            />

            {/* AI Tags */}
            <div style={{ 
              display: 'flex', 
              gap: '15px', 
              marginTop: '15px',
              padding: '15px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px'
            }}>
              <div>
                <strong>Detected Sentiment:</strong>{' '}
                <span style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  backgroundColor: getSentimentColor(aiReply.tags.sentiment),
                  color: 'white',
                  fontSize: '13px',
                  marginLeft: '5px'
                }}>
                  {aiReply.tags.sentiment}
                </span>
              </div>
              <div>
                <strong>Detected Topic:</strong>{' '}
                <span style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  backgroundColor: '#007bff',
                  color: 'white',
                  fontSize: '13px',
                  marginLeft: '5px'
                }}>
                  {aiReply.tags.topic}
                </span>
              </div>
            </div>

            {/* Reasoning Log */}
            {aiReply.reasoning_log && aiReply.reasoning_log.length > 0 && (
              <div style={{ marginTop: '15px' }}>
                <button
                  onClick={() => setShowReasoning(!showReasoning)}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  {showReasoning ? '▼ Hide Reasoning' : '▶ Show Reasoning'}
                </button>

                {showReasoning && (
                  <div style={{
                    marginTop: '10px',
                    padding: '15px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '8px',
                    borderLeft: '4px solid #6c757d'
                  }}>
                    <h5 style={{ marginTop: 0, marginBottom: '10px' }}>AI Reasoning:</h5>
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      {aiReply.reasoning_log.map((log, idx) => (
                        <li key={idx} style={{ marginBottom: '5px', fontSize: '14px' }}>
                          {log}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
