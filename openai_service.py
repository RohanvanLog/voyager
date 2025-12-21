# openai_service.py
"""
OpenAI API integration for The Voyager application.
Handles AI-powered itinerary generation using GPT-5-nano model.
"""

import json
import openai
from config import Config


# ============================================================================
# CONFIGURATION
# ============================================================================

# Set the OpenAI API key from environment configuration
openai.api_key = Config.OPENAI_API_KEY

# Model configuration
MODEL_NAME = "gpt-5-nano"
TEMPERATURE = 0  # Deterministic output for consistent JSON structure


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

ITINERARY_SYSTEM_PROMPT = """You are TravelGPT, an expert AI travel planner. 
You must respond with valid JSON only, with no markdown formatting, no code blocks, and no extra text.
Your response must be a single JSON object with this exact structure:
{"days": [{"day": 1, "summary": "..."}, {"day": 2, "summary": "..."}, ...]}

Each summary should be a concise paragraph describing the day's activities, attractions, and recommendations.
Do not include any text before or after the JSON object."""

REGENERATE_DAY_SYSTEM_PROMPT = """You are TravelGPT, an expert AI travel planner.
You must respond with valid JSON only, with no markdown formatting, no code blocks, and no extra text.
Your response must be a single JSON object with this exact structure:
{"day": <number>, "summary": "..."}

The summary should be a concise paragraph describing the day's activities, attractions, and recommendations.
Do not include any text before or after the JSON object."""


# ============================================================================
# ITINERARY GENERATION
# ============================================================================

def generate_itinerary(destination, days, prefs):
    """
    Generate a complete multi-day travel itinerary using OpenAI GPT-5.
    
    Args:
        destination: The travel destination (city, country, or region)
        days: Number of days for the trip
        prefs: User preferences (dietary restrictions, interests, budget, etc.)
    
    Returns:
        dict: Parsed JSON with structure {"days": [{"day": 1, "summary": "..."}, ...]}
        None: If generation fails or response is invalid
    
    Raises:
        Exception: If API call fails or JSON parsing fails
    """
    # Build the user prompt
    if prefs and prefs.strip():
        user_message = (
            f"Plan a {days}-day trip to {destination}. "
            f"User preferences: {prefs}. "
            f"Provide the itinerary in the specified JSON format."
        )
    else:
        user_message = (
            f"Plan a {days}-day trip to {destination}. "
            f"Provide the itinerary in the specified JSON format."
        )
    
    try:
        # Call OpenAI ChatCompletion API
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": ITINERARY_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=TEMPERATURE,
            max_tokens=1500  # Sufficient for ~20-30 days with detailed summaries
        )
        
        # Extract the response content
        response_content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        itinerary_data = json.loads(response_content)
        
        # Validate the structure
        if not isinstance(itinerary_data, dict):
            print(f"Error: Response is not a dict: {itinerary_data}")
            return None
        
        if "days" not in itinerary_data:
            print(f"Error: Response missing 'days' key: {itinerary_data}")
            return None
        
        if not isinstance(itinerary_data["days"], list):
            print(f"Error: 'days' is not a list: {itinerary_data}")
            return None
        
        # Validate we got the correct number of days
        if len(itinerary_data["days"]) != days:
            print(f"Warning: Expected {days} days, got {len(itinerary_data['days'])}")
            # Still return it - we can handle partial results
        
        # Validate each day has required fields
        for day_data in itinerary_data["days"]:
            if "day" not in day_data or "summary" not in day_data:
                print(f"Error: Day missing required fields: {day_data}")
                return None
        
        return itinerary_data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response content: {response_content}")
        
        # Attempt to retry once with stricter prompt
        try:
            retry_message = (
                f"Plan a {days}-day trip to {destination}. "
                f"CRITICAL: Respond with ONLY valid JSON, no markdown, no code blocks. "
                f"Format: {{\"days\": [{{\"day\": 1, \"summary\": \"...\"}}, ...]}}. "
                f"Preferences: {prefs if prefs else 'none'}."
            )
            
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": ITINERARY_SYSTEM_PROMPT},
                    {"role": "user", "content": retry_message}
                ],
                temperature=TEMPERATURE,
                max_tokens=1500
            )
            
            response_content = response.choices[0].message.content.strip()
            itinerary_data = json.loads(response_content)
            
            # Quick validation
            if "days" in itinerary_data and isinstance(itinerary_data["days"], list):
                return itinerary_data
            else:
                return None
                
        except Exception as retry_error:
            print(f"Retry also failed: {retry_error}")
            return None
    
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None
    
    except Exception as e:
        print(f"Unexpected error in generate_itinerary: {e}")
        return None


# ============================================================================
# SINGLE DAY REGENERATION
# ============================================================================

def regenerate_day(destination, day_num, total_days, prefs):
    """
    Regenerate the itinerary for a single day of a trip.
    
    Args:
        destination: The travel destination
        day_num: The specific day number to regenerate (1-indexed)
        total_days: Total number of days in the trip (for context)
        prefs: User preferences for the trip
    
    Returns:
        dict: Parsed JSON with structure {"day": <num>, "summary": "..."}
        None: If generation fails or response is invalid
    
    Raises:
        Exception: If API call fails or JSON parsing fails
    """
    # Build the user prompt with context
    if prefs and prefs.strip():
        user_message = (
            f"Regenerate the itinerary for Day {day_num} of a {total_days}-day trip to {destination}. "
            f"User preferences: {prefs}. "
            f"Provide a fresh, alternative plan for this day in the specified JSON format."
        )
    else:
        user_message = (
            f"Regenerate the itinerary for Day {day_num} of a {total_days}-day trip to {destination}. "
            f"Provide a fresh, alternative plan for this day in the specified JSON format."
        )
    
    try:
        # Call OpenAI ChatCompletion API
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": REGENERATE_DAY_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=TEMPERATURE,
            max_tokens=300  # Single day needs less tokens
        )
        
        # Extract the response content
        response_content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        day_data = json.loads(response_content)
        
        # Validate the structure
        if not isinstance(day_data, dict):
            print(f"Error: Response is not a dict: {day_data}")
            return None
        
        if "day" not in day_data or "summary" not in day_data:
            print(f"Error: Response missing required fields: {day_data}")
            return None
        
        # Validate the day number matches
        if day_data["day"] != day_num:
            print(f"Warning: Expected day {day_num}, got day {day_data['day']}")
            # Correct it to match what was requested
            day_data["day"] = day_num
        
        return day_data
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response content: {response_content}")
        return None
    
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None
    
    except Exception as e:
        print(f"Unexpected error in regenerate_day: {e}")
        return None