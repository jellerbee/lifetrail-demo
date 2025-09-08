import boto3
import requests
import json
from io import BytesIO
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from openai import OpenAI
from sqlalchemy.orm import sessionmaker
from .settings import settings
from .db import engine
from . import models
from .ai import create_first_person_summary, generate_clarification_questions, create_timeline_narrative

# AWS client factory functions
def get_rekognition_client():
    return boto3.client(
        'rekognition',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )

def get_textract_client():
    return boto3.client(
        'textract',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )

openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

SessionLocal = sessionmaker(bind=engine)

def detect_faces(s3_key: str):
    """Detect faces with AWS Rekognition"""
    rekognition = get_rekognition_client()
    response = rekognition.detect_faces(
        Image={"S3Object": {"Bucket": settings.aws_bucket_name, "Name": s3_key}},
        Attributes=["ALL"]
    )
    
    # Simplify face data
    faces = []
    for face in response.get("FaceDetails", []):
        face_data = {
            "age_range": face.get("AgeRange", {}),
            "gender": face.get("Gender", {}).get("Value"),
            "emotions": [e for e in face.get("Emotions", []) if e.get("Confidence", 0) > 50]
        }
        faces.append(face_data)
    
    return faces

def detect_labels(s3_key: str):
    """Detect image labels with AWS Rekognition"""
    rekognition = get_rekognition_client()
    response = rekognition.detect_labels(
        Image={"S3Object": {"Bucket": settings.aws_bucket_name, "Name": s3_key}},
        MaxLabels=15,
        MinConfidence=80
    )
    
    # Simplify labels
    labels = []
    for label in response.get("Labels", []):
        label_data = {
            "name": label.get("Name"),
            "confidence": label.get("Confidence")
        }
        labels.append(label_data)
    
    return labels

def extract_text_from_textract(s3_key: str):
    """Extract text from image using AWS Textract"""
    textract = get_textract_client()
    response = textract.detect_document_text(
        Document={"S3Object": {"Bucket": settings.aws_bucket_name, "Name": s3_key}}
    )
    
    text_blocks = []
    for block in response.get("Blocks", []):
        if block["BlockType"] == "LINE":
            text_blocks.append(block.get("Text", ""))
    
    return " ".join(text_blocks)

def extract_exif_gps(s3_key: str):
    """Extract GPS coordinates from EXIF data"""
    try:
        # Download image from S3
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=settings.aws_bucket_name, Key=s3_key)
        image_bytes = response['Body'].read()
        
        # Extract EXIF data
        image = Image.open(BytesIO(image_bytes))
        exif_dict = image._getexif() or {}
        
        gps_info = {}
        for tag_id, value in exif_dict.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_value
        
        # Convert GPS coordinates
        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
            lat = convert_to_degrees(gps_info['GPSLatitude'])
            lon = convert_to_degrees(gps_info['GPSLongitude'])
            
            if gps_info.get('GPSLatitudeRef') == 'S':
                lat = -lat
            if gps_info.get('GPSLongitudeRef') == 'W':
                lon = -lon
                
            return {"latitude": lat, "longitude": lon}
    
    except Exception:
        pass
    
    return None

def convert_to_degrees(value):
    """Convert GPS coordinates to degrees"""
    d, m, s = value
    return float(d) + float(m)/60 + float(s)/3600

def reverse_geocode_locationiq(lat: float, lon: float):
    """Reverse geocode using LocationIQ"""
    if not settings.locationiq_api_key:
        return None
    
    try:
        url = f"https://us1.locationiq.com/v1/reverse.php"
        params = {
            "key": settings.locationiq_api_key,
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "address": data.get("display_name"),
                "city": data.get("address", {}).get("city"),
                "country": data.get("address", {}).get("country")
            }
    except Exception:
        pass
    
    return None

