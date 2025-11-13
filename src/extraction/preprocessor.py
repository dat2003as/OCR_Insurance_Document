"""
Image Preprocessing for Better OCR Results
"""
from PIL import Image, ImageEnhance
import cv2
import numpy as np

class ImagePreprocessor:
    """Preprocess images to improve OCR accuracy"""
    
    @staticmethod
    def enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """
        Enhance image contrast
        
        Args:
            image: PIL Image
            factor: Contrast factor (1.0 = original, >1.0 = more contrast)
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def enhance_sharpness(image: Image.Image, factor: float = 2.0) -> Image.Image:
        """Enhance image sharpness"""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    @staticmethod
    def denoise(image: Image.Image) -> Image.Image:
        """Remove noise from image"""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Apply denoising
        if len(img_array.shape) == 3:  # Color image
            denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
        else:  # Grayscale
            denoised = cv2.fastNlMeansDenoising(img_array, None, 10, 7, 21)
        
        return Image.fromarray(denoised)
    
    @staticmethod
    def binarize(image: Image.Image, threshold: int = 128) -> Image.Image:
        """
        Convert to binary (black and white)
        
        Args:
            image: PIL Image
            threshold: Threshold value (0-255)
        """
        # Convert to grayscale
        gray = image.convert('L')
        
        # Apply threshold
        binary = gray.point(lambda x: 255 if x > threshold else 0, '1')
        
        return binary.convert('RGB')
    
    @staticmethod
    def adaptive_threshold(image: Image.Image) -> Image.Image:
        """Apply adaptive thresholding"""
        # Convert to numpy
        img_array = np.array(image.convert('L'))
        
        # Apply adaptive threshold
        binary = cv2.adaptiveThreshold(
            img_array, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        return Image.fromarray(binary).convert('RGB')
    
    @staticmethod
    def deskew(image: Image.Image) -> Image.Image:
        """Deskew (straighten) image"""
        # Convert to numpy
        img_array = np.array(image.convert('L'))
        
        # Find coordinates of non-zero pixels
        coords = np.column_stack(np.where(img_array > 0))
        
        # Calculate rotation angle
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Rotate image
        (h, w) = img_array.shape
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            img_array, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return Image.fromarray(rotated).convert('RGB')
    
    @staticmethod
    def remove_borders(image: Image.Image, border_size: int = 10) -> Image.Image:
        """Remove borders from image"""
        width, height = image.size
        return image.crop((
            border_size,
            border_size,
            width - border_size,
            height - border_size
        ))
    
    @staticmethod
    def upscale(image: Image.Image, scale: float = 2.0) -> Image.Image:
        """Upscale image for better OCR"""
        new_size = (int(image.width * scale), int(image.height * scale))
        return image.resize(new_size, Image.LANCZOS)
    
    def preprocess_for_ocr(
        self, 
        image: Image.Image,
        enhance_contrast: bool = True,
        denoise: bool = True,
        deskew: bool = True,
        binarize: bool = False
    ) -> Image.Image:
        """
        Complete preprocessing pipeline for OCR
        
        Args:
            image: Input image
            enhance_contrast: Whether to enhance contrast
            denoise: Whether to remove noise
            deskew: Whether to straighten image
            binarize: Whether to convert to binary
        """
        processed = image.copy()
        
        # Upscale if image is small
        if min(processed.size) < 1000:
            scale = 1000 / min(processed.size)
            processed = self.upscale(processed, scale)
        
        # Remove borders
        processed = self.remove_borders(processed, border_size=5)
        
        # Denoise
        if denoise:
            processed = self.denoise(processed)
        
        # Deskew
        if deskew:
            try:
                processed = self.deskew(processed)
            except:
                pass  # Skip if deskewing fails
        
        # Enhance contrast
        if enhance_contrast:
            processed = self.enhance_contrast(processed, factor=1.5)
            processed = self.enhance_sharpness(processed, factor=2.0)
        
        # Binarize
        if binarize:
            processed = self.adaptive_threshold(processed)
        
        return processed