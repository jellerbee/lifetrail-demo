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

def process_image_async(event_id: int, s3_key: str, caption: str):
    """Process image asynchronously with AI services"""
    db = SessionLocal()
    
    try:
        # Detect faces
        faces = detect_faces(s3_key)
        
        # Detect labels
        labels = detect_labels(s3_key)
        
        # Extract text
        ocr_text = extract_text_from_textract(s3_key)
        
        # Extract GPS and get location
        gps_coords = extract_exif_gps(s3_key)
        location_info = None
        if gps_coords:
            location_info = reverse_geocode_locationiq(
                gps_coords["latitude"], 
                gps_coords["longitude"]
            )
        
        # Classify event type
        event_type = infer_event_from_context(labels, ocr_text, caption)
        
        # Prepare AI results
        ai_results = {
            "faces": faces,
            "labels": labels,
            "ocr_text": ocr_text,
            "location": location_info,
            "event_type": event_type
        }
        
        # Update event in database
        event = db.query(models.Event).filter(models.Event.id == event_id).first()
        if event:
            event.ai_results = ai_results
            event.processing_status = "completed"
            
            # Update labels field with top labels
            top_labels = [label["name"] for label in labels[:5]]
            event.labels = ",".join(top_labels)
            
            db.commit()
    
    except Exception as e:
        # Mark as failed
        event = db.query(models.Event).filter(models.Event.id == event_id).first()
        if event:
            event.processing_status = "failed"
            event.ai_results = {"error": str(e)}
            db.commit()
    
    finally:
        db.close()