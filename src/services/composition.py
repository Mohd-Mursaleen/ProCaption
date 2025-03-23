from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import requests
from io import BytesIO
from src.services.s3_service import S3Service
import os
from pathlib import Path
import cv2
import logging
import math
import random
import time
import tempfile
import aiofiles
import aiohttp
import urllib.parse

logger = logging.getLogger(__name__)

class CompositionService:
    def __init__(self):
        self.s3 = S3Service()
        self.fonts_dir = Path("assets/fonts")
        self.fonts_dir.mkdir(parents=True, exist_ok=True)
        
        # Map of stylistic font names to actual font files
        self.dramatic_fonts = {
            "anton": "Anton-Regular.ttf",
            "sixcaps": "SixCaps.ttf",
            "impact": "Impact",  # System font as fallback
            "arial_bold": "Arial Bold",  # System font as fallback
            "helvetica_bold": "Helvetica Bold",  # System font as fallback
            "boldonse": "Boldonse.ttf"  # Added Boldonse font
        }
        
        # 3D effect presets
        self.effect_presets = {
            "shadow": {
                "offset": (5, 5),
                "color": "#000000",
                "opacity": 0.5,
                "blur": 3
            },
            "outline": {
                "width": 2,
                "color": "#000000",
                "opacity": 1.0
            },
            "glow": {
                "color": "#FFFFFF",
                "radius": 10,
                "opacity": 0.7
            },
            "3d_depth": {
                "layers": 10,
                "angle": 45,  # degrees
                "distance": 2,
                "color_gradient": ["#333333", "#666666", "#999999"]
            },
            "text_gradient": {
                "colors": ["#FF0000", "#FFFF00", "#00FF00", "#00FFFF", "#0000FF", "#FF00FF"],
                "direction": "horizontal",  # horizontal, vertical, diagonal
                "use_mask": True  # Use text as mask for gradient
            },
            "background_gradient": {
                "colors": ["#FF000088", "#0000FF88"],  # With alpha channel for transparency
                "direction": "vertical",
                "padding": 10,  # Padding around text in pixels
                "radius": 0,  # Border radius for the background
                "opacity": 0.7  # Overall opacity of the background
            }
        }

        # Ensure the uploads directory exists
        Path("uploads/public").mkdir(parents=True, exist_ok=True)
        Path("uploads/temp").mkdir(parents=True, exist_ok=True)
        
        # Base directory for the application
        self.base_dir = Path(os.getcwd())
        logger.info(f"CompositionService initialized with base directory: {self.base_dir}")

    async def _resolve_image_path(self, image_path: str) -> str:
        """
        Resolves various image path formats to an actual file path that can be opened.
        Handles URLs, S3 paths, and local paths, ensuring the file exists.
        
        Args:
            image_path: URL, S3 path, or local file path
            
        Returns:
            A local file path that can be opened by PIL
        """
        logger.info(f"Resolving image path: {image_path}")
        
        # If it's a URL, download it
        if image_path.startswith(('http://', 'https://')):
            logger.info(f"Detected URL path: {image_path}")
            try:
                # Create a temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                temp_path = temp_file.name
                temp_file.close()
                
                # Download the file
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_path) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to download image: HTTP {response.status}")
                        
                        content = await response.read()
                        async with aiofiles.open(temp_path, 'wb') as f:
                            await f.write(content)
                
                logger.info(f"Downloaded image to temporary file: {temp_path}")
                return temp_path
            
            except Exception as e:
                logger.error(f"Error downloading image from URL: {str(e)}")
                raise ValueError(f"Failed to download image from URL: {str(e)}")
        
        # If it's a relative path starting with /uploads
        elif image_path.startswith('/uploads/'):
            logger.info(f"Detected /uploads/ path: {image_path}")
            
            # Try different path resolutions
            possible_paths = [
                # Absolute path as provided
                image_path,
                # Remove leading slash and use relative to current directory
                str(self.base_dir / image_path[1:]),
                # Try relative to the current working directory
                str(Path("uploads") / image_path[9:])  # Remove "/uploads/" prefix
            ]
            
            for path in possible_paths:
                logger.info(f"Trying path: {path}")
                if os.path.isfile(path):
                    logger.info(f"Found file at: {path}")
                    return path
            
            # If we got here, none of the paths worked
            logger.error(f"File not found after trying multiple path resolutions: {possible_paths}")
            raise FileNotFoundError(f"Could not locate image file at any of these locations: {', '.join(possible_paths)}")
        
        # Otherwise, treat it as a local path
        else:
            logger.info(f"Treating as local path: {image_path}")
            if os.path.isfile(image_path):
                return image_path
            
            # Try with base directory
            full_path = str(self.base_dir / image_path)
            if os.path.isfile(full_path):
                return full_path
                
            logger.error(f"File not found: {image_path} or {full_path}")
            raise FileNotFoundError(f"File not found: {image_path}")

    async def _get_image_from_url(self, url: str) -> Image.Image:
        """Fetches an image from a URL with improved error handling"""
        try:
            # Set a timeout for the request to prevent hanging
            response = requests.get(url, timeout=60)
            response.raise_for_status()  # Raise an exception for 4xx/5xx responses
            return Image.open(BytesIO(response.content)).convert('RGBA')
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching image from URL {url}: {str(e)}")
            raise ValueError(f"Failed to fetch image from URL: {str(e)}")
        except Exception as e:
            logging.error(f"Error processing image from URL {url}: {str(e)}")
            raise ValueError(f"Failed to process image: {str(e)}")
        
    def _get_font(self, font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
        """Try to load the specified font or fall back to a suitable alternative"""
        try:
            # Check if font is in our map of known fonts
            if font_name.lower() in self.dramatic_fonts:
                font_file = self.dramatic_fonts[font_name.lower()]
                
                # If it's a local file name, try to load it from our fonts directory
                if font_file.endswith('.ttf') or font_file.endswith('.otf'):
                    font_path = self.fonts_dir / font_file
                    if font_path.exists():
                        return ImageFont.truetype(str(font_path), font_size)
                
                # Otherwise assume it's a system font
                return ImageFont.truetype(font_file, font_size)
            
            # Direct font name as fallback
            return ImageFont.truetype(font_name, font_size)
        except Exception as e:
            logging.warning(f"Failed to load font {font_name}: {e}")
            # Fallback to default font
            try:
                return ImageFont.truetype("Arial", font_size)
            except:
                return ImageFont.load_default()

    def _apply_text_effects(
        self, 
        draw: ImageDraw.ImageDraw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        color: str = "#FFFFFF",
        effects: Dict[str, Any] = None
    ) -> None:
        """
        Apply text with visual effects to the image.
        
        Args:
            draw: ImageDraw object
            text: Text to draw
            position: (x, y) position
            font: Font to use
            color: Text color in hex format
            effects: Dictionary with text effects settings
        """
        # Log all input parameters for debugging
        logger.info(f"_apply_text_effects: text='{text}', position={position}, font={font}, color={color}")
        logger.info(f"Effects: {effects}")
        
        # Get bounding box of the text to properly center it
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
        
        logger.debug(f"Text bounding box: width={text_width}, height={text_height}")
        
        # Convert position tuple to x, y coordinates
        if isinstance(position, tuple) and len(position) == 2:
            x, y = position
        else:
            # Handle dictionary positions (from frontend)
            if isinstance(position, dict) and 'x' in position and 'y' in position:
                x = position['x']
                y = position['y']
            else:
                logger.warning(f"Invalid position format: {position}, using (0, 0)")
                x, y = 0, 0
                
        logger.debug(f"Original position: x={x}, y={y}")
                
        # Apply the ORIGINAL positioning logic that worked correctly
        # 1. Center horizontally
        centered_x = x - text_width // 2
        
        # 2. Apply the vertical adjustment factor that matches CSS rendering
        # This factor (0.375 or 37.5%) was calibrated to match frontend preview
        vertical_adjustment_factor = 0.375
        vertical_adjustment = int(text_height * vertical_adjustment_factor)
        
        # 3. Center vertically and apply the adjustment
        centered_y = y - text_height // 2 - vertical_adjustment
        
        logger.debug(f"Adjusted position: x={centered_x}, y={centered_y} (with {vertical_adjustment}px vertical adjustment)")
        
        # If no effects specified or effects is None, just draw the text
        if not effects:
            logger.debug("No effects specified, drawing plain text")
            draw.text((centered_x, centered_y), text, fill=color, font=font)
            return
            
        # Check if it's the legacy format (direct keys) or new format (type + settings)
        if 'type' in effects:
            # Process the new unified effects format
            effect_type = effects.get('type')
            settings = effects.get('settings', {})
            
            logger.debug(f"Using new effects format: type={effect_type}")
            
            if effect_type == 'shadow':
                # Shadow effect
                shadow_offset = settings.get('offset', [5, 5])
                shadow_color = settings.get('color', '#000000')
                shadow_opacity = settings.get('opacity', 0.5)
                shadow_blur = settings.get('blur', 3)
                
                # Ensure offset is a tuple/list with at least 2 elements
                if isinstance(shadow_offset, (list, tuple)) and len(shadow_offset) >= 2:
                    offset_x, offset_y = shadow_offset[0], shadow_offset[1]
                else:
                    offset_x, offset_y = 5, 5
                
                logger.debug(f"Applying shadow effect: offset=({offset_x}, {offset_y}), color={shadow_color}, opacity={shadow_opacity}, blur={shadow_blur}")
                
                # Convert shadow color to RGBA with opacity
                shadow_rgba = self._hex_to_rgba(shadow_color)
                shadow_rgba = (shadow_rgba[0], shadow_rgba[1], shadow_rgba[2], int(255 * shadow_opacity))
                
                # Apply shadow
                shadow_x = centered_x + offset_x
                shadow_y = centered_y + offset_y
                
                # Draw shadow text
                draw.text((shadow_x, shadow_y), text, fill=shadow_rgba, font=font)
                
                # Draw main text on top
                draw.text((centered_x, centered_y), text, fill=color, font=font)
                
            elif effect_type == 'outline':
                # Outline effect
                outline_width = settings.get('width', 2)
                outline_color = settings.get('color', '#000000')
                outline_opacity = settings.get('opacity', 1.0)
                
                logger.debug(f"Applying outline effect: width={outline_width}, color={outline_color}, opacity={outline_opacity}")
                
                # Convert outline color to RGBA with opacity
                outline_rgba = self._hex_to_rgba(outline_color)
                outline_rgba = (outline_rgba[0], outline_rgba[1], outline_rgba[2], int(255 * outline_opacity))
                
                # Draw text multiple times around the target position for outline
                for offset_x in range(-outline_width, outline_width + 1):
                    for offset_y in range(-outline_width, outline_width + 1):
                        # Skip the center pixel
                        if offset_x == 0 and offset_y == 0:
                            continue
                            
                        # Draw the outline text
                        draw.text(
                            (centered_x + offset_x, centered_y + offset_y),
                            text,
                            fill=outline_rgba,
                            font=font
                        )
                
                # Draw the main text on top
                draw.text((centered_x, centered_y), text, fill=color, font=font)
                
            elif effect_type == 'glow':
                # Glow effect
                glow_color = settings.get('color', '#FFFFFF')
                glow_radius = settings.get('radius', 10)
                glow_opacity = settings.get('opacity', 0.7)
                
                logger.debug(f"Applying glow effect: color={glow_color}, radius={glow_radius}, opacity={glow_opacity}")
                
                # Convert glow color to RGBA with opacity
                glow_rgba = self._hex_to_rgba(glow_color)
                glow_rgba = (glow_rgba[0], glow_rgba[1], glow_rgba[2], int(255 * glow_opacity))
                
                # Create a series of increasingly transparent outlines
                steps = min(glow_radius, 20)  # Limit to 20 steps for performance
                
                for i in range(1, steps + 1):
                    current_radius = (i / steps) * glow_radius
                    current_opacity = glow_opacity * (1 - (i / steps))
                    
                    current_rgba = (glow_rgba[0], glow_rgba[1], glow_rgba[2], int(255 * current_opacity))
                    
                    # Draw text at various offsets to create the glow
                    for angle in range(0, 360, 30):  # 12 points around the circle
                        offset_x = int(current_radius * math.cos(math.radians(angle)))
                        offset_y = int(current_radius * math.sin(math.radians(angle)))
                        
                        draw.text(
                            (centered_x + offset_x, centered_y + offset_y),
                            text,
                            fill=current_rgba,
                            font=font
                        )
                
                # Draw the main text on top
                draw.text((centered_x, centered_y), text, fill=color, font=font)
                
            elif effect_type == '3d_depth':
                # 3D depth effect
                layers = settings.get('layers', 10)
                angle = settings.get('angle', 45)
                distance = settings.get('distance', 2)
                color_gradient = settings.get('color_gradient', ['#333333', '#666666', '#999999'])
                
                logger.debug(f"Applying 3D depth effect: layers={layers}, angle={angle}, distance={distance}")
                
                # Convert angle to radians
                angle_rad = math.radians(angle)
                
                # Calculate x and y offsets based on the angle
                dx = math.cos(angle_rad) * distance
                dy = math.sin(angle_rad) * distance
                
                # Draw layers back to front
                for i in range(layers, 0, -1):
                    # Map layer index to color index in gradient
                    color_index = min(int((i / layers) * (len(color_gradient) - 1)), len(color_gradient) - 1)
                    layer_color = color_gradient[color_index]
                    
                    layer_x = centered_x - int(i * dx)
                    layer_y = centered_y - int(i * dy)
                    
                    draw.text((layer_x, layer_y), text, fill=layer_color, font=font)
                
                # Draw the main text on top
                draw.text((centered_x, centered_y), text, fill=color, font=font)
                
            else:
                # Unknown effect type, just draw plain text
                logger.warning(f"Unknown effect type: {effect_type}, drawing plain text")
                draw.text((centered_x, centered_y), text, fill=color, font=font)
        
        else:
            # Legacy format (for backward compatibility)
            logger.debug("Using legacy effects format (direct keys)")
            
            # Apply shadow if specified
            if 'shadow' in effects:
                shadow_settings = effects['shadow']
                shadow_offset = shadow_settings.get('offset', (5, 5))
                shadow_color = shadow_settings.get('color', '#000000')
                
                # Draw shadow
                shadow_x = centered_x + shadow_offset[0]
                shadow_y = centered_y + shadow_offset[1]
                
                draw.text((shadow_x, shadow_y), text, fill=shadow_color, font=font)
            
            # Draw the main text
            draw.text((centered_x, centered_y), text, fill=color, font=font)

    def _hex_to_rgba(self, hex_color: str) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple"""
        # Handle colors with alpha in hex format (#RRGGBBAA)
        if hex_color.startswith('#'):
            hex_color = hex_color.lstrip('#')
            
            # Handle different hex formats
            if len(hex_color) == 8:  # #RRGGBBAA
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                a = int(hex_color[6:8], 16)
            elif len(hex_color) == 6:  # #RRGGBB
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                a = 255
            elif len(hex_color) == 4:  # #RGBA
                r = int(hex_color[0], 16) * 17
                g = int(hex_color[1], 16) * 17
                b = int(hex_color[2], 16) * 17
                a = int(hex_color[3], 16) * 17
            elif len(hex_color) == 3:  # #RGB
                r = int(hex_color[0], 16) * 17
                g = int(hex_color[1], 16) * 17
                b = int(hex_color[2], 16) * 17
                a = 255
            else:
                # Default to white fully opaque if invalid format
                r, g, b, a = 255, 255, 255, 255
        else:
            # Default to white fully opaque if not hex format
            r, g, b, a = 255, 255, 255, 255
            
        return (r, g, b, a)
    
    def _suggest_text_positions(
        self, 
        background: Image.Image, 
        text: str,
        font: ImageFont.FreeTypeFont,
        text_size: Tuple[int, int]
    ) -> List[Dict[str, int]]:
        """Suggest optimal text positions based on background content"""
        width, height = background.size
        
        # Convert to numpy array for analysis
        bg_array = np.array(background)
        
        # Check if alpha channel exists
        has_alpha = bg_array.shape[2] == 4
        
        # Create grid of potential positions
        grid_size = 3  # 3x3 grid
        positions = []
        
        for y_idx in range(grid_size):
            for x_idx in range(grid_size):
                # Calculate position in grid
                x_pos = int(width * (x_idx + 0.5) / grid_size - text_size[0] / 2)
                y_pos = int(height * (y_idx + 0.5) / grid_size - text_size[1] / 2)
                
                # Keep within bounds
                x_pos = max(10, min(width - text_size[0] - 10, x_pos))
                y_pos = max(10, min(height - text_size[1] - 10, y_pos))
                
                # Check if this position is good (transparent or empty area)
                region = bg_array[
                    y_pos:min(y_pos + text_size[1], height), 
                    x_pos:min(x_pos + text_size[0], width)
                ]
                
                if has_alpha:
                    # Calculate average alpha (transparency)
                    avg_alpha = np.mean(region[:, :, 3]) if region.size > 0 else 0
                    
                    # If area is transparent (low alpha), it's a good candidate
                    if avg_alpha < 128:  # Less than 50% opaque
                        positions.append({"x": x_pos, "y": y_pos, "score": 255 - avg_alpha})
                else:
                    # For images without alpha, check brightness (darker areas might be better for light text)
                    avg_brightness = np.mean(region) if region.size > 0 else 0
                    positions.append({"x": x_pos, "y": y_pos, "score": 255 - avg_brightness})
        
        # Sort by score (higher is better)
        positions.sort(key=lambda p: p["score"], reverse=True)
        
        # Return top 3 positions
        return positions[:3]

    async def add_text(
        self,
        background_path: str,
        text: str,
        position: Dict[str, int],
        font_size: int = 120,  # Increased default font size for dramatic effect
        color: str = "#FFFFFF",  # Changed default to white for better visibility
        font_name: str = "Impact",  # Changed default font for dramatic effect
        effects: Dict[str, Any] = None  # New parameter for text effects
    ) -> Tuple[str, dict]:
        """
        Add text to an image at a specific position
        
        Args:
            background_path: Path to the background image
            text: Text to add
            position: Dictionary with x and y coordinates
            font_size: Font size in points
            color: Text color in hex format
            font_name: Font name
            effects: Dictionary with text effects settings
            
        Returns:
            Path to the image with text added
        """
        logger.info(f"Adding text '{text}' to background image: {background_path}")
        logger.info(f"Using font: {font_name}, size: {font_size}, position: {position}")
        
        try:
            # Resolve the image path
            resolved_path = await self._resolve_image_path(background_path)
            logger.info(f"Resolved background path to: {resolved_path}")
            
            # Open the background image
            background = Image.open(resolved_path).convert('RGBA')
            
            # Log image dimensions to help diagnose positioning issues
            logging.info(f"Original background dimensions: {background.size}")
            
            # Create a drawing canvas
            canvas = background.copy()
            draw = ImageDraw.Draw(canvas)
            
            # Get the font
            font = self._get_font(font_name, font_size)
            
            # Calculate text size for info purposes
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Extract position coordinates and ensure they're integers
            pos_x = int(position.get('x', 10))
            pos_y = int(position.get('y', 10))
            
            # Log the text position for debugging
            logging.info(f"Rendering text at position: x={pos_x}, y={pos_y}, font_size={font_size}")
            logging.info(f"Text dimensions: width={text_width}, height={text_height}")
            
            # Apply text with effects using position coordinates
            # Note: position adjustment is handled inside _apply_text_effects
            self._apply_text_effects(
                draw, 
                text, 
                (pos_x, pos_y), 
                font, 
                color, 
                effects
            )
            
            # Save the result
            processed_dir = Path("uploads/processed")
            processed_dir.mkdir(exist_ok=True)
            
            # Generate a unique filename based on the original path
            base_name = os.path.basename(background_path)
            base_name_without_ext = os.path.splitext(base_name)[0]
            text_path = processed_dir / f"{base_name_without_ext}_text_{int(time.time())}.png"
            
            # Save locally
            canvas.save(text_path, "PNG")
            
            # Log the path of the saved image
            logging.info(f"Saved text image to: {text_path}")
            
            # Upload to cloud storage
            cloud_url = await self.s3.upload_image(str(text_path))
            
            # Store the original (non-adjusted) position in the return info
            # This ensures the frontend gets back the same position it sent
            return str(text_path), {
                "path": str(text_path),
                "cloud_url": cloud_url,
                "text_size": {
                    "width": text_width,
                    "height": text_height
                },
                "position": {
                    "x": pos_x,
                    "y": pos_y
                },
                "image_size": {
                    "width": background.width,
                    "height": background.height
                }
            }
        except Exception as e:
            logging.error(f"Error in add_text: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to add text: {str(e)}")

    async def add_dramatic_text(
        self,
        background_path: str,
        text: str,
        position: Dict[str, int],
        font_size: int = 150,
        color: str = "#FFFFFF",
        font_name: str = "anton",  # Default to Anton since we downloaded it
        with_period: bool = True,  # Option to add period like in examples
        to_uppercase: bool = False,  # Make uppercase conversion optional
        effects: Dict[str, Any] = None  # Added effects parameter
    ) -> Tuple[str, dict]:
        """
        Add dramatic impact-style text to the image
        
        Args:
            background_path: Path to the background image
            text: Text to add
            position: Dictionary with x and y coordinates
            font_size: Font size in points
            color: Text color in hex format
            font_name: Font name (defaults to Anton for dramatic effect)
            with_period: Whether to add a period at the end of the text
            to_uppercase: Whether to convert the text to uppercase
            effects: Dictionary with text effects settings
            
        Returns:
            Path to the image with dramatic text added
        """
        try:
            # Apply transformations to the text
            processed_text = text
            
            # Apply uppercase conversion if requested
            if to_uppercase:
                processed_text = processed_text.upper()
                
            # Add period if requested and not already ending with punctuation
            if with_period and not processed_text[-1] in ".!?":
                processed_text = processed_text + "."
                
            # Use standard text effect for dramatic text
            shadow_effect = {
                "type": "shadow",
                "settings": {
                    "offset": [5, 5],
                    "color": "#000000",
                    "opacity": 0.5,
                    "blur": 3
                }
            }
            
            # Use provided effects or default to shadow
            final_effects = effects if effects else shadow_effect
                
            result, info = await self.add_text(
                background_path=background_path,
                text=processed_text,
                position=position,
                font_size=font_size,
                color=color,
                font_name=font_name,
                effects=final_effects
            )
            
            return result, info
        except Exception as e:
            logging.error(f"Error in add_dramatic_text: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to add dramatic text: {str(e)}")

    async def compose_final_image(
        self,
        background_with_text_path: str,
        foreground_path: str,
        blend_mode: str = 'normal',  # Added parameter for blend mode
        blend_opacity: float = 1.0  # Added parameter for opacity
    ) -> str:
        """
        Compose the final image by overlaying the foreground on top of the background with text
        
        Args:
            background_with_text_path: Path to the background image with text
            foreground_path: Path to the foreground image
            blend_mode: Blend mode for composition
            blend_opacity: Opacity for the blend
            
        Returns:
            Path to the final composed image
        """
        try:
            # Resolve the image paths
            background_resolved = await self._resolve_image_path(background_with_text_path)
            foreground_resolved = await self._resolve_image_path(foreground_path)
            
            # Load the images
            background = Image.open(background_resolved).convert('RGBA')
            foreground = Image.open(foreground_resolved).convert('RGBA')
            
            # Resize foreground to match background if needed
            if foreground.size != background.size:
                foreground = foreground.resize(background.size, Image.Resampling.LANCZOS)
            
            # Create a composite
            result = Image.alpha_composite(background, foreground)
            
            # Create a unique filename for the result
            timestamp = int(time.time())
            result_path = Path(f"uploads/public/composed_{timestamp}.png")
            result.save(result_path)
            
            # Upload to S3 and get public URL
            result_info = await self.s3.upload_image(result_path)
            
            return result_info['url']
        except Exception as e:
            logging.error(f"Error in compose_final_image: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to compose final image: {str(e)}")

    async def generate_font_size_previews(
        self,
        background_path: str,
        text: str,
        position: Dict[str, int],
        font_name: str = "anton"
    ) -> Tuple[List[int], Dict[str, str]]:
        """Generate previews of different font sizes for the user to choose from"""
        # Define range of font sizes to preview
        sizes = [80, 100, 120, 150, 180, 220]
        previews = {}
        
        # Generate preview for each size
        for size in sizes:
            # Add text with the specified size
            _, info = await self.add_text(
                background_path,
                text,
                position,
                font_size=size,
                font_name=font_name
            )
            
            # Store cloud URL
            previews[str(size)] = info['cloud_url']
        
        return sizes, previews

    async def suggest_text_positions(
        self,
        background_path: str,
        text: str,
        font_size: int = 120,
        font_name: str = "anton"
    ) -> List[Dict[str, int]]:
        """Suggest optimal text positions based on background content"""
        # Load the background image
        if background_path.startswith('http'):
            background = await self._get_image_from_url(background_path)
        else:
            background = Image.open(background_path).convert('RGBA')
        
        # Get the font and calculate text size
        font = self._get_font(font_name, font_size)
        
        # Create a temp drawing context to measure text
        temp_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Get position suggestions
        return self._suggest_text_positions(
            background, 
            text, 
            font, 
            (text_width, text_height)
        )

    def _get_social_media_dimensions(self, template_name: str) -> Tuple[int, int]:
        """Get dimensions for a social media template"""
        templates = {
            "instagram_post": (1080, 1080),
            "instagram_story": (1080, 1920),
            "facebook_post": (1200, 630),
            "twitter_post": (1600, 900),
            "linkedin_post": (1200, 627),
            "youtube_thumbnail": (1280, 720),
            "tiktok_video": (1080, 1920)
        }
        
        return templates.get(template_name, (1080, 1080))  # Default to square

    async def create_template(
        self,
        foreground_path: str,
        background_color: str = "#000000",
        template_name: str = "instagram_post",
        padding_percent: int = 10
    ) -> str:
        """Create a social media template with the foreground subject"""
        # Load foreground image
        if foreground_path.startswith('http'):
            foreground = await self._get_image_from_url(foreground_path)
        else:
            foreground = Image.open(foreground_path).convert('RGBA')
        
        # Get template dimensions
        width, height = self._get_social_media_dimensions(template_name)
        
        # Create background with specified color
        background = Image.new('RGBA', (width, height), background_color)
        
        # Calculate scaling to fit foreground within template
        # while maintaining aspect ratio and adding padding
        fg_width, fg_height = foreground.size
        fg_aspect = fg_width / fg_height
        
        # Calculate available space after padding
        padding_px = min(width, height) * padding_percent // 100
        avail_width = width - (2 * padding_px)
        avail_height = height - (2 * padding_px)
        
        # Scale foreground to fit available space
        if avail_width / avail_height > fg_aspect:
            # Constrained by height
            new_height = avail_height
            new_width = int(new_height * fg_aspect)
        else:
            # Constrained by width
            new_width = avail_width
            new_height = int(new_width / fg_aspect)
        
        # Resize foreground
        foreground_resized = foreground.resize((new_width, new_height), Image.LANCZOS)
        
        # Calculate position to center in template
        pos_x = (width - new_width) // 2
        pos_y = (height - new_height) // 2
        
        # Paste foreground onto background
        background.paste(foreground_resized, (pos_x, pos_y), foreground_resized)
        
        # Save result
        processed_dir = Path("uploads/processed")
        template_path = processed_dir / f"template_{template_name}_{int(time.time())}.png"
        background.save(template_path, "PNG")
        
        # Upload to cloud storage
        cloud_url = await self.s3.upload_image(str(template_path))
        
        return cloud_url

    async def add_multiple_text_layers(self, background_path: str, text_layers: List['TextLayer']) -> str:
        """
        Add multiple text layers to a background image
        
        Args:
            background_path: Path to the background image
            text_layers: List of TextLayer objects
            
        Returns:
            Path to the image with all text layers added
        """
        try:
            # Resolve the background path
            resolved_path = await self._resolve_image_path(background_path)
            
            # Open the background image
            background = Image.open(resolved_path).convert('RGBA')
            logger.info(f"Loaded background image: {resolved_path}, size: {background.size}")
            
            # Create a draw object
            draw = ImageDraw.Draw(background)
            
            # Process each text layer
            for i, layer in enumerate(text_layers):
                text = layer.text
                
                # Get position as a tuple directly from the layer
                pos_x = int(layer.position.get('x', 10))
                pos_y = int(layer.position.get('y', 10))
                position = (pos_x, pos_y)
                
                # Extract style properties with defaults
                font_size = layer.style.get('font_size', 120)
                color = layer.style.get('color', '#FFFFFF')
                font_name = layer.style.get('font_name', 'anton')
                effects = layer.style.get('effects', None)
                
                # Log text layer details
                logger.info(f"Processing text layer {i+1}: text='{text}', position={position}, font={font_name}, size={font_size}")
                
                # Get the font
                font = self._get_font(font_name, font_size)
                
                # Apply text effects - position adjustment happens inside this method
                self._apply_text_effects(draw, text, position, font, color, effects)
            
            # Save the result
            timestamp = int(time.time())
            result_path = Path(f"uploads/public/multilayer_{timestamp}.png")
            background.save(result_path)
            logger.info(f"Saved multilayer image to: {result_path}")
            
            # Upload to S3 and get public URL
            result_info = await self.s3.upload_image(result_path)
            logger.info(f"Uploaded multilayer image to S3: {result_info['url']}")
            
            return result_info['url']
        except Exception as e:
            logging.error(f"Error in add_multiple_text_layers: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to add multiple text layers: {str(e)}")

class TextLayer:
    def __init__(self, text: str, position: Dict[str, int], style: Dict):
        self.text = text
        self.position = position
        self.style = style

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "position": self.position,
            "style": self.style
        }