from PIL import Image
import numpy as np
from typing import Dict, Any, Tuple
import re


class OCRQualityChecker:
    """Check and assess OCR quality"""
    
    def __init__(self):
        self.min_resolution = (800, 600)
        self.min_confidence = 0.5
    
    def check_image_quality(self, image: Image.Image) -> Dict[str, Any]:
        """
        Check image quality metrics
        
        Returns:
            Dict with quality metrics and scores
        """
        width, height = image.size
        
        # Resolution check
        resolution_score = self._check_resolution(width, height)
        
        # Brightness check
        brightness_score = self._check_brightness(image)
        
        # Contrast check
        contrast_score = self._check_contrast(image)
        
        # Sharpness check
        sharpness_score = self._check_sharpness(image)
        
        # Overall quality
        overall_score = np.mean([
            resolution_score,
            brightness_score,
            contrast_score,
            sharpness_score
        ])
        
        return {
            "resolution_score": resolution_score,
            "brightness_score": brightness_score,
            "contrast_score": contrast_score,
            "sharpness_score": sharpness_score,
            "overall_score": overall_score,
            "quality_level": self._get_quality_level(overall_score),
            "dimensions": {"width": width, "height": height}
        }
    
    def _check_resolution(self, width: int, height: int) -> float:
        """Check if resolution is adequate"""
        min_w, min_h = self.min_resolution
        
        if width >= min_w and height >= min_h:
            return 1.0
        elif width >= min_w * 0.7 and height >= min_h * 0.7:
            return 0.7
        elif width >= min_w * 0.5 and height >= min_h * 0.5:
            return 0.5
        else:
            return 0.3
    
    def _check_brightness(self, image: Image.Image) -> float:
        """Check image brightness"""
        # Convert to grayscale
        gray = np.array(image.convert('L'))
        
        # Calculate mean brightness
        mean_brightness = np.mean(gray) / 255.0
        
        # Ideal brightness is around 0.5-0.7
        if 0.4 <= mean_brightness <= 0.75:
            return 1.0
        elif 0.3 <= mean_brightness <= 0.85:
            return 0.7
        else:
            return 0.4
    
    def _check_contrast(self, image: Image.Image) -> float:
        """Check image contrast"""
        gray = np.array(image.convert('L'))
        
        # Calculate contrast (standard deviation)
        std = np.std(gray)
        
        # Good contrast: std > 50
        if std > 60:
            return 1.0
        elif std > 40:
            return 0.7
        elif std > 20:
            return 0.5
        else:
            return 0.3
    
    def _check_sharpness(self, image: Image.Image) -> float:
        """Check image sharpness using Laplacian variance"""
        import cv2
        
        gray = np.array(image.convert('L'))
        
        # Calculate Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Higher variance = sharper image
        if laplacian_var > 500:
            return 1.0
        elif laplacian_var > 200:
            return 0.7
        elif laplacian_var > 100:
            return 0.5
        else:
            return 0.3
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level from score"""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def check_text_quality(self, text: str) -> Dict[str, Any]:
        """
        Check quality of extracted text
        
        Returns:
            Dict with text quality metrics
        """
        if not text or len(text.strip()) < 10:
            return {
                "confidence": 0.0,
                "quality_level": "poor",
                "issues": ["Text too short or empty"]
            }
        
        issues = []
        
        # Check for minimum length
        word_count = len(text.split())
        if word_count < 5:
            issues.append("Very few words detected")
        
        # Check for special characters ratio
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s]', text)) / len(text)
        if special_char_ratio > 0.3:
            issues.append("High ratio of special characters")
        
        # Check for consecutive spaces
        if '  ' in text:
            issues.append("Multiple consecutive spaces detected")
        
        # Check for gibberish (too many consonants)
        consonant_ratio = len(re.findall(r'[bcdfghjklmnpqrstvwxyz]{4,}', text.lower())) / max(word_count, 1)
        if consonant_ratio > 0.2:
            issues.append("Possible gibberish detected")
        
        # Calculate confidence
        confidence = 1.0
        confidence -= len(issues) * 0.15
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            "confidence": confidence,
            "quality_level": self._get_quality_level(confidence),
            "word_count": word_count,
            "character_count": len(text),
            "issues": issues
        }
    
    def should_preprocess(self, image: Image.Image) -> Tuple[bool, str]:
        """
        Determine if image needs preprocessing
        
        Returns:
            (needs_preprocessing, reason)
        """
        quality = self.check_image_quality(image)
        
        if quality["overall_score"] < 0.6:
            return True, f"Low quality ({quality['quality_level']})"
        
        if quality["brightness_score"] < 0.5:
            return True, "Poor brightness"
        
        if quality["contrast_score"] < 0.5:
            return True, "Poor contrast"
        
        if quality["sharpness_score"] < 0.5:
            return True, "Image not sharp enough"
        
        return False, "Quality acceptable"