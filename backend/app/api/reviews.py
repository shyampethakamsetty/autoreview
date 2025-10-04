from fastapi import APIRouter, Header, HTTPException, Path, Body, Query, Request
from typing import List, Optional
from sqlmodel import select, Session, col, func
from ..models import Review
from ..db import engine, init_db
from .. import ai_client
from ..middleware import limiter, AI_RATE_LIMIT
import os
import json

router = APIRouter()
API_KEY = os.getenv('API_KEY', 'supersecret')

@router.get('/reviews')
def list_reviews(
    x_api_key: str = Header(None),
    location: Optional[str] = Query(None, description="Filter by location"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (positive/negative/neutral)"),
    q: Optional[str] = Query(None, description="Search in review text"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating filter"),
    max_rating: Optional[int] = Query(None, ge=1, le=5, description="Maximum rating filter"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    topic: Optional[str] = Query(None, description="Filter by topic")
):
    """List reviews with filtering and pagination"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    init_db()
    with Session(engine) as session:
        # Build query with filters
        statement = select(Review)
        
        if location:
            statement = statement.where(col(Review.location) == location)
        
        if sentiment:
            statement = statement.where(col(Review.sentiment) == sentiment)
        
        if q:
            statement = statement.where(col(Review.text).contains(q))
        
        if topic:
            statement = statement.where(col(Review.topic) == topic)
        
        if min_rating is not None:
            statement = statement.where(col(Review.rating) >= min_rating)
        
        if max_rating is not None:
            statement = statement.where(col(Review.rating) <= max_rating)
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                statement = statement.where(col(Review.date) >= date_from_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail='Invalid date_from format. Use YYYY-MM-DD')
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                statement = statement.where(col(Review.date) <= date_to_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail='Invalid date_to format. Use YYYY-MM-DD')
        
        # Get total count before pagination - OPTIMIZED with COUNT(*)
        count_statement = select(func.count(Review.id))
        if location:
            count_statement = count_statement.where(col(Review.location) == location)
        if sentiment:
            count_statement = count_statement.where(col(Review.sentiment) == sentiment)
        if q:
            count_statement = count_statement.where(col(Review.text).contains(q))
        if topic:
            count_statement = count_statement.where(col(Review.topic) == topic)
        if min_rating is not None:
            count_statement = count_statement.where(col(Review.rating) >= min_rating)
        if max_rating is not None:
            count_statement = count_statement.where(col(Review.rating) <= max_rating)
        if date_from:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            count_statement = count_statement.where(col(Review.date) >= date_from_obj)
        if date_to:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            count_statement = count_statement.where(col(Review.date) <= date_to_obj)
        
        total = session.exec(count_statement).first()
        
        # Apply pagination
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)
        
        results = session.exec(statement).all()
        
        return {
            "reviews": results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

@router.get('/reviews/{review_id}', response_model=Review)
def get_review(review_id: str = Path(...), x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    # Validate that review_id is a valid integer
    try:
        review_id_int = int(review_id)
    except ValueError:
        raise HTTPException(status_code=404, detail='Not found')
    
    with Session(engine) as session:
        r = session.get(Review, review_id_int)
        if not r:
            raise HTTPException(status_code=404, detail='Not found')
        return r

@router.post('/reviews/{review_id}/suggest-reply')
@limiter.limit(AI_RATE_LIMIT)
def suggest_reply(
    request: Request,
    review_id: str, 
    payload: dict = Body({}), 
    x_api_key: str = Header(None)
):
    """Generate AI-powered reply suggestion for a review"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    # Validate that review_id is a valid integer
    try:
        review_id_int = int(review_id)
    except ValueError:
        raise HTTPException(status_code=404, detail='Not found')
    
    with Session(engine) as session:
        review = session.get(Review, review_id_int)
        if not review:
            raise HTTPException(status_code=404, detail='Not found')
        
        # Get temperature from payload
        temperature = payload.get('temperature', 0.2)
        
        # Ensure review has sentiment and topic
        if not review.sentiment:
            review.sentiment = ai_client.analyze_sentiment(review.text)
            session.add(review)
            session.commit()
            session.refresh(review)
        
        if not review.topic:
            review.topic = ai_client.extract_topic(review.text)
            session.add(review)
            session.commit()
            session.refresh(review)
        
        # Generate reply
        result = ai_client.generate_reply(
            review_text=review.text,
            location=review.location,
            rating=review.rating,
            sentiment=review.sentiment,
            topic=review.topic,
            temperature=temperature
        )
        
        return result

@router.post('/reviews/{review_id}/suggest-reply-stream')
@limiter.limit(AI_RATE_LIMIT)
def suggest_reply_stream(
    request: Request,
    review_id: int, 
    payload: dict = Body({}), 
    x_api_key: str = Header(None)
):
    """Generate AI-powered reply suggestion with streaming response"""
    from fastapi.responses import StreamingResponse
    from .. import ai_client
    
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    with Session(engine) as session:
        review = session.get(Review, review_id)
        if not review:
            raise HTTPException(status_code=404, detail='Not found')
        
        # Get temperature from payload
        temperature = payload.get('temperature', 0.2)
        
        # Ensure review has sentiment and topic
        if not review.sentiment:
            review.sentiment = ai_client.analyze_sentiment(review.text)
            session.add(review)
            session.commit()
            session.refresh(review)
        
        if not review.topic:
            review.topic = ai_client.extract_topic(review.text)
            session.add(review)
            session.commit()
            session.refresh(review)
        
        # Generate streaming response
        def generate():
            for chunk in ai_client.generate_reply_stream(
                review_text=review.text,
                location=review.location,
                rating=review.rating,
                sentiment=review.sentiment,
                topic=review.topic,
                temperature=temperature
            ):
                yield chunk
        
        return StreamingResponse(
            generate(), 
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )

@router.post('/reviews/bulk-reply')
@limiter.limit("5/minute")  # Very restrictive for bulk operations
def bulk_suggest_replies(
    request: Request,
    payload: dict = Body(...),
    x_api_key: str = Header(None)
):
    """Generate replies for multiple reviews in bulk"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    review_ids = payload.get('review_ids', [])
    temperature = payload.get('temperature', 0.2)
    max_bulk_size = 10  # Limit bulk operations
    
    if not review_ids:
        raise HTTPException(status_code=400, detail='No review_ids provided')
    
    if len(review_ids) > max_bulk_size:
        raise HTTPException(
            status_code=400, 
            detail=f'Bulk operation limited to {max_bulk_size} reviews at once'
        )
    
    results = []
    with Session(engine) as session:
        for review_id in review_ids:
            try:
                review = session.get(Review, review_id)
                if not review:
                    results.append({
                        'review_id': review_id,
                        'success': False,
                        'error': 'Review not found'
                    })
                    continue
                
                # Ensure review has sentiment and topic
                if not review.sentiment:
                    review.sentiment = ai_client.analyze_sentiment(review.text)
                    session.add(review)
                
                if not review.topic:
                    review.topic = ai_client.extract_topic(review.text)
                    session.add(review)
                
                session.commit()
                session.refresh(review)
                
                # Generate reply
                result = ai_client.generate_reply(
                    review_text=review.text,
                    location=review.location,
                    rating=review.rating,
                    sentiment=review.sentiment,
                    topic=review.topic,
                    temperature=temperature
                )
                
                results.append({
                    'review_id': review_id,
                    'success': True,
                    **result
                })
                
            except Exception as e:
                results.append({
                    'review_id': review_id,
                    'success': False,
                    'error': str(e)
                })
    
    return {
        'processed': len(results),
        'successful': len([r for r in results if r['success']]),
        'failed': len([r for r in results if not r['success']]),
        'results': results
    }

@router.get('/reviews/export')
@limiter.limit("10/minute")
def export_reviews(
    request: Request,
    format: str = Query('csv', pattern='^(csv|json)$'),
    x_api_key: str = Header(None),
    location: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None)
):
    """Export reviews in CSV or JSON format"""
    from fastapi.responses import Response
    import csv
    import io
    
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid API key')
    
    with Session(engine) as session:
        # Build query with filters
        statement = select(Review)
        
        if location:
            statement = statement.where(col(Review.location) == location)
        
        if sentiment:
            statement = statement.where(col(Review.sentiment) == sentiment)
        
        reviews = session.exec(statement).all()
        
        if format == 'csv':
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['id', 'location', 'rating', 'text', 'date', 'sentiment', 'topic'])
            
            # Write data
            for review in reviews:
                writer.writerow([
                    review.id,
                    review.location,
                    review.rating,
                    review.text,
                    review.date,
                    review.sentiment or '',
                    review.topic or ''
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            return Response(
                content=csv_content,
                media_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename=reviews.csv'}
            )
        
        else:  # JSON format
            reviews_data = [
                {
                    'id': review.id,
                    'location': review.location,
                    'rating': review.rating,
                    'text': review.text,
                    'date': str(review.date),
                    'sentiment': review.sentiment,
                    'topic': review.topic
                }
                for review in reviews
            ]
            
            return Response(
                content=json.dumps(reviews_data, indent=2),
                media_type='application/json',
                headers={'Content-Disposition': 'attachment; filename=reviews.json'}
            )
