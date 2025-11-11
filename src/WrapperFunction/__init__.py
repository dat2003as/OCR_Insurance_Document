"""
Wrapper and helper functions
"""
from typing import Dict, Any
from PIL import Image
import base64
import io


class ImageHelper:
    """Helper functions for image processing"""
    
    @staticmethod
    def image_to_base64(image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    @staticmethod
    def base64_to_image(base64_str: str) -> Image.Image:
        """Convert base64 string to PIL Image"""
        if base64_str.startswith('data:image'):
            base64_str = base64_str.split(',')[1]
        
        img_data = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(img_data))
    
    @staticmethod
    def resize_for_preview(image: Image.Image, max_width: int = 800) -> Image.Image:
        """Resize image for preview while maintaining aspect ratio"""
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            return image.resize((max_width, new_height), Image.LANCZOS)
        return image
    
    @staticmethod
    def compress_image(image: Image.Image, quality: int = 85) -> Image.Image:
        """Compress image to reduce file size"""
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        return Image.open(output)


class FileHelper:
    """Helper functions for file operations"""
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension from filename"""
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    @staticmethod
    def is_valid_pdf(filename: str) -> bool:
        """Check if file is a valid PDF"""
        return FileHelper.get_file_extension(filename) == 'pdf'
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"