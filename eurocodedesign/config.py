"""Simple config file

Example:
    >>> from eurocodedesign.config import config
    >>> config['stepper']['output']
    True
"""
from typing import Dict, Any

config: Dict[str, Any] = {
    'stepper': {
        'output': True
    },
    'standard': {
        '_NA': {
            'country': None
        }
    }
}
