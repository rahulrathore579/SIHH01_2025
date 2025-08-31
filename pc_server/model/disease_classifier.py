import os
import numpy as np
from typing import Dict, Any, Optional
import json
import time

class DiseaseClassifier:
    """
    Plant disease classification using various ML backends
    """
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.model_info = {}
        self.backend = "mock"  # Default to mock for testing
        
        # Try to load different model types
        self._load_model()
    
    def _load_model(self):
        """Attempt to load the ML model from various backends"""
        try:
            # Try TensorFlow/Keras first
            if self._load_tensorflow_model():
                self.backend = "tensorflow"
                return
            
            # Try ONNX
            if self._load_onnx_model():
                self.backend = "onnx"
                return
            
            # Try TFLite
            if self._load_tflite_model():
                self.backend = "tflite"
                return
            
            # Fallback to mock model
            self._load_mock_model()
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self._load_mock_model()
    
    def _load_tensorflow_model(self) -> bool:
        """Load TensorFlow/Keras model"""
        try:
            import tensorflow as tf
            if os.path.exists(self.model_path) and self.model_path.endswith('.h5'):
                self.model = tf.keras.models.load_model(self.model_path)
                self.model_info = {
                    "backend": "tensorflow",
                    "model_type": "keras",
                    "input_shape": self.model.input_shape,
                    "output_shape": self.model.output_shape,
                    "layers": len(self.model.layers)
                }
                print("✅ TensorFlow model loaded successfully")
                return True
        except ImportError:
            print("TensorFlow not available")
        except Exception as e:
            print(f"Error loading TensorFlow model: {e}")
        return False
    
    def _load_onnx_model(self) -> bool:
        """Load ONNX model"""
        try:
            import onnxruntime as ort
            if os.path.exists(self.model_path) and self.model_path.endswith('.onnx'):
                self.model = ort.InferenceSession(self.model_path)
                self.model_info = {
                    "backend": "onnx",
                    "model_type": "onnx",
                    "providers": self.model.get_providers()
                }
                print("✅ ONNX model loaded successfully")
                return True
        except ImportError:
            print("ONNX Runtime not available")
        except Exception as e:
            print(f"Error loading ONNX model: {e}")
        return False
    
    def _load_tflite_model(self) -> bool:
        """Load TFLite model"""
        try:
            import tensorflow as tf
            if os.path.exists(self.model_path) and self.model_path.endswith('.tflite'):
                interpreter = tf.lite.Interpreter(model_path=self.model_path)
                interpreter.allocate_tensors()
                self.model = interpreter
                self.model_info = {
                    "backend": "tflite",
                    "model_type": "tflite",
                    "input_details": interpreter.get_input_details(),
                    "output_details": interpreter.get_output_details()
                }
                print("✅ TFLite model loaded successfully")
                return True
        except ImportError:
            print("TensorFlow Lite not available")
        except Exception as e:
            print(f"Error loading TFLite model: {e}")
        return False
    
    def _load_mock_model(self):
        """Load mock model for testing when no real model is available"""
        self.model = "mock"
        self.model_info = {
            "backend": "mock",
            "model_type": "mock",
            "description": "Mock model for testing - returns random predictions"
        }
        print("⚠️  Using mock model - no real ML model loaded")
    
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Predict disease from preprocessed image
        
        Args:
            image: Preprocessed image array (should match model input shape)
            
        Returns:
            Dictionary with prediction results
        """
        if self.backend == "mock":
            return self._mock_predict()
        
        try:
            if self.backend == "tensorflow":
                return self._tensorflow_predict(image)
            elif self.backend == "onnx":
                return self._onnx_predict(image)
            elif self.backend == "tflite":
                return self._tflite_predict(image)
            else:
                return self._mock_predict()
                
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._mock_predict()
    
    def _tensorflow_predict(self, image: np.ndarray) -> Dict[str, Any]:
        """TensorFlow/Keras prediction"""
        # Ensure image has correct shape and batch dimension
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        # Run prediction
        predictions = self.model.predict(image, verbose=0)
        
        # Get class with highest probability
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        
        # Map class index to disease names (customize based on your model)
        disease_classes = ["healthy", "blight", "rust", "mildew", "leaf_spot"]
        disease_class = disease_classes[class_idx] if class_idx < len(disease_classes) else f"class_{class_idx}"
        
        return {
            "class": disease_class,
            "confidence": confidence,
            "all_probabilities": predictions[0].tolist(),
            "backend": "tensorflow"
        }
    
    def _onnx_predict(self, image: np.ndarray) -> Dict[str, Any]:
        """ONNX prediction"""
        # Get input name
        input_name = self.model.get_inputs()[0].name
        
        # Ensure image has correct shape
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        # Run prediction
        predictions = self.model.run(None, {input_name: image.astype(np.float32)})[0]
        
        # Get class with highest probability
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        
        # Map class index to disease names
        disease_classes = ["healthy", "blight", "rust", "mildew", "leaf_spot"]
        disease_class = disease_classes[class_idx] if class_idx < len(disease_classes) else f"class_{class_idx}"
        
        return {
            "class": disease_class,
            "confidence": confidence,
            "all_probabilities": predictions[0].tolist(),
            "backend": "onnx"
        }
    
    def _tflite_predict(self, image: np.ndarray) -> Dict[str, Any]:
        """TFLite prediction"""
        interpreter = self.model
        
        # Get input and output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        # Ensure image has correct shape and type
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], image.astype(np.float32))
        
        # Run inference
        interpreter.invoke()
        
        # Get output
        predictions = interpreter.get_tensor(output_details[0]['index'])
        
        # Get class with highest probability
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        
        # Map class index to disease names
        disease_classes = ["healthy", "blight", "rust", "mildew", "leaf_spot"]
        disease_class = disease_classes[class_idx] if class_idx < len(disease_classes) else f"class_{class_idx}"
        
        return {
            "class": disease_class,
            "confidence": confidence,
            "all_probabilities": predictions[0].tolist(),
            "backend": "tflite"
        }
    
    def _mock_predict(self) -> Dict[str, Any]:
        """Mock prediction for testing"""
        import random
        
        # Simulate some delay
        time.sleep(0.1)
        
        # Random disease classes
        diseases = ["healthy", "blight", "rust", "mildew", "leaf_spot"]
        disease = random.choice(diseases)
        
        # Generate realistic confidence
        if disease == "healthy":
            confidence = random.uniform(0.7, 0.95)
        else:
            confidence = random.uniform(0.6, 0.9)
        
        return {
            "class": disease,
            "confidence": confidence,
            "all_probabilities": [0.1] * len(diseases),  # Placeholder
            "backend": "mock"
        }
    
    def is_model_loaded(self) -> bool:
        """Check if a real model is loaded"""
        return self.backend != "mock"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "backend": self.backend,
            "model_path": self.model_path,
            "model_loaded": self.is_model_loaded(),
            "info": self.model_info
        }
    
    def get_supported_formats(self) -> list:
        """Get list of supported model formats"""
        formats = []
        try:
            import tensorflow as tf
            formats.append("h5 (TensorFlow/Keras)")
        except ImportError:
            pass
        
        try:
            import onnxruntime as ort
            formats.append("onnx")
        except ImportError:
            pass
        
        try:
            import tensorflow as tf
            formats.append("tflite")
        except ImportError:
            pass
        
        return formats 