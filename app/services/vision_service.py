"""
Vision Service for AI Assistant Bot
Handles image analysis using computer vision models
"""

import logging
import asyncio
import aiohttp
import base64
import io
from typing import Dict, Any, Tuple, Optional
from PIL import Image
import json

logger = logging.getLogger(__name__)

class VisionService:
    """Service for analyzing images using computer vision models."""
    
    def __init__(self):
        """Initialize the vision service."""
        # Basic image analysis capabilities
        self.image_analysis_prompts = [
            "Describe this image in detail",
            "What do you see in this image?",
            "Analyze the content of this image",
            "Provide a detailed description of this image"
        ]
        
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze image data and return basic information.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with image analysis results
        """
        try:
            # Basic image analysis using PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Extract basic image information
            analysis = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "description": f"Image with dimensions {image.width}x{image.height} pixels in {image.format} format"
            }
            
            # Add color information if available
            if image.mode in ['RGB', 'RGBA']:
                analysis["color_mode"] = "color"
            elif image.mode == 'L':
                analysis["color_mode"] = "grayscale"
            else:
                analysis["color_mode"] = "other"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {"error": f"Failed to analyze image: {str(e)}"}
    
    async def get_image_analysis_prompt(self) -> str:
        """Get a random prompt for image analysis."""
        import random
        return random.choice(self.image_analysis_prompts)
    
    def is_image_file(self, filename: str) -> bool:
        """Check if filename corresponds to an image file."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        return any(filename.lower().endswith(ext) for ext in image_extensions)
