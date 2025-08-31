"""
Configuration settings for Raspberry Pi Plant Disease Detection System

This combines the Pi-specific settings with your existing working configuration
"""

import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables"""
    load_dotenv()

class Config:
    """
    Configuration class for the plant disease detection system
    """
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # API Configuration
        self.API_BASE_URL = os.getenv('API_BASE_URL', 'http://192.168.1.100:5000')
        self.API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))  # seconds
        
        # Camera Configuration
        self.CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
        self.CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', '1920'))
        self.CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', '1080'))
        self.CAMERA_SOURCE = os.getenv('CAMERA_SOURCE', 'picamera2')  # picamera2|opencv|mock
        
        # Capture Settings
        self.CAPTURE_INTERVAL = int(os.getenv('CAPTURE_INTERVAL', '30'))  # seconds
        self.IMAGE_SAVE_DIR = os.getenv('IMAGE_SAVE_DIR', '/home/pi/plant_images')
        self.IMAGE_RETENTION_HOURS = int(os.getenv('IMAGE_RETENTION_HOURS', '24'))
        
        # GPIO Configuration
        self.GPIO_PIN_SPRINKLER = int(os.getenv('GPIO_PIN_SPRINKLER', '17'))  # BCM pin
        self.SPRAY_DURATION_LOW_MS = int(os.getenv('SPRAY_DURATION_LOW_MS', '2000'))
        self.SPRAY_DURATION_HIGH_MS = int(os.getenv('SPRAY_DURATION_HIGH_MS', '5000'))
        
        # Disease Detection Configuration
        self.DETECTION_BACKEND = os.getenv('DETECTION_BACKEND', 'gemini')  # tflite|plantid|gemini|mock
        self.PLANT_ID_API_KEY = os.getenv('PLANT_ID_API_KEY', '')
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDHW3ArABy2ogwl7twkVXT0oqDR4ykioxw')
        self.GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        self.SEVERITY_LOW_THRESHOLD = float(os.getenv('SEVERITY_LOW_THRESHOLD', '30'))
        self.SEVERITY_HIGH_THRESHOLD = float(os.getenv('SEVERITY_HIGH_THRESHOLD', '70'))
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', '/home/pi/plant_detection.log')
        
        # Network Configuration
        self.NETWORK_RETRY_ATTEMPTS = int(os.getenv('NETWORK_RETRY_ATTEMPTS', '3'))
        self.NETWORK_RETRY_DELAY = int(os.getenv('NETWORK_RETRY_DELAY', '5'))  # seconds
        
        # Health Check Configuration
        self.HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '300'))  # 5 minutes
        self.ENABLE_HEALTH_CHECKS = os.getenv('ENABLE_HEALTH_CHECKS', 'true').lower() == 'true'
    
    def validate(self) -> bool:
        """
        Validate configuration settings
        
        Returns:
            True if configuration is valid, False otherwise
        """
        errors = []
        
        # Check API URL format
        if not self.API_BASE_URL.startswith(('http://', 'https://')):
            errors.append("API_BASE_URL must start with http:// or https://")
        
        # Check camera settings
        if self.CAMERA_WIDTH <= 0 or self.CAMERA_HEIGHT <= 0:
            errors.append("Camera dimensions must be positive")
        
        # Check capture interval
        if self.CAPTURE_INTERVAL < 5:
            errors.append("CAPTURE_INTERVAL must be at least 5 seconds")
        
        # Check GPIO pin
        if not (1 <= self.GPIO_PIN_SPRINKLER <= 40):
            errors.append("GPIO_PIN_SPRINKLER must be between 1 and 40")
        
        # Check spray durations
        if self.SPRAY_DURATION_LOW_MS <= 0 or self.SPRAY_DURATION_HIGH_MS <= 0:
            errors.append("Spray durations must be positive")
        
        # Check severity thresholds
        if self.SEVERITY_LOW_THRESHOLD >= self.SEVERITY_HIGH_THRESHOLD:
            errors.append("SEVERITY_LOW_THRESHOLD must be less than SEVERITY_HIGH_THRESHOLD")
        
        # Check image retention
        if self.IMAGE_RETENTION_HOURS <= 0:
            errors.append("IMAGE_RETENTION_HOURS must be positive")
        
        # Check network settings
        if self.NETWORK_RETRY_ATTEMPTS <= 0:
            errors.append("NETWORK_RETRY_ATTEMPTS must be positive")
        
        if self.NETWORK_RETRY_DELAY <= 0:
            errors.append("NETWORK_RETRY_DELAY must be positive")
        
        # Report errors
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'API_BASE_URL': self.API_BASE_URL,
            'API_TIMEOUT': self.API_TIMEOUT,
            'CAMERA_INDEX': self.CAMERA_INDEX,
            'CAMERA_WIDTH': self.CAMERA_WIDTH,
            'CAMERA_HEIGHT': self.CAMERA_HEIGHT,
            'CAMERA_SOURCE': self.CAMERA_SOURCE,
            'CAPTURE_INTERVAL': self.CAPTURE_INTERVAL,
            'IMAGE_SAVE_DIR': self.IMAGE_SAVE_DIR,
            'IMAGE_RETENTION_HOURS': self.IMAGE_RETENTION_HOURS,
            'GPIO_PIN_SPRINKLER': self.GPIO_PIN_SPRINKLER,
            'SPRAY_DURATION_LOW_MS': self.SPRAY_DURATION_LOW_MS,
            'SPRAY_DURATION_HIGH_MS': self.SPRAY_DURATION_HIGH_MS,
            'DETECTION_BACKEND': self.DETECTION_BACKEND,
            'SEVERITY_LOW_THRESHOLD': self.SEVERITY_LOW_THRESHOLD,
            'SEVERITY_HIGH_THRESHOLD': self.SEVERITY_HIGH_THRESHOLD,
            'LOG_LEVEL': self.LOG_LEVEL,
            'LOG_FILE': self.LOG_FILE,
            'NETWORK_RETRY_ATTEMPTS': self.NETWORK_RETRY_ATTEMPTS,
            'NETWORK_RETRY_DELAY': self.NETWORK_RETRY_DELAY,
            'HEALTH_CHECK_INTERVAL': self.HEALTH_CHECK_INTERVAL,
            'ENABLE_HEALTH_CHECKS': self.ENABLE_HEALTH_CHECKS
        }
    
    def print_config(self):
        """Print current configuration"""
        print("🌱 Pi Plant Disease Detection Configuration:")
        print("=" * 50)
        
        config_dict = self.to_dict()
        for key, value in config_dict.items():
            print(f"{key:25}: {value}")
        
        print("=" * 50)
    
    @classmethod
    def from_env_file(cls, env_file_path: str = '.env'):
        """
        Create configuration from environment file
        
        Args:
            env_file_path: Path to .env file
            
        Returns:
            Config instance
        """
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        
        return cls()

# Default configuration instance
config = Config()

# Example .env file content for Pi:
"""
# API Configuration
API_BASE_URL=http://192.168.1.100:5000
API_TIMEOUT=30

# Camera Configuration
CAMERA_INDEX=0
CAMERA_WIDTH=1920
CAMERA_HEIGHT=1080
CAMERA_SOURCE=picamera2

# Capture Settings
CAPTURE_INTERVAL=30
IMAGE_SAVE_DIR=/home/pi/plant_images
IMAGE_RETENTION_HOURS=24

# GPIO Configuration
GPIO_PIN_SPRINKLER=17
SPRAY_DURATION_LOW_MS=2000
SPRAY_DURATION_HIGH_MS=5000

# Disease Detection Configuration
DETECTION_BACKEND=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
SEVERITY_LOW_THRESHOLD=30
SEVERITY_HIGH_THRESHOLD=70

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/home/pi/plant_detection.log

# Network Configuration
NETWORK_RETRY_ATTEMPTS=3
NETWORK_RETRY_DELAY=5

# Health Check Configuration
HEALTH_CHECK_INTERVAL=300
ENABLE_HEALTH_CHECKS=true
""" 