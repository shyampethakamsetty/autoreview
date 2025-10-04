"""
AI Client for sentiment analysis, topic extraction, and reply generation.
Supports OpenAI API (primary) and Hugging Face transformers (fallback).
"""
import os
from typing import Dict, List, Optional
import logging

# Configure logging to ensure INFO messages show up
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Check if OpenAI is available
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
USE_OPENAI = bool(OPENAI_API_KEY)

if USE_OPENAI:
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=180.0  # 3 minutes timeout for OpenAI requests
        )
        logger.info("OpenAI client initialized successfully - Primary AI provider ready")
    except Exception as e:
        logger.warning(f"OpenAI initialization failed: {e}")
        logger.info("Falling back to HuggingFace transformers as primary AI provider")
        USE_OPENAI = False
else:
    logger.info("OpenAI API key not configured - Using HuggingFace transformers as primary AI provider")

# Import for streaming
import json

# Lazy load transformers pipelines
_sentiment_pipeline = None
_topic_classifier = None
_reply_generator = None

def get_sentiment_pipeline():
    """Lazy load sentiment analysis pipeline"""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        logger.info("Loading DistilBERT sentiment model (first time may take 30-60s)...")
        from transformers import pipeline
        _sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        logger.info("DistilBERT sentiment pipeline loaded and ready")
    return _sentiment_pipeline

def get_reply_generator():
    """Lazy load lightweight conversational model for reply generation"""
    global _reply_generator
    if _reply_generator is None:
        logger.info("Loading DialoGPT-small for reply generation (first time may take 20-30s)...")
        from transformers import pipeline
        _reply_generator = pipeline(
            "conversational",
            model="microsoft/DialoGPT-small",
            pad_token_id=50256  # GPT-2 EOS token
        )
        logger.info("DialoGPT-small reply generator loaded and ready")
    return _reply_generator

def get_topic_classifier():
    """Lazy load zero-shot classification for topics"""
    global _topic_classifier
    if _topic_classifier is None:
        logger.info("Loading BART-Large-MNLI topic model (first time may take 60-90s)...")
        from transformers import pipeline
        _topic_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        logger.info("BART-Large-MNLI topic classifier loaded and ready")
    return _topic_classifier

# Removed duplicate get_reply_generator function - using conversational pipeline from line 51

def analyze_sentiment_local(text: str) -> str:
    """Analyze sentiment using local transformers model"""
    try:
        logger.info("Initializing HuggingFace sentiment pipeline...")
        pipeline = get_sentiment_pipeline()
        logger.info("Processing sentiment with DistilBERT model...")
        result = pipeline(text)[0]
        sentiment = 'positive' if result['label'] == 'POSITIVE' else 'negative'
        confidence = result['score']
        logger.info(f"HuggingFace sentiment analysis completed: {sentiment} (confidence: {confidence:.2f})")
        return sentiment
    except Exception as e:
        logger.error(f"HuggingFace sentiment analysis failed: {e}")
        return 'unknown'

def extract_topics_local(text: str) -> str:
    """Extract topics using zero-shot classification"""
    try:
        logger.info("Initializing HuggingFace topic classification pipeline...")
        classifier = get_topic_classifier()
        candidate_labels = ['food', 'service', 'ambience', 'price', 'cleanliness', 'staff']
        logger.info("Processing topic classification with BART-Large-MNLI model...")
        result = classifier(text, candidate_labels)
        topic = result['labels'][0]
        confidence = result['scores'][0]
        logger.info(f"HuggingFace topic extraction completed: {topic} (confidence: {confidence:.2f})")
        return topic
    except Exception as e:
        logger.error(f"HuggingFace topic extraction failed: {e}")
        return 'unknown'

def analyze_sentiment_with_fallback(text: str) -> str:
    """Analyze sentiment with OpenAI, fallback to local model"""
    if USE_OPENAI:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a sentiment analyzer. Respond with only 'positive', 'negative', or 'neutral'."},
                    {"role": "user", "content": f"Analyze the sentiment of this review: {text}"}
                ],
                max_tokens=10,
                temperature=0
            )
            result = response.choices[0].message.content.strip().lower()
            logger.info(f"OpenAI sentiment analysis successful: {result}")
            return result if result in ['positive', 'negative', 'neutral'] else 'neutral'
        except Exception as e:
            logger.warning(f"OpenAI sentiment analysis failed: {str(e)[:100]}...")
            logger.info("FALLBACK ACTIVATED: Switching to HuggingFace sentiment model")
    else:
        logger.info("OpenAI disabled, using HuggingFace sentiment model directly")
    
    return analyze_sentiment_local(text)

