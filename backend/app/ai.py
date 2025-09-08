import re
import random
from typing import List, Optional, Dict, Any

# very simple keyword extractor placeholder
def extract_keywords(text: str, k: int = 5) -> List[str]:
    words = re.findall(r"[A-Za-z0-9_]+", text.lower())
    freq = {}
    for w in words:
        if len(w) < 3: continue
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]

# simple "AI" summarizer stub (replace with real LLM call)
async def summarize(text: str) -> str:
    return f"Life Moment: {text[:160]}..." if len(text) > 160 else f"Life Moment: {text}"

# TODO: This code demonstrates using multiple AI processes from different sources.
# The create_first_person_summary function below uses AWS Rekognition + OpenAI text-based analysis,
# while create_timeline_narrative uses GPT-4 Vision for direct image analysis.

def create_first_person_summary(
    caption: str, 
    labels: List[Dict[str, Any]] = None, 
    location_info: Dict[str, Any] = None,
    faces: List[Dict[str, Any]] = None,
    ocr_text: str = "",
    heic_metadata: Dict[str, Any] = None,
    user_profile: Dict[str, Any] = None
) -> str:
    """
    Generate a first-person narrative summary from image analysis data.
    This is a demo stub - in production would use actual LLM.
    """
    
    # Extract key elements
    labels = labels or []
    faces = faces or []
    face_count = len(faces)
    user_profile = user_profile or {}
    
    # Determine if this seems like an interesting or mundane photo
    interesting_labels = {
        'celebration', 'party', 'wedding', 'birthday', 'vacation', 'travel',
        'restaurant', 'beach', 'mountain', 'sunset', 'ceremony', 'graduation',
        'concert', 'festival', 'sports', 'game', 'performance'
    }
    
    detected_labels = [label.get('name', '').lower() for label in labels[:5]]
    is_interesting = any(interesting in ' '.join(detected_labels) for interesting in interesting_labels)
    
    # Template-based first-person narratives
    if caption and len(caption.strip()) > 3:
        # Use the caption as primary context
        base_caption = caption.strip()
        
        # Add location context if available
        if location_info and location_info.get('city'):
            city = location_info.get('city')
            country = location_info.get('country', '')
            if city and country and country.lower() != 'united states':
                location_context = f" in {city}, {country}"
            elif city:
                location_context = f" in {city}"
            else:
                location_context = ""
        else:
            location_context = ""
            
        # Add people context
        if face_count == 1:
            people_context = " with someone special"
        elif face_count == 2:
            people_context = " with a friend"
        elif face_count > 2:
            people_context = f" with {face_count - 1} others"  # -1 assuming one is the person taking photo
        else:
            people_context = ""
            
        # Create first-person narrative
        if is_interesting:
            return f"{base_caption}{location_context}{people_context}. One of those moments worth remembering."
        else:
            return f"{base_caption}{location_context}{people_context}."
    
    # Fallback for photos without good captions
    fallbacks = []
    
    # Location-based fallbacks with profile context
    if location_info and location_info.get('city'):
        city = location_info.get('city')
        user_city = user_profile.get('city', '')
        
        if city.lower() != user_city.lower():
            # Away from home
            fallbacks.extend([
                f"Visiting {city} today.",
                f"Exploring {city}.",
                f"Trip to {city} - good to get away from {user_city}."
            ])
        else:
            # At home
            fallbacks.extend([
                f"Out and about in {city}.",
                f"Another day in {city}.",
                f"Home sweet {city}."
            ])
        
    # Activity-based fallbacks from labels with profile context
    if 'restaurant' in ' '.join(detected_labels):
        # Add context based on occupation/interests
        if 'cooking' in user_profile.get('interests', []):
            fallbacks.extend([
                "Decided to let someone else do the cooking tonight.",
                "Taking a break from my own kitchen.",
                "Good food and good company - sometimes you need a night off."
            ])
        else:
            fallbacks.extend([
                "Had a nice meal out.",
                "Dinner out tonight.",
                "Good food and good company."
            ])
    elif 'beach' in ' '.join(detected_labels):
        fallbacks.extend([
            "Beach day - exactly what I needed.",
            "Nothing beats a day by the water.",
            "Sandy toes and salty air."
        ])
    elif any(word in ' '.join(detected_labels) for word in ['nature', 'tree', 'outdoor']):
        # Add context based on hiking interest
        if 'hiking' in user_profile.get('interests', []):
            fallbacks.extend([
                "Back on the trails again.",
                "Nothing beats getting out in nature.",
                "My happy place - away from the screen."
            ])
        else:
            fallbacks.extend([
                "Getting some fresh air.",
                "Nature walk to clear my head.",
                "Sometimes you just need to be outside."
            ])
    elif 'home' in ' '.join(detected_labels) or 'room' in ' '.join(detected_labels):
        fallbacks.extend([
            "Quiet moment at home.",
            "Just another day.",
            "Home sweet home."
        ])
    
    # People-based fallbacks
    if face_count > 1:
        fallbacks.extend([
            "Good times with good people.",
            "Caught up with friends today.",
            "These are the moments that matter."
        ])
    elif face_count == 1:
        fallbacks.extend([
            "A moment with someone special.",
            "Good company makes everything better."
        ])
    
    # Generic fallbacks for mundane photos
    generic_fallbacks = [
        "A moment from today.",
        "Life happening.",
        "Just a regular day.",
        "Another memory captured.",
        "This moment felt worth saving."
    ]
    
    # Choose appropriate fallback
    if fallbacks:
        return random.choice(fallbacks)
    else:
        return random.choice(generic_fallbacks)