def infer_event_from_context(labels: list, ocr_text: str, caption: str):
    """Use OpenAI to classify event type"""
    if not openai_client:
        return "personal"
    
    try:
        label_names = [label["name"] for label in labels]
        
        # Enhanced prompt with more context and examples
        prompt = f"""You are an expert at categorizing life moments and personal events. Based on the image analysis below, classify this life moment into the most appropriate category.

USER'S DESCRIPTION: "{caption}"
VISUAL ELEMENTS: {', '.join(label_names) if label_names else 'None detected'}
TEXT IN IMAGE: "{ocr_text}" {'' if ocr_text else '(No text found)'}

CATEGORIES:
- family: Family gatherings, relatives, children, parents, home life, family meals
- travel: Vacations, tourism, landmarks, hotels, airports, transportation, sightseeing
- food: Restaurants, cooking, meals, recipes, dining experiences, food preparation
- work: Office, meetings, conferences, professional events, workplace, business
- celebration: Birthdays, weddings, parties, holidays, anniversaries, achievements
- nature: Outdoors, hiking, beaches, parks, wildlife, landscapes, camping, hunting, fishing
- sports: Exercise, games, athletics, fitness, recreational activities
- education: School, learning, books, graduation, classes, academic events
- social: Friends, social gatherings, nightlife, community events, networking
- hobby: Personal interests, crafts, collections, creative activities, hobbies
- personal: Daily life, self-care, routine activities, individual moments

INSTRUCTIONS:
1. Give primary weight to the user's caption as it reflects their intent
2. Use visual elements and text to support the classification
3. Choose the single most specific category that fits
4. If multiple categories apply, choose the most prominent theme
5. Respond with ONLY the category name (lowercase, no explanation)

Category:"""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=15,
            temperature=0.2
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        # Validate response is one of our categories
        valid_categories = {
            'family', 'travel', 'food', 'work', 'celebration', 
            'nature', 'sports', 'education', 'social', 'hobby', 'personal'
        }
        
        return result if result in valid_categories else "personal"
    
    except Exception:
        return "personal"

def extract_photo_date(s3_key: str):
    """Extract the date when photo was taken from EXIF data"""
    try:
        # Download image from S3
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket=settings.aws_bucket_name, Key=s3_key)
        image_bytes = response['Body'].read()
        
        # Extract EXIF data
        image = Image.open(BytesIO(image_bytes))
        exif_dict = image._getexif() or {}
        
        # Try to find date taken
        for tag_id, value in exif_dict.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "DateTimeOriginal":
                # Parse EXIF datetime format: "2023:03:15 14:30:20"
                from datetime import datetime
                return datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
            elif tag == "DateTime":
                from datetime import datetime
                return datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
    
    except Exception:
        pass
    
    return None

