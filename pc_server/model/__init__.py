"""
Plant Disease Detection ML Model Package

This package contains the machine learning components for plant disease detection:
- DiseaseClassifier: Main classification model with multiple backend support
- ImageProcessor: Image preprocessing and augmentation utilities
"""

from .disease_classifier import DiseaseClassifier
from .image_processor import ImageProcessor

__all__ = ['DiseaseClassifier', 'ImageProcessor'] 