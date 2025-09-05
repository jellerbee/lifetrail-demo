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
        questions.append("Is this a wedding or special celebration?")
    
    if 'cake' in ' '.join(detected_labels) and 'candle' in ' '.join(detected_labels):
        questions.append("Is this a birthday celebration?")
    
    if any(word in ' '.join(detected_labels) for word in ['stage', 'crowd', 'performance']):
        questions.append("Are you performing or watching a show?")
    
    # Location context questions
    if location_info and location_info.get('city'):
        city = location_info.get('city')
        user_city = user_profile.get('city', '')
        if city.lower() != user_city.lower():
            questions.append(f"Are you visiting {city} for work or pleasure?")
    
    # People context questions
    if len(faces) == 2:
        partner_name = user_profile.get('relationships', {}).get('partner', 'someone special')
        questions.append(f"Is this with {partner_name}?")
    elif len(faces) > 2:
        questions.append("Is this a family gathering or friends meetup?")
    
    # Activity questions based on objects/context
    if 'food' in ' '.join(detected_labels) and 'kitchen' in ' '.join(detected_labels):
        if 'cooking' in user_profile.get('interests', []):
            questions.append("Did you cook this yourself?")
    
    if any(word in ' '.join(detected_labels) for word in ['mountain', 'trail', 'backpack']):
        if 'hiking' in user_profile.get('interests', []):
            questions.append("Which trail is this from?")
    
    # Return max 2 questions
    return questions[:2]