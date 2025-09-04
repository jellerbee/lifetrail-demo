import boto3
import uuid
from io import BytesIO
from PIL import Image
from .settings import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)

def convert_to_jpeg(image_bytes: bytes) -> bytes:
    """Convert image to JPEG format"""
    image = Image.open(BytesIO(image_bytes))
    if image.format == 'JPEG':
        return image_bytes
    
    # Convert to RGB if needed (for PNG with transparency, etc.)
    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')
    
    output = BytesIO()
    image.save(output, format='JPEG', quality=90)
    return output.getvalue()

def upload_image_to_s3(image_bytes: bytes, filename: str) -> str:
    """Upload image to S3 and return the S3 key"""
    # Convert to JPEG
    jpeg_bytes = convert_to_jpeg(image_bytes)
    
    # Generate unique S3 key
    unique_id = str(uuid.uuid4())
    s3_key = f"images/{unique_id}.jpg"
    
    # Upload to S3
    s3_client.put_object(
        Bucket=settings.aws_bucket_name,
        Key=s3_key,
        Body=jpeg_bytes,
        ContentType='image/jpeg'
    )
    
    return s3_key

def get_s3_url(s3_key: str) -> str:
    """Generate S3 URL for displaying image"""
    return f"https://{settings.aws_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"