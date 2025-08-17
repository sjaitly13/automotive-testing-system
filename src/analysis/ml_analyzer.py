"""
Machine learning analyzer for infotainment performance prediction.
Uses historical data to predict bottlenecks and provide optimization recommendations.
"""

import sys
import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pickle

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.config_loader import get_config
from monitoring.performance_monitor import get_performance_monitor

try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
    from sklearn.neural_network import MLPRegressor
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

@dataclass
class PerformancePrediction:
    """Represents a performance prediction result."""
    timestamp: float
    prediction_horizon_minutes: int
    predicted_cpu_usage: float
    predicted_memory_usage: float
    predicted_response_time: float
    confidence_score: float
    bottleneck_risk: str  # low, medium, high
    recommendations: List[str]

@dataclass
class BottleneckAnalysis:
    """Represents a bottleneck analysis result."""
    component: str
    risk_level: str
    current_metrics: Dict[str, float]
    predicted_metrics: Dict[str, float]
    contributing_factors: List[str]
    optimization_suggestions: List[str]

class MLPerformanceAnalyzer:
    """Machine learning-based performance analyzer for infotainment systems."""
    
    def __init__(self):
        self.logger = get_logger("ml_analyzer")
        self.config = get_config()
        self.performance_monitor = get_performance_monitor()
        
        if not SKLEARN_AVAILABLE:
            self.logger.warning("scikit-learn not available. ML features will be disabled.")
            self.ml_enabled = False
        else:
            self.ml_enabled = self.config.get('machine_learning.enabled', True)
        
        # ML model configuration
        self.model_type = self.config.get('machine_learning.model_type', 'random_forest')
        self.training_data_size = self.config.get('machine_learning.training_data_size', 1000)
        self.prediction_horizon = self.config.get('machine_learning.prediction_horizon_minutes', 30)
        
        # ML models
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        
        # Training data
        self.training_data = []
        self.model_trained = False
        
        # Initialize models
        self._initialize_models()
        
        self.logger.info("ML Performance Analyzer initialized")
    
    def _initialize_models(self):
        """Initialize machine learning models."""
        if not self.ml_enabled:
            return
        
        try:
            # Define feature columns
            self.feature_columns = [
                'cpu_usage', 'memory_usage', 'response_time_ms', 
                'frame_rate', 'error_count', 'operation_count',
                'time_of_day', 'day_of_week', 'system_uptime'
            ]
            
            # Initialize models for different prediction tasks
            if self.model_type == 'random_forest':
                self.models['cpu_prediction'] = RandomForestRegressor(
                    n_estimators=100, random_state=42
                )
                self.models['memory_prediction'] = RandomForestRegressor(
                    n_estimators=100, random_state=42
                )
                self.models['response_time_prediction'] = RandomForestRegressor(
                    n_estimators=100, random_state=42
                )
                self.models['bottleneck_classification'] = RandomForestClassifier(
                    n_estimators=100, random_state=42
                )
            
            elif self.model_type == 'linear_regression':
                self.models['cpu_prediction'] = LinearRegression()
                self.models['memory_prediction'] = LinearRegression()
                self.models['response_time_prediction'] = LinearRegression()
                self.models['bottleneck_classification'] = RandomForestClassifier(
                    n_estimators=50, random_state=42
                )
            
            elif self.model_type == 'neural_network':
                self.models['cpu_prediction'] = MLPRegressor(
                    hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
                )
                self.models['memory_prediction'] = MLPRegressor(
                    hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
                )
                self.models['response_time_prediction'] = MLPRegressor(
                    hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
                )
                self.models['bottleneck_classification'] = RandomForestClassifier(
                    n_estimators=100, random_state=42
                )
            
            # Initialize scalers
            for model_name in self.models.keys():
                if 'prediction' in model_name:
                    self.scalers[model_name] = StandardScaler()
            
            self.logger.info(f"ML models initialized with {self.model_type} architecture")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
            self.ml_enabled = False
    
    def collect_training_data(self, data_source: str = "performance_monitor") -> bool:
        """Collect training data from various sources."""
        if not self.ml_enabled:
            return False
        
        try:
            self.logger.info("Collecting training data...")
            
            if data_source == "performance_monitor":
                # Collect from performance monitor
                self._collect_from_performance_monitor()
            elif data_source == "file":
                # Load from saved data files
                self._load_training_data_from_files()
            else:
                self.logger.error(f"Unknown data source: {data_source}")
                return False
            
            self.logger.info(f"Training data collected: {len(self.training_data)} samples")
            return True
            
        except Exception as e:
            self.logger.error(f"Error collecting training data: {e}")
            return False
    
    def _collect_from_performance_monitor(self):
        """Collect training data from the performance monitor."""
        try:
            # Get current metrics
            current_metrics = self.performance_monitor.get_current_metrics()
            
            if not current_metrics:
                return
            
            # Get historical metrics for the last hour
            end_time = time.time()
            start_time = end_time - 3600  # Last hour
            
            # Collect metrics for different components
            for metric_name in ['cpu_usage', 'memory_usage', 'response_time']:
                metrics = self.performance_monitor.get_metrics_history(
                    metric_name, start_time, end_time
                )
                
                for metric in metrics:
                    # Create training sample
                    sample = self._create_training_sample(metric, current_metrics)
                    if sample:
                        self.training_data.append(sample)
            
            # Limit training data size
            if len(self.training_data) > self.training_data_size:
                self.training_data = self.training_data[-self.training_data_size:]
            
        except Exception as e:
            self.logger.error(f"Error collecting from performance monitor: {e}")
    
    def _create_training_sample(self, metric, current_metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a training sample from metric data."""
        try:
            # Extract features
            features = {
                'cpu_usage': current_metrics.get('cpu_percent', 0.0),
                'memory_usage': current_metrics.get('memory_percent', 0.0),
                'response_time_ms': current_metrics.get('response_time_ms', 0.0),
                'frame_rate': current_metrics.get('frame_rate', 0.0),
                'error_count': current_metrics.get('error_count', 0),
                'operation_count': len(self.training_data),  # Simple operation count
                'time_of_day': time.localtime().tm_hour,
                'day_of_week': time.localtime().tm_wday,
                'system_uptime': time.time() - self.performance_monitor.start_time if hasattr(self.performance_monitor, 'start_time') else 0
            }
            
            # Add target values
            targets = {
                'cpu_usage_target': metric.value if metric.metric_name == 'cpu_usage' else features['cpu_usage'],
                'memory_usage_target': metric.value if metric.metric_name == 'memory_usage' else features['memory_usage'],
                'response_time_target': metric.value if metric.metric_name == 'response_time' else features['response_time_ms'],
                'bottleneck_risk': self._classify_bottleneck_risk(features)
            }
            
            # Combine features and targets
            sample = {**features, **targets}
            return sample
            
        except Exception as e:
            self.logger.error(f"Error creating training sample: {e}")
            return None
    
    def _classify_bottleneck_risk(self, features: Dict[str, Any]) -> str:
        """Classify bottleneck risk based on current features."""
        try:
            risk_score = 0
            
            # CPU usage risk
            if features['cpu_usage'] > 80:
                risk_score += 3
            elif features['cpu_usage'] > 60:
                risk_score += 2
            elif features['cpu_usage'] > 40:
                risk_score += 1
            
            # Memory usage risk
            if features['memory_usage'] > 85:
                risk_score += 3
            elif features['memory_usage'] > 70:
                risk_score += 2
            elif features['memory_usage'] > 50:
                risk_score += 1
            
            # Response time risk
            if features['response_time_ms'] > 200:
                risk_score += 3
            elif features['response_time_ms'] > 100:
                risk_score += 2
            elif features['response_time_ms'] > 50:
                risk_score += 1
            
            # Frame rate risk
            if features['frame_rate'] < 30:
                risk_score += 3
            elif features['frame_rate'] < 50:
                risk_score += 2
            elif features['frame_rate'] < 60:
                risk_score += 1
            
            # Error count risk
            if features['error_count'] > 10:
                risk_score += 3
            elif features['error_count'] > 5:
                risk_score += 2
            elif features['error_count'] > 0:
                risk_score += 1
            
            # Classify risk level
            if risk_score >= 8:
                return 'high'
            elif risk_score >= 4:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            self.logger.error(f"Error classifying bottleneck risk: {e}")
            return 'low'
    
    def _load_training_data_from_files(self):
        """Load training data from saved data files."""
        try:
            data_dir = Path("data")
            if not data_dir.exists():
                return
            
            # Look for performance data files
            for data_file in data_dir.glob("*.json"):
                try:
                    with open(data_file, 'r') as f:
                        data = json.load(f)
                    
                    # Process the data and add to training set
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                sample = self._process_file_data(item)
                                if sample:
                                    self.training_data.append(sample)
                    
                except Exception as e:
                    self.logger.warning(f"Error loading data file {data_file}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error loading training data from files: {e}")
    
    def _process_file_data(self, data_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process data from file and convert to training sample format."""
        try:
            # Extract relevant fields and create training sample
            # This is a simplified version - you might need to adapt based on your data format
            sample = {
                'cpu_usage': data_item.get('cpu_percent', 0.0),
                'memory_usage': data_item.get('memory_percent', 0.0),
                'response_time_ms': data_item.get('response_time_ms', 0.0),
                'frame_rate': data_item.get('frame_rate', 0.0),
                'error_count': data_item.get('error_count', 0),
                'operation_count': data_item.get('operation_count', 0),
                'time_of_day': time.localtime().tm_hour,
                'day_of_week': time.localtime().tm_wday,
                'system_uptime': 0,
                'cpu_usage_target': data_item.get('cpu_percent', 0.0),
                'memory_usage_target': data_item.get('memory_percent', 0.0),
                'response_time_target': data_item.get('response_time_ms', 0.0),
                'bottleneck_risk': self._classify_bottleneck_risk({
                    'cpu_usage': data_item.get('cpu_percent', 0.0),
                    'memory_usage': data_item.get('memory_percent', 0.0),
                    'response_time_ms': data_item.get('response_time_ms', 0.0),
                    'frame_rate': data_item.get('frame_rate', 0.0),
                    'error_count': data_item.get('error_count', 0)
                })
            }
            
            return sample
            
        except Exception as e:
            self.logger.error(f"Error processing file data: {e}")
            return None
    
    def train_models(self) -> bool:
        """Train the machine learning models."""
        if not self.ml_enabled:
            return False
        
        if len(self.training_data) < 100:
            self.logger.warning("Insufficient training data. Need at least 100 samples.")
            return False
        
        try:
            self.logger.info("Training ML models...")
            
            # Convert training data to DataFrame
            df = pd.DataFrame(self.training_data)
            
            # Prepare features and targets
            X = df[self.feature_columns].values
            y_cpu = df['cpu_usage_target'].values
            y_memory = df['memory_usage_target'].values
            y_response = df['response_time_target'].values
            y_bottleneck = df['bottleneck_risk'].values
            
            # Split data for training and validation
            X_train, X_test, y_cpu_train, y_cpu_test = train_test_split(
                X, y_cpu, test_size=0.2, random_state=42
            )
            
            # Train CPU prediction model
            if 'cpu_prediction' in self.models:
                self.scalers['cpu_prediction'].fit(X_train)
                X_train_scaled = self.scalers['cpu_prediction'].transform(X_train)
                X_test_scaled = self.scalers['cpu_prediction'].transform(X_test)
                
                self.models['cpu_prediction'].fit(X_train_scaled, y_cpu_train)
                y_pred = self.models['cpu_prediction'].predict(X_test_scaled)
                mse = mean_squared_error(y_cpu_test, y_pred)
                self.logger.info(f"CPU prediction model trained. MSE: {mse:.4f}")
            
            # Train memory prediction model
            if 'memory_prediction' in self.models:
                self.scalers['memory_prediction'].fit(X_train)
                X_train_scaled = self.scalers['memory_prediction'].transform(X_train)
                X_test_scaled = self.scalers['memory_prediction'].transform(X_test)
                
                self.models['memory_prediction'].fit(X_train_scaled, y_memory_train)
                y_pred = self.models['memory_prediction'].predict(X_test_scaled)
                mse = mean_squared_error(y_memory_test, y_pred)
                self.logger.info(f"Memory prediction model trained. MSE: {mse:.4f}")
            
            # Train response time prediction model
            if 'response_time_prediction' in self.models:
                self.scalers['response_time_prediction'].fit(X_train)
                X_train_scaled = self.scalers['response_time_prediction'].transform(X_train)
                X_test_scaled = self.scalers['response_time_prediction'].transform(X_test)
                
                self.models['response_time_prediction'].fit(X_train_scaled, y_response_train)
                y_pred = self.models['response_time_prediction'].predict(X_test_scaled)
                mse = mean_squared_error(y_response_test, y_pred)
                self.logger.info(f"Response time prediction model trained. MSE: {mse:.4f}")
            
            # Train bottleneck classification model
            if 'bottleneck_classification' in self.models:
                self.models['bottleneck_classification'].fit(X_train, y_bottleneck)
                y_pred = self.models['bottleneck_classification'].predict(X_test)
                accuracy = accuracy_score(y_bottleneck_test, y_pred)
                self.logger.info(f"Bottleneck classification model trained. Accuracy: {accuracy:.4f}")
            
            self.model_trained = True
            self.logger.info("All ML models trained successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training ML models: {e}")
            return False
    
    def predict_performance(self, prediction_horizon_minutes: int = None) -> Optional[PerformancePrediction]:
        """Predict future performance metrics."""
        if not self.ml_enabled or not self.model_trained:
            return None
        
        if prediction_horizon_minutes is None:
            prediction_horizon_minutes = self.prediction_horizon
        
        try:
            # Get current system state
            current_metrics = self.performance_monitor.get_current_metrics()
            if not current_metrics:
                return None
            
            # Prepare features for prediction
            features = self._extract_prediction_features(current_metrics)
            X = np.array([features]).reshape(1, -1)
            
            # Make predictions
            predictions = {}
            confidence_scores = []
            
            # CPU usage prediction
            if 'cpu_prediction' in self.models:
                X_scaled = self.scalers['cpu_prediction'].transform(X)
                cpu_pred = self.models['cpu_prediction'].predict(X_scaled)[0]
                predictions['cpu_usage'] = max(0, min(100, cpu_pred))
                
                # Calculate confidence score (simplified)
                confidence_scores.append(1.0 - abs(cpu_pred - current_metrics.get('cpu_percent', 0)) / 100)
            
            # Memory usage prediction
            if 'memory_prediction' in self.models:
                X_scaled = self.scalers['memory_prediction'].transform(X)
                memory_pred = self.models['memory_prediction'].predict(X_scaled)[0]
                predictions['memory_usage'] = max(0, min(100, memory_pred))
                
                confidence_scores.append(1.0 - abs(memory_pred - current_metrics.get('memory_percent', 0)) / 100)
            
            # Response time prediction
            if 'response_time_prediction' in self.models:
                X_scaled = self.scalers['response_time_prediction'].transform(X)
                response_pred = self.models['response_time_prediction'].predict(X_scaled)[0]
                predictions['response_time'] = max(0, response_pred)
                
                confidence_scores.append(1.0 - abs(response_pred - current_metrics.get('response_time_ms', 0)) / 1000)
            
            # Bottleneck risk prediction
            if 'bottleneck_classification' in self.models:
                bottleneck_pred = self.models['bottleneck_classification'].predict(X)[0]
                predictions['bottleneck_risk'] = bottleneck_pred
            else:
                predictions['bottleneck_risk'] = 'low'
            
            # Calculate overall confidence
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
            
            # Generate recommendations
            recommendations = self._generate_recommendations(predictions, current_metrics)
            
            # Create prediction result
            prediction = PerformancePrediction(
                timestamp=time.time(),
                prediction_horizon_minutes=prediction_horizon_minutes,
                predicted_cpu_usage=predictions.get('cpu_usage', 0),
                predicted_memory_usage=predictions.get('memory_usage', 0),
                predicted_response_time=predictions.get('response_time', 0),
                confidence_score=overall_confidence,
                bottleneck_risk=predictions.get('bottleneck_risk', 'low'),
                recommendations=recommendations
            )
            
            self.logger.info(f"Performance prediction generated with confidence: {overall_confidence:.3f}")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error generating performance prediction: {e}")
            return None
    
    def _extract_prediction_features(self, current_metrics: Dict[str, Any]) -> List[float]:
        """Extract features for prediction from current metrics."""
        try:
            features = [
                current_metrics.get('cpu_percent', 0.0),
                current_metrics.get('memory_percent', 0.0),
                current_metrics.get('response_time_ms', 0.0),
                current_metrics.get('frame_rate', 0.0),
                current_metrics.get('error_count', 0),
                len(self.training_data),  # Operation count
                time.localtime().tm_hour,  # Time of day
                time.localtime().tm_wday,  # Day of week
                0  # System uptime (simplified)
            ]
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting prediction features: {e}")
            return [0.0] * len(self.feature_columns)
    
    def _generate_recommendations(self, predictions: Dict[str, Any], 
                                 current_metrics: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on predictions."""
        recommendations = []
        
        try:
            # CPU usage recommendations
            if predictions.get('cpu_usage', 0) > 80:
                recommendations.append("High CPU usage predicted. Consider optimizing resource-intensive operations.")
                recommendations.append("Review background processes and reduce unnecessary computations.")
            
            # Memory usage recommendations
            if predictions.get('memory_usage', 0) > 85:
                recommendations.append("High memory usage predicted. Implement memory cleanup routines.")
                recommendations.append("Consider reducing cache sizes and optimizing data structures.")
            
            # Response time recommendations
            if predictions.get('response_time', 0) > 200:
                recommendations.append("Slow response time predicted. Optimize UI rendering and event handling.")
                recommendations.append("Consider implementing async operations for long-running tasks.")
            
            # Bottleneck risk recommendations
            if predictions.get('bottleneck_risk') == 'high':
                recommendations.append("High bottleneck risk detected. Implement proactive monitoring.")
                recommendations.append("Consider load balancing and resource allocation optimization.")
            
            # General recommendations
            if not recommendations:
                recommendations.append("System performance appears stable. Continue monitoring.")
                recommendations.append("Consider running periodic stress tests to validate performance.")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations = ["Error generating recommendations. Check system logs."]
        
        return recommendations
    
    def analyze_bottlenecks(self) -> List[BottleneckAnalysis]:
        """Analyze current system bottlenecks."""
        try:
            current_metrics = self.performance_monitor.get_current_metrics()
            if not current_metrics:
                return []
            
            bottlenecks = []
            
            # Analyze CPU bottleneck
            cpu_analysis = self._analyze_cpu_bottleneck(current_metrics)
            if cpu_analysis:
                bottlenecks.append(cpu_analysis)
            
            # Analyze memory bottleneck
            memory_analysis = self._analyze_memory_bottleneck(current_metrics)
            if memory_analysis:
                bottlenecks.append(memory_analysis)
            
            # Analyze response time bottleneck
            response_analysis = self._analyze_response_time_bottleneck(current_metrics)
            if response_analysis:
                bottlenecks.append(response_analysis)
            
            return bottlenecks
            
        except Exception as e:
            self.logger.error(f"Error analyzing bottlenecks: {e}")
            return []
    
    def _analyze_cpu_bottleneck(self, metrics: Dict[str, Any]) -> Optional[BottleneckAnalysis]:
        """Analyze CPU-related bottlenecks."""
        try:
            cpu_usage = metrics.get('cpu_percent', 0)
            
            if cpu_usage < 60:
                return None  # No bottleneck
            
            risk_level = 'high' if cpu_usage > 80 else 'medium'
            
            contributing_factors = []
            if cpu_usage > 80:
                contributing_factors.append("Very high CPU utilization")
            elif cpu_usage > 60:
                contributing_factors.append("High CPU utilization")
            
            # Add more specific factors based on other metrics
            if metrics.get('frame_rate', 0) < 30:
                contributing_factors.append("Low frame rate indicating rendering issues")
            
            optimization_suggestions = [
                "Implement CPU usage monitoring and alerts",
                "Optimize resource-intensive operations",
                "Consider implementing task scheduling",
                "Review and optimize background processes"
            ]
            
            return BottleneckAnalysis(
                component="CPU",
                risk_level=risk_level,
                current_metrics={'cpu_percent': cpu_usage},
                predicted_metrics={'cpu_percent': cpu_usage + 5},  # Simple prediction
                contributing_factors=contributing_factors,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing CPU bottleneck: {e}")
            return None
    
    def _analyze_memory_bottleneck(self, metrics: Dict[str, Any]) -> Optional[BottleneckAnalysis]:
        """Analyze memory-related bottlenecks."""
        try:
            memory_usage = metrics.get('memory_percent', 0)
            
            if memory_usage < 70:
                return None  # No bottleneck
            
            risk_level = 'high' if memory_usage > 85 else 'medium'
            
            contributing_factors = []
            if memory_usage > 85:
                contributing_factors.append("Very high memory utilization")
            elif memory_usage > 70:
                contributing_factors.append("High memory utilization")
            
            optimization_suggestions = [
                "Implement memory leak detection",
                "Optimize data structures and algorithms",
                "Implement garbage collection strategies",
                "Monitor memory allocation patterns"
            ]
            
            return BottleneckAnalysis(
                component="Memory",
                risk_level=risk_level,
                current_metrics={'memory_percent': memory_usage},
                predicted_metrics={'memory_percent': memory_usage + 3},  # Simple prediction
                contributing_factors=contributing_factors,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing memory bottleneck: {e}")
            return None
    
    def _analyze_response_time_bottleneck(self, metrics: Dict[str, Any]) -> Optional[BottleneckAnalysis]:
        """Analyze response time bottlenecks."""
        try:
            response_time = metrics.get('response_time_ms', 0)
            
            if response_time < 100:
                return None  # No bottleneck
            
            risk_level = 'high' if response_time > 200 else 'medium'
            
            contributing_factors = []
            if response_time > 200:
                contributing_factors.append("Very slow response time")
            elif response_time > 100:
                contributing_factors.append("Slow response time")
            
            optimization_suggestions = [
                "Optimize UI rendering pipeline",
                "Implement async operations for long tasks",
                "Review event handling efficiency",
                "Consider implementing response time monitoring"
            ]
            
            return BottleneckAnalysis(
                component="Response Time",
                risk_level=risk_level,
                current_metrics={'response_time_ms': response_time},
                predicted_metrics={'response_time_ms': response_time + 10},  # Simple prediction
                contributing_factors=contributing_factors,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing response time bottleneck: {e}")
            return None
    
    def save_models(self, filepath: str = None) -> bool:
        """Save trained models to disk."""
        if not self.ml_enabled or not self.model_trained:
            return False
        
        try:
            if not filepath:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filepath = f"data/ml_models_{timestamp}.pkl"
            
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Save models and scalers
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'feature_columns': self.feature_columns,
                'model_type': self.model_type,
                'training_data_size': len(self.training_data),
                'timestamp': time.time()
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            self.logger.info(f"ML models saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving ML models: {e}")
            return False
    
    def load_models(self, filepath: str) -> bool:
        """Load trained models from disk."""
        if not self.ml_enabled:
            return False
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            # Restore models and scalers
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.feature_columns = model_data['feature_columns']
            self.model_type = model_data.get('model_type', self.model_type)
            
            self.model_trained = True
            
            self.logger.info(f"ML models loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading ML models: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get the current status of ML models."""
        return {
            'ml_enabled': self.ml_enabled,
            'model_trained': self.model_trained,
            'model_type': self.model_type,
            'training_data_size': len(self.training_data),
            'models_available': list(self.models.keys()) if self.models else [],
            'feature_columns': self.feature_columns
        }

def main():
    """Main function for testing the ML analyzer."""
    try:
        # Setup logging
        logger = get_logger("ml_analyzer")
        logger.info("Testing ML Performance Analyzer")
        
        # Create analyzer
        analyzer = MLPerformanceAnalyzer()
        
        # Check status
        status = analyzer.get_model_status()
        logger.info(f"ML Analyzer Status: {status}")
        
        if not status['ml_enabled']:
            logger.warning("ML features are disabled. Install scikit-learn to enable.")
            return
        
        # Collect training data
        if analyzer.collect_training_data():
            logger.info("Training data collected successfully")
            
            # Train models
            if analyzer.train_models():
                logger.info("Models trained successfully")
                
                # Make prediction
                prediction = analyzer.predict_performance()
                if prediction:
                    logger.info(f"Performance prediction: CPU={prediction.predicted_cpu_usage:.1f}%, "
                              f"Memory={prediction.predicted_memory_usage:.1f}%, "
                              f"Response={prediction.predicted_response_time:.1f}ms")
                    logger.info(f"Bottleneck risk: {prediction.bottleneck_risk}")
                    logger.info("Recommendations:")
                    for rec in prediction.recommendations:
                        logger.info(f"  - {rec}")
                
                # Analyze bottlenecks
                bottlenecks = analyzer.analyze_bottlenecks()
                if bottlenecks:
                    logger.info(f"Found {len(bottlenecks)} bottlenecks:")
                    for bottleneck in bottlenecks:
                        logger.info(f"  {bottleneck.component}: {bottleneck.risk_level} risk")
                
                # Save models
                analyzer.save_models()
                
            else:
                logger.error("Failed to train models")
        else:
            logger.error("Failed to collect training data")
        
    except Exception as e:
        logger.error(f"Error in ML analyzer test: {e}")

if __name__ == "__main__":
    main() 