def generate_clarification_questions(
    labels: List[Dict[str, Any]] = None,
    location_info: Dict[str, Any] = None,
    faces: List[Dict[str, Any]] = None,
    ocr_text: str = "",
    user_profile: Dict[str, Any] = None
) -> List[str]:
    """
    Generate up to 2 clarification questions for ambiguous photos.
    Returns empty list if photo seems clear enough.
    """
    labels = labels or []
    faces = faces or []
    user_profile = user_profile or {}
    detected_labels = [label.get('name', '').lower() for label in labels[:5]]
    
    questions = []
    
    # Event-related questions based on visual cues
    if any(word in ' '.join(detected_labels) for word in ['formal', 'dress', 'suit', 'flower']):
        questions.append("What special event is this?")
    
    if 'cake' in ' '.join(detected_labels) and 'candle' in ' '.join(detected_labels):
        questions.append("Whose birthday celebration is this?")
    
    if any(word in ' '.join(detected_labels) for word in ['stage', 'crowd', 'performance']):
        questions.append("What show or performance is this?")
    
    # Location context questions
    if location_info and location_info.get('city'):
        city = location_info.get('city')
        user_city = user_profile.get('city', '')
        if city.lower() != user_city.lower():
            questions.append(f"What brings you to {city}?")
    
    # People context questions
    if len(faces) == 2:
        partner_name = user_profile.get('relationships', {}).get('partner', 'someone special')
        questions.append(f"Who is with you in this photo?")
    elif len(faces) > 2:
        questions.append("Who are you with in this photo?")
    
    # Activity questions based on objects/context
    if 'food' in ' '.join(detected_labels) and 'kitchen' in ' '.join(detected_labels):
        if 'cooking' in user_profile.get('interests', []):
            questions.append("What are you cooking?")
    
    if any(word in ' '.join(detected_labels) for word in ['mountain', 'trail', 'backpack']):
        if 'hiking' in user_profile.get('interests', []):
            questions.append("Where are you hiking?")
    
    # Return max 2 questions
    return questions[:2]


def create_timeline_narrative(
    image_bytes: bytes,
    caption: str = "",
    photo_datetime: str = "",
    location_info: Dict[str, Any] = None,
    user_profile: Dict[str, Any] = None
) -> str:
    """
    Generate a friendly journalist-style narrative using GPT-4 Vision.
    Analyzes the image directly and creates contextually aware descriptions.
    """
    import base64
    import json
    from datetime import datetime
    from openai import OpenAI
    from .settings import settings
    
    if not settings.openai_api_key:
        return "A moment captured in time."
    
    try:
        # Encode image for GPT-4 Vision
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Parse datetime for smart context
        day_of_week = ""
        time_context = ""
        if photo_datetime:
            try:
                dt = datetime.fromisoformat(photo_datetime.replace('Z', '+00:00'))
                day_of_week = dt.strftime('%A')
                hour = dt.hour
                if 9 <= hour <= 17:
                    time_context = "during work hours"
                elif 17 < hour <= 21:
                    time_context = "in the evening"
                elif 6 <= hour < 9:
                    time_context = "in the morning"
                else:
                    time_context = "late at night"
            except:
                pass
        
        # Build context
        user_name = user_profile.get('name', 'User') if user_profile else 'User'
        user_age = user_profile.get('age', '') if user_profile else ''
        occupation = user_profile.get('occupation', '') if user_profile else ''
        city = user_profile.get('city', '') if user_profile else ''
        interests = ', '.join(user_profile.get('interests', [])) if user_profile else ''
        
        location_text = ""
        if location_info:
            if location_info.get('city') and location_info.get('city').lower() != city.lower():
                location_text = f"while visiting {location_info.get('city')}"
            elif location_info.get('address'):
                # Local location
                location_text = f"at {location_info.get('city', 'a local spot')}"
        
        caption_text = f'Caption: "{caption}"' if caption else "No caption provided"
        
        prompt = f"""Analyze this photo and create a friendly journalist-style description of this moment in {user_name}'s life.

CONTEXT DATA:
- Date/Time: {photo_datetime} ({day_of_week} {time_context}) 
- Location: {location_text or 'location unknown'}
- User: {user_name}{f', {user_age}' if user_age else ''}{f', {occupation}' if occupation else ''}{f' in {city}' if city else ''}
- Interests: {interests or 'not specified'}
- {caption_text}

SMART INFERENCE RULES:
- Weekday 9am-5pm + outdoor scene = likely break from work
- Weekend + activity = recreational/personal time  
- Evening + restaurant/social = dinner/social time
- Travel location ≠ home city = trip context
- Consider visible weather, lighting, season
- Use relationships context if multiple people visible

Create a 1-2 sentence description that:
1. Uses third person with {user_name}'s name
2. Makes reasonable assumptions about the context/timing
3. Stays factual but warm in tone
4. Incorporates what you can see in the image
5. Avoids putting emotional words in {user_name}'s mouth

Example good outputs:
- "{user_name} stepped away from his desk for a lunchtime walk through the park on Tuesday afternoon"  
- "{user_name} and Sam enjoyed dinner at a neighborhood restaurant on Saturday evening"
- "{user_name} captured the sunrise during an early morning hike before starting his workday"
"""

        client = OpenAI(api_key=settings.openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        narrative = response.choices[0].message.content.strip()
        return narrative if narrative else "A moment from this day."
        
    except Exception as e:
        print(f"GPT-4 Vision narrative generation failed: {e}")
        return "A moment captured during the day."