def extract_topics_with_fallback(text: str) -> str:
    """Extract topics with OpenAI, fallback to local model"""
    if USE_OPENAI:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a topic classifier for restaurant reviews. Respond with only one word from: food, service, ambience, price, cleanliness, staff."},
                    {"role": "user", "content": f"What is the main topic of this review: {text}"}
                ],
                max_tokens=10,
                temperature=0
            )
            result = response.choices[0].message.content.strip().lower()
            logger.info(f"OpenAI topic extraction successful: {result}")
            valid_topics = ['food', 'service', 'ambience', 'price', 'cleanliness', 'staff']
            return result if result in valid_topics else 'general'
        except Exception as e:
            logger.warning(f"OpenAI topic extraction failed: {str(e)[:100]}...")
            logger.info("FALLBACK ACTIVATED: Switching to HuggingFace topic classification model")
    else:
        logger.info("OpenAI disabled, using HuggingFace topic model directly")
    
    return extract_topics_local(text)

# Public API - these are the main functions called by the ingest API
def analyze_sentiment(text: str) -> str:
    """Public API: Analyze sentiment with OpenAI fallback to HuggingFace"""
    return analyze_sentiment_with_fallback(text)

def extract_topic(text: str) -> str:
    """Public API: Extract topic with OpenAI fallback to HuggingFace"""
    return extract_topics_with_fallback(text)

def generate_reply(review_text: str, location: str = "", rating: int = 3, 
                   sentiment: Optional[str] = None, topic: Optional[str] = None,
                   temperature: float = 0.2) -> Dict:
    """Generate contextual reply to review"""
    
    # Auto-detect sentiment and topic if not provided
    if sentiment is None:
        sentiment = analyze_sentiment(review_text)
    if topic is None:
        topic = extract_topic(review_text)
    
    reasoning = []
    
    # Determine response approach based on rating and sentiment
    if rating >= 4 or sentiment == 'positive':
        approach = "grateful and encouraging"
        reasoning.append(f"High rating ({rating}) or positive sentiment detected")
    elif rating <= 2 or sentiment == 'negative':
        approach = "apologetic and solution-focused"
        reasoning.append(f"Low rating ({rating}) or negative sentiment detected")
    else:
        approach = "balanced and appreciative"
        reasoning.append(f"Neutral rating ({rating}) or sentiment detected")
    
    # Build context-aware prompt
    location_context = f" at our {location} location" if location else ""
    
    if USE_OPENAI:
        try:
            system_prompt = f"""You are a professional restaurant manager responding to customer reviews. 
Be {approach}. Keep responses under 50 words. Be sincere and personal.
Topic focus: {topic}. Location: {location if location else 'our restaurant'}."""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Respond to this {rating}-star review{location_context}: {review_text}"}
                ],
                max_tokens=80,
                temperature=temperature
            )
            
            reply = response.choices[0].message.content.strip()
            reasoning.append("Generated using OpenAI GPT-3.5-turbo")
            
        except Exception as e:
            logger.warning(f"OpenAI reply generation failed: {str(e)[:100]}...")
            logger.info("FALLBACK ACTIVATED: Switching to lightweight LLM reply generation")
            # Try lightweight DialoGPT first
            try:
                reply = generate_llm_reply_local(review_text, rating, sentiment, topic, location)
                reasoning.append("Generated using DialoGPT-small fallback due to OpenAI failure")
            except Exception as llm_e:
                logger.warning(f"Lightweight LLM reply generation failed: {str(llm_e)[:100]}...")
                logger.info("FINAL FALLBACK ACTIVATED: Switching to template-based reply generation")
                reply = generate_template_reply(rating, sentiment, topic, location)
                reasoning.append("Generated using template fallback due to both OpenAI and LLM failure")
    else:
        logger.info("OpenAI disabled, trying lightweight LLM reply generation")
        try:
            reply = generate_llm_reply_local(review_text, rating, sentiment, topic, location)
            reasoning.append("Generated using DialoGPT-small (OpenAI not available)")
        except Exception as e:
            logger.warning(f"Lightweight LLM reply generation failed: {str(e)[:100]}...")
            logger.info("FINAL FALLBACK ACTIVATED: Using template-based reply generation")
            reply = generate_template_reply(rating, sentiment, topic, location)
            reasoning.append("Generated using template (both OpenAI and LLM not available)")
    
    return {
        "reply": reply,
        "tags": {"sentiment": sentiment, "topic": topic},
        "reasoning_log": reasoning
    }

