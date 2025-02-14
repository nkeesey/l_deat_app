from abc import ABC, abstractmethod

class BaseFigure(ABC):
    """Base class for all figures"""
    def __init__(self, data):
        self.data = data
        
    @abstractmethod
    def create(self):
        """Create the figure"""
        pass
        
    @abstractmethod
    def update(self, **kwargs):
        """Update the figure with new parameters"""
        pass