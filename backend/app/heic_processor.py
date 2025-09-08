"""
HEIC image processing module
Handles HEIC/HEIF image conversion and rich metadata extraction
"""
import io
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from PIL import Image, ExifTags
import pillow_heif
import exifread

class MockExifTag:
    """Mock exifread tag for Pillow EXIF data compatibility"""
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

def extract_heic_metadata(image_bytes: bytes) -> Dict:
    """Extract comprehensive metadata from HEIC image bytes"""
    metadata = {
        'device_info': {},
        'camera_settings': {},
        'location': {},
        'timestamp': None,
        'image_properties': {},
        'raw_exif': {}
    }
    
    try:
        print("Starting HEIC metadata extraction...")
        
        # First try using Pillow with pillow-heif for EXIF data
        image_file = io.BytesIO(image_bytes)
        tags = {}
        exif_data = None
        
        try:
            with Image.open(image_file) as img:
                print(f"HEIC image opened successfully: {img.format} {img.size}")
                exif_data = img.getexif()
                if exif_data:
                    print(f"Found {len(exif_data)} EXIF entries via Pillow")
                    # Convert to exifread-style format
                    for tag_id, value in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag_id, f"Tag_{tag_id}")
                        if tag_name == "DateTime":
                            tags["Image DateTime"] = MockExifTag(value)
                        elif tag_name == "DateTimeOriginal":
                            tags["EXIF DateTimeOriginal"] = MockExifTag(value)
                        elif tag_name == "GPSInfo" and isinstance(value, dict):
                            # Handle GPS data
                            for gps_tag_id, gps_value in value.items():
                                gps_tag_name = ExifTags.GPSTAGS.get(gps_tag_id, f"GPS_{gps_tag_id}")
                                if gps_tag_name in ["GPSLatitude", "GPSLongitude", "GPSLatitudeRef", "GPSLongitudeRef"]:
                                    tags[f"GPS {gps_tag_name}"] = MockExifTag(gps_value)
                else:
                    print("No EXIF data found via Pillow")
        except Exception as pillow_error:
            print(f"Pillow EXIF extraction failed: {pillow_error}")
        
        # Fallback to exifread if we didn't get what we need
        if not tags:
            try:
                image_file.seek(0)
                tags = exifread.process_file(image_file, details=True)
                print(f"HEIC EXIF extraction via exifread found {len(tags)} tags")
            except Exception as exifread_error:
                print(f"exifread extraction failed: {exifread_error}")
        
        # Show debug info about found tags
        if tags:
            key_tags = ['EXIF DateTimeOriginal', 'Image DateTime', 'EXIF DateTime', 'GPS GPSLatitude', 'GPS GPSLongitude']
            for tag_name in key_tags:
                if tag_name in tags:
                    print(f"Found HEIC tag {tag_name}: {tags[tag_name]}")
            
            date_time_tags = {k: str(v) for k, v in tags.items() if 'date' in k.lower() or 'time' in k.lower()}
            if date_time_tags:
                print(f"All HEIC date/time tags: {date_time_tags}")
        else:
            print("No EXIF tags extracted from HEIC file")
        
        # Extract device information
        if 'Image Make' in tags:
            metadata['device_info']['make'] = str(tags['Image Make'])
        if 'Image Model' in tags:
            metadata['device_info']['model'] = str(tags['Image Model'])
        if 'Image Software' in tags:
            metadata['device_info']['software'] = str(tags['Image Software'])
        
        # Extract camera settings
        if 'EXIF FNumber' in tags:
            metadata['camera_settings']['f_number'] = str(tags['EXIF FNumber'])
        if 'EXIF ExposureTime' in tags:
            metadata['camera_settings']['exposure_time'] = str(tags['EXIF ExposureTime'])
        if 'EXIF ISOSpeedRatings' in tags:
            metadata['camera_settings']['iso'] = str(tags['EXIF ISOSpeedRatings'])
        if 'EXIF FocalLength' in tags:
            metadata['camera_settings']['focal_length'] = str(tags['EXIF FocalLength'])
        if 'EXIF WhiteBalance' in tags:
            metadata['camera_settings']['white_balance'] = str(tags['EXIF WhiteBalance'])
        if 'EXIF Flash' in tags:
            metadata['camera_settings']['flash'] = str(tags['EXIF Flash'])
        
        # Extract GPS information
        gps_data = {}
        for tag_key in tags.keys():
            if tag_key.startswith('GPS'):
                gps_data[tag_key] = str(tags[tag_key])
        
        if gps_data:
            metadata['location']['raw_gps'] = gps_data
            # Convert GPS coordinates if available
            lat, lon = convert_gps_coordinates(tags)
            if lat is not None and lon is not None:
                metadata['location']['latitude'] = lat
                metadata['location']['longitude'] = lon
        
        # Extract timestamp
        timestamp_found = False
        if 'EXIF DateTimeOriginal' in tags:
            try:
                dt_str = str(tags['EXIF DateTimeOriginal'])
                print(f"HEIC DateTimeOriginal found: '{dt_str}'")
                metadata['timestamp'] = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S').isoformat()
                print(f"HEIC timestamp parsed to ISO: {metadata['timestamp']}")
                timestamp_found = True
            except ValueError as e:
                print(f"Failed to parse HEIC DateTimeOriginal '{dt_str}': {e}")
        
        if not timestamp_found and 'Image DateTime' in tags:
            try:
                dt_str = str(tags['Image DateTime'])
                print(f"HEIC DateTime found: '{dt_str}'")
                metadata['timestamp'] = datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S').isoformat()
                print(f"HEIC timestamp parsed to ISO: {metadata['timestamp']}")
                timestamp_found = True
            except ValueError as e:
                print(f"Failed to parse HEIC DateTime '{dt_str}': {e}")
        
        if not timestamp_found:
            print("No HEIC timestamp found in EXIF data")
            # List all date-related tags for debugging
            date_tags = {k: str(v) for k, v in tags.items() if 'date' in k.lower() or 'time' in k.lower()}
            if date_tags:
                print(f"Available date/time tags: {date_tags}")
        
        # Extract image properties using Pillow
        image_file.seek(0)
        with Image.open(image_file) as img:
            metadata['image_properties'] = {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode
            }
            
            # Extract additional EXIF data using Pillow
            if hasattr(img, '_getexif') and img._getexif():
                exif_dict = img._getexif()
                for tag_id, value in exif_dict.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    # Convert complex values to strings
                    if isinstance(value, (bytes, tuple)):
                        value = str(value)
                    metadata['raw_exif'][tag] = value
        
        # Store all EXIF tags for completeness
        metadata['all_exif_tags'] = {str(k): str(v) for k, v in tags.items()}
        
    except Exception as e:
        metadata['extraction_error'] = str(e)
    
    return metadata