def generate_llm_reply_local(review_text: str, rating: int, sentiment: str, topic: str, location: str) -> str:
    """Generate reply using lightweight DialoGPT-small model as local fallback"""
    
    logger.info(f"Generating local LLM reply for rating={rating}, sentiment={sentiment}, topic={topic}")
    
    try:
        logger.debug("About to load conversational model...")
        # Load the conversational model
        reply_generator = get_reply_generator()
        logger.debug("Reply generator loaded successfully")
        
        # Use direct conversation approach - simpler and more effective
        from transformers import Conversation
        conversation = Conversation()
        
        # Add the customer's review as user input
        conversation.add_user_input(review_text[:200])
        
        # Generate response with the model
        result = reply_generator(conversation)
        
        # Extract the reply - DialoGPT returns a Conversation object
        logger.debug(f"Result type: {type(result)}")
        if hasattr(result, 'generated_responses') and result.generated_responses:
            logger.debug(f"Generated responses: {result.generated_responses}")
            logger.debug(f"Last response type: {type(result.generated_responses[-1])}")
            reply = str(result.generated_responses[-1])
            logger.debug(f"Reply after str(): {reply} (type: {type(reply)})")
        else:
            reply = "Thank you for your feedback."
        
        # Post-process to make it more appropriate for a restaurant manager
        logger.debug(f"Before strip: {reply} (type: {type(reply)})")
        reply = reply.strip()
        logger.debug(f"After strip: {reply} (type: {type(reply)})")
        
        # Add context-appropriate prefix if the reply is too generic
        if reply.lower() in ["i'm sorry to hear that.", "i'm sorry about that.", "sorry to hear that."]:
            if rating <= 2:
                reply = f"I'm truly sorry to hear about your experience. {reply}"
            elif rating >= 4:
                reply = f"Thank you so much for your feedback! {reply}"
            else:
                reply = f"Thank you for letting us know. {reply}"
        
        # Ensure reasonable length
        if len(reply) > 120:
            sentences = reply.split('.')
            reply = sentences[0] + '.' if sentences and len(sentences[0]) > 10 else reply[:120]
        
        # Ensure it's not empty or too short
        if not reply or len(reply) < 10:
            reply = generate_template_reply(rating, sentiment, topic, location)
        
        logger.info(f"DialoGPT-small reply generated successfully")
        return reply
        
    except Exception as e:
        logger.warning(f"Lightweight LLM reply generation failed: {str(e)}")
        logger.info("FINAL FALLBACK ACTIVATED: Switching to template-based reply generation")
        return generate_template_reply(rating, sentiment, topic, location)

def generate_template_reply(rating: int, sentiment: str, topic: str, location: str) -> str:
    """Generate template-based reply as final fallback (Tier 3)
    
    Three-tier reply generation system:
    1. OpenAI GPT-3.5-turbo (primary, most contextual)
    2. DialoGPT-small (lightweight LLM fallback)  
    3. Template-based (final safety net, always works)
    """
    
    logger.info(f"Generating template reply for rating={rating}, sentiment={sentiment}, topic={topic}, location={location}")
    
    location_text = f" at {location}" if location else ""
    
    if rating >= 4 or sentiment == 'positive':
        if topic == 'ambience':
            reply = f"Thank you for the wonderful review! We're delighted you enjoyed the atmosphere{location_text}. Your feedback motivates our team!"
        elif topic == 'food':
            reply = f"We're thrilled you loved the food{location_text}! Thank you for choosing us and for taking time to share your experience."
        elif topic == 'service':
            reply = f"Thank you for recognizing our team's efforts{location_text}! We're so happy you had a great service experience."
        else:
            reply = f"Thank you for your wonderful review! We're thrilled you enjoyed your experience{location_text}."
    elif rating <= 2 or sentiment == 'negative':
        if topic == 'service':
            reply = f"We sincerely apologize for the service issues you experienced{location_text}. We're taking immediate steps to improve and would love the chance to make it right."
        elif topic == 'food':
            reply = f"We're sorry the food didn't meet your expectations{location_text}. We take quality seriously and are reviewing our processes to ensure this doesn't happen again."
        elif topic == 'ambience':
            reply = f"We apologize for the disappointing atmosphere{location_text}. We're working to improve the dining environment for all our guests."
        else:
            reply = f"We apologize for falling short of your expectations{location_text}. Your feedback is valuable and we're committed to doing better."
    else:
        reply = f"Thank you for your feedback{location_text}. We appreciate you taking the time to share your experience and are always working to improve."
    
    logger.info(f"Template reply generated: {reply[:50]}...")
    return reply

# Streaming response function for real-time UI
def generate_reply_stream(review_text: str, location: str = "", rating: int = 3):
    """Generate streaming reply for real-time UI updates"""
    if not USE_OPENAI:
        # Return complete response immediately if no streaming available
        result = generate_reply(review_text, location, rating)
        yield f"data: {json.dumps(result)}\n\n"
        return
    
    try:
        sentiment = analyze_sentiment(review_text)
        topic = extract_topic(review_text)
        
        approach = "grateful" if rating >= 4 else "apologetic" if rating <= 2 else "balanced"
        location_context = f" at our {location} location" if location else ""
        
        system_prompt = f"""You are a professional restaurant manager. Be {approach} and concise (under 50 words).
Topic focus: {topic}. Location: {location if location else 'our restaurant'}."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Respond to this {rating}-star review{location_context}: {review_text}"}
            ],
            max_tokens=80,
            temperature=0.2,
            stream=True
        )
        
        reply_parts = []
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                reply_parts.append(content)
                yield f"data: {json.dumps({'content': content, 'type': 'chunk'})}\n\n"
        
        # Send final result
        final_result = {
            "reply": "".join(reply_parts),
            "tags": {"sentiment": sentiment, "topic": topic},
            "type": "complete"
        }
        yield f"data: {json.dumps(final_result)}\n\n"
        
    except Exception as e:
        logger.error(f"Streaming reply failed: {e}")
        fallback_result = generate_reply(review_text, location, rating)
        yield f"data: {json.dumps(fallback_result)}\n\n"