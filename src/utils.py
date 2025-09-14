# src/utils.py
import yaml
import os
import logging

def load_config(config_path):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return {}

def setup_logging(log_file="coffee_analysis.log"):
    """Setup logging configuration"""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)