def convert_gps_coordinates(tags: dict) -> Tuple[Optional[float], Optional[float]]:
    """Convert GPS EXIF tags to decimal coordinates"""
    try:
        if 'GPS GPSLatitude' not in tags or 'GPS GPSLongitude' not in tags:
            return None, None
        
        lat = convert_dms_to_decimal(tags['GPS GPSLatitude'])
        lon = convert_dms_to_decimal(tags['GPS GPSLongitude'])
        
        # Apply hemisphere corrections
        if 'GPS GPSLatitudeRef' in tags and str(tags['GPS GPSLatitudeRef']).upper() == 'S':
            lat = -lat
        if 'GPS GPSLongitudeRef' in tags and str(tags['GPS GPSLongitudeRef']).upper() == 'W':
            lon = -lon
            
        return lat, lon
    except Exception:
        return None, None

def convert_dms_to_decimal(dms_tag) -> float:
    """Convert degrees, minutes, seconds to decimal degrees"""
    # Handle different formats of DMS data
    dms_str = str(dms_tag).strip('[]')
    parts = dms_str.split(', ')
    
    if len(parts) >= 3:
        # Parse each part as a fraction
        degrees = parse_fraction(parts[0])
        minutes = parse_fraction(parts[1])
        seconds = parse_fraction(parts[2])
        
        return degrees + minutes/60 + seconds/3600
    return 0.0

def parse_fraction(fraction_str: str) -> float:
    """Parse fraction string like '37' or '37/1' to float"""
    fraction_str = fraction_str.strip()
    if '/' in fraction_str:
        num, denom = fraction_str.split('/')
        return float(num) / float(denom)
    else:
        return float(fraction_str)

def convert_heic_to_jpeg(image_bytes: bytes, quality: int = 95) -> bytes:
    """Convert HEIC image bytes to JPEG bytes"""
    try:
        # Open HEIC image using pillow-heif
        image_file = io.BytesIO(image_bytes)
        with Image.open(image_file) as img:
            # Convert to RGB if necessary (HEIC can have different color modes)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)
            return output.getvalue()
    
    except Exception as e:
        raise ValueError(f"Failed to convert HEIC to JPEG: {str(e)}")

def is_heic_file(filename: str) -> bool:
    """Check if filename has HEIC/HEIF extension"""
    if not filename:
        return False
    
    heic_extensions = {'.heic', '.heif', '.hif'}
    return any(filename.lower().endswith(ext) for ext in heic_extensions)

def process_heic_upload(image_bytes: bytes, filename: str) -> Tuple[bytes, Dict]:
    """
    Process HEIC upload: extract metadata and convert to JPEG
    Returns: (jpeg_bytes, metadata_dict)
    """
    # Extract comprehensive metadata from original HEIC
    metadata = extract_heic_metadata(image_bytes)
    
    # Convert to JPEG for storage
    jpeg_bytes = convert_heic_to_jpeg(image_bytes)
    
    # Add processing info to metadata
    metadata['processing_info'] = {
        'original_format': 'HEIC',
        'converted_to': 'JPEG',
        'original_filename': filename,
        'processed_at': datetime.utcnow().isoformat()
    }
    
    return jpeg_bytes, metadata