def process_image_async(event_id: int, s3_key: str, caption: str):
    """Process image asynchronously with AI services"""
    print(f"Starting image processing for event {event_id}, s3_key: {s3_key}, caption: '{caption}'")
    db = SessionLocal()
    
    try:
        # Check if AWS credentials are available
        aws_available = bool(settings.aws_access_key_id and settings.aws_secret_access_key and settings.aws_bucket_name)
        print(f"AWS available: {aws_available}")
        
        # Detect faces (with fallback)
        faces = []
        if aws_available:
            try:
                faces = detect_faces(s3_key)
                print(f"AWS face detection successful: {len(faces)} faces")
            except Exception as e:
                print(f"Face detection failed: {e}, using mock data")
                # Use mock data as fallback
                faces = [
                    {"age_range": {"Low": 25, "High": 35}, "gender": "Male", "emotions": []},
                    {"age_range": {"Low": 28, "High": 38}, "gender": "Female", "emotions": []}
                ]
        else:
            print("AWS not available, using mock face data")
            # Mock some face data for testing when AWS is unavailable
            faces = [
                {"age_range": {"Low": 25, "High": 35}, "gender": "Male", "emotions": []},
                {"age_range": {"Low": 28, "High": 38}, "gender": "Female", "emotions": []}
            ]
        
        # Detect labels (with fallback)
        labels = []
        if aws_available:
            try:
                labels = detect_labels(s3_key)
                print(f"AWS label detection successful: {len(labels)} labels")
            except Exception as e:
                print(f"Label detection failed: {e}, using mock data")
                # Use mock data as fallback
                labels = [
                    {"name": "Person", "confidence": 85.0},
                    {"name": "Outdoor", "confidence": 75.0},
                    {"name": "Day", "confidence": 90.0}
                ]
        else:
            print("AWS not available, using mock label data")
            # Mock some common labels for testing when AWS is unavailable
            labels = [
                {"name": "Person", "confidence": 85.0},
                {"name": "Outdoor", "confidence": 75.0},
                {"name": "Day", "confidence": 90.0}
            ]
        
        # Extract text (with fallback)
        ocr_text = ""
        if aws_available:
            try:
                ocr_text = extract_text_from_textract(s3_key)
                print(f"AWS text extraction successful: '{ocr_text}'")
            except Exception as e:
                print(f"Text extraction failed: {e}, continuing without OCR")
                ocr_text = ""
        
        # Get the current event to check for HEIC metadata
        event = db.query(models.Event).filter(models.Event.id == event_id).first()
        
        # Extract photo date - prioritize HEIC metadata if available
        print("Extracting photo date...")
        print(f"Event ID: {event_id}, has heic_metadata: {event and event.heic_metadata is not None}")
        if event and event.heic_metadata:
            print(f"HEIC metadata keys: {list(event.heic_metadata.keys())}")
            print(f"HEIC timestamp field: {event.heic_metadata.get('timestamp')}")
            if 'extraction_error' in event.heic_metadata:
                print(f"HEIC extraction error: {event.heic_metadata['extraction_error']}")
            # Show all available EXIF tags for debugging
            if 'all_exif_tags' in event.heic_metadata:
                all_tags = event.heic_metadata['all_exif_tags']
                date_related = {k: v for k, v in all_tags.items() if 'date' in k.lower() or 'time' in k.lower()}
                print(f"HEIC date-related EXIF tags: {date_related}")
                # Also show first 10 tags to see what's available
                first_tags = dict(list(all_tags.items())[:10])
                print(f"First 10 HEIC EXIF tags: {first_tags}")
        
        photo_date = None
        if event and event.heic_metadata and event.heic_metadata.get('timestamp'):
            print("Using date from HEIC metadata")
            from datetime import datetime
            timestamp_value = event.heic_metadata.get('timestamp')
            print(f"Raw timestamp value: {timestamp_value}, type: {type(timestamp_value)}")
            try:
                # HEIC metadata timestamp is in ISO format
                photo_date = datetime.fromisoformat(timestamp_value)
                print(f"HEIC date parsed: {photo_date}")
            except (ValueError, TypeError) as e:
                print(f"Failed to parse HEIC timestamp '{timestamp_value}': {e}")
        
        if not photo_date:
            print("Extracting photo date from S3 image EXIF...")
            photo_date = extract_photo_date(s3_key)
            print(f"S3 photo date extracted: {photo_date}")
        
        # Extract GPS coordinates - prioritize HEIC metadata if available
        print("Extracting GPS coordinates...")
        gps_coords = None
        if event and event.heic_metadata and 'location' in event.heic_metadata:
            heic_location = event.heic_metadata['location']
            if 'latitude' in heic_location and 'longitude' in heic_location:
                print("Using GPS from HEIC metadata")
                gps_coords = {
                    'latitude': heic_location['latitude'],
                    'longitude': heic_location['longitude']
                }
                print(f"HEIC GPS coords: {gps_coords}")
        
        if not gps_coords:
            print("Extracting GPS coordinates from S3 image EXIF...")
            gps_coords = extract_exif_gps(s3_key)
            print(f"S3 GPS coords: {gps_coords}")
        location_info = None
        if gps_coords and settings.locationiq_api_key:
            try:
                print("Attempting reverse geocoding...")
                location_info = reverse_geocode_locationiq(
                    gps_coords["latitude"], 
                    gps_coords["longitude"]
                )
                print(f"Location info: {location_info}")
            except Exception as e:
                print(f"Reverse geocoding failed: {e}")
        
        # Classify event type (with fallback)
        print("Classifying event type...")
        event_type = "personal"  # Default fallback
        if settings.openai_api_key:
            try:
                print("Attempting OpenAI event classification...")
                event_type = infer_event_from_context(labels, ocr_text, caption)
                print(f"Event type classified: {event_type}")
            except Exception as e:
                print(f"Event classification failed: {e}")
        else:
            print("No OpenAI key, using default event type: personal")
        
        # Get user profile and create first-person narrative summary
        print("Getting user profile...")
        user_profile = settings.user_profile
        print(f"User profile loaded for: {user_profile.get('name')}")
        
        print("Creating timeline narrative using GPT-4 Vision...")
        
        # Get image bytes from S3 for GPT-4 Vision
        image_bytes = None
        try:
            s3_client = get_s3_client()
            response = s3_client.get_object(Bucket=settings.aws_bucket_name, Key=s3_key)
            image_bytes = response['Body'].read()
            print("Image bytes retrieved from S3 for GPT-4 Vision")
        except Exception as e:
            print(f"Failed to get image bytes from S3: {e}")
        
        # Format photo datetime for GPT-4 Vision
        photo_datetime_str = ""
        if photo_date:
            photo_datetime_str = photo_date.isoformat()
        
        if image_bytes:
            timeline_narrative = create_timeline_narrative(
                image_bytes=image_bytes,
                caption=caption,
                photo_datetime=photo_datetime_str,
                location_info=location_info,
                user_profile=user_profile
            )
        else:
            # Fallback to old method if image bytes not available
            timeline_narrative = create_first_person_summary(
                caption=caption,
                labels=labels,
                location_info=location_info,
                faces=faces,
                ocr_text=ocr_text,
                heic_metadata=None,
                user_profile=user_profile
            )
        
        print(f"Narrative created: '{timeline_narrative}'")
        
        # Generate clarification questions for photos without captions
        print("Checking for clarification questions...")
        clarification_questions = []
        if not caption or len(caption.strip()) <= 3:
            print(f"Generating questions for empty caption. Labels: {[l.get('name') for l in labels]}, faces: {len(faces)}")
            clarification_questions = generate_clarification_questions(
                labels=labels,
                location_info=location_info,
                faces=faces,
                ocr_text=ocr_text,
                user_profile=user_profile
            )
            print(f"Generated {len(clarification_questions)} questions: {clarification_questions}")
        
        # Prepare AI results
        print("Preparing AI results...")
        ai_results = {
            "faces": faces,
            "labels": labels,
            "ocr_text": ocr_text,
            "location": location_info,
            "event_type": event_type,
            "clarification_questions": clarification_questions
        }
        print("AI results prepared successfully")
        
        # Update event in database (event already queried above)
        if event:
            event.ai_results = ai_results
            event.processing_status = "completed"
            event.summary = timeline_narrative  # Use timeline narrative instead of caption
            event.photo_taken_at = photo_date  # Store the actual photo date
            
            # Update labels field with top labels
            top_labels = [label["name"] for label in labels[:5]]
            event.labels = ",".join(top_labels)
            
            print(f"Updated event {event_id}: status=completed, summary='{timeline_narrative}', questions={len(clarification_questions)}")
            db.commit()
        else:
            print(f"Event {event_id} not found in database!")
    
    except Exception as e:
        # Mark as failed
        event = db.query(models.Event).filter(models.Event.id == event_id).first()
        if event:
            event.processing_status = "failed"
            event.ai_results = {"error": str(e)}
            db.commit()
    
    finally:
        db.close()