import cv2
import numpy as np
from typing import Tuple, Optional
import os

class ImageProcessor:
    """
    Image preprocessing for plant disease detection
    """
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        self.mean = [0.485, 0.456, 0.406]  # ImageNet mean
        self.std = [0.229, 0.224, 0.225]   # ImageNet std
    
    def preprocess(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for ML model input
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image array ready for model input
        """
        # Load image
        image = self._load_image(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Apply preprocessing pipeline
        image = self._resize_image(image)
        image = self._normalize_image(image)
        image = self._ensure_channels(image)
        
        return image
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image from file path"""
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None
        
        try:
            # Load image in BGR format (OpenCV default)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Failed to load image: {image_path}")
                return None
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
            
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """Resize image to target size"""
        # Get current dimensions
        height, width = image.shape[:2]
        
        # Calculate scaling factors
        scale_x = self.target_size[0] / width
        scale_y = self.target_size[1] / height
        
        # Use the smaller scale to maintain aspect ratio
        scale = min(scale_x, scale_y)
        
        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Create canvas with target size
        canvas = np.zeros((self.target_size[1], self.target_size[0], 3), dtype=np.uint8)
        
        # Calculate position to center the image
        x_offset = (self.target_size[0] - new_width) // 2
        y_offset = (self.target_size[1] - new_height) // 2
        
        # Place resized image on canvas
        canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
        
        return canvas
    
    def _normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Normalize image pixel values"""
        # Convert to float32
        image = image.astype(np.float32)
        
        # Normalize to [0, 1]
        image = image / 255.0
        
        # Apply ImageNet normalization
        for i in range(3):
            image[:, :, i] = (image[:, :, i] - self.mean[i]) / self.std[i]
        
        return image
    
    def _ensure_channels(self, image: np.ndarray) -> np.ndarray:
        """Ensure image has correct number of channels"""
        if len(image.shape) == 2:
            # Grayscale image, convert to RGB
            image = np.stack([image] * 3, axis=-1)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            # RGBA image, remove alpha channel
            image = image[:, :, :3]
        elif len(image.shape) == 3 and image.shape[2] != 3:
            # Unexpected number of channels
            raise ValueError(f"Unexpected number of channels: {image.shape[2]}")
        
        return image
    
    def preprocess_for_display(self, image_path: str, max_size: Tuple[int, int] = (800, 600)) -> np.ndarray:
        """
        Preprocess image for display purposes (no normalization)
        
        Args:
            image_path: Path to the image file
            max_size: Maximum dimensions for display
            
        Returns:
            Image array suitable for display
        """
        # Load image
        image = self._load_image(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        # Resize for display (maintain aspect ratio)
        height, width = image.shape[:2]
        scale_x = max_size[0] / width
        scale_y = max_size[1] / height
        scale = min(scale_x, scale_y, 1.0)  # Don't upscale
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return image
    
    def extract_leaf_region(self, image_path: str, x: int, y: int, size: int = 100) -> np.ndarray:
        """
        Extract a region around a point for focused analysis
        
        Args:
            image_path: Path to the image file
            x, y: Center coordinates
            size: Size of the region to extract
            
        Returns:
            Extracted region as numpy array
        """
        # Load image
        image = self._load_image(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        height, width = image.shape[:2]
        
        # Calculate region boundaries
        x1 = max(0, x - size // 2)
        y1 = max(0, y - size // 2)
        x2 = min(width, x + size // 2)
        y2 = min(height, y + size // 2)
        
        # Extract region
        region = image[y1:y2, x1:x2]
        
        # Resize to target size
        region = cv2.resize(region, self.target_size, interpolation=cv2.INTER_AREA)
        
        return region
    
    def apply_augmentation(self, image: np.ndarray) -> np.ndarray:
        """
        Apply data augmentation techniques for training
        
        Args:
            image: Input image array
            
        Returns:
            Augmented image array
        """
        # Random horizontal flip
        if np.random.random() > 0.5:
            image = np.fliplr(image)
        
        # Random rotation (small angles)
        if np.random.random() > 0.5:
            angle = np.random.uniform(-15, 15)
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            image = cv2.warpAffine(image, rotation_matrix, (width, height))
        
        # Random brightness adjustment
        if np.random.random() > 0.5:
            factor = np.random.uniform(0.8, 1.2)
            image = np.clip(image * factor, 0, 255).astype(np.uint8)
        
        return image
    
    def save_preprocessed(self, image: np.ndarray, output_path: str) -> bool:
        """
        Save preprocessed image for debugging
        
        Args:
            image: Preprocessed image array
            output_path: Path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Denormalize if needed
            if image.dtype == np.float32:
                # Reverse ImageNet normalization
                denorm_image = image.copy()
                for i in range(3):
                    denorm_image[:, :, i] = denorm_image[:, :, i] * self.std[i] + self.mean[i]
                
                # Clip to [0, 1] and convert to [0, 255]
                denorm_image = np.clip(denorm_image, 0, 1)
                denorm_image = (denorm_image * 255).astype(np.uint8)
            else:
                denorm_image = image
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert RGB to BGR for OpenCV
            bgr_image = cv2.cvtColor(denorm_image, cv2.COLOR_RGB2BGR)
            
            # Save image
            cv2.imwrite(output_path, bgr_image)
            return True
            
        except Exception as e:
            print(f"Error saving preprocessed image: {e}")
            return False 