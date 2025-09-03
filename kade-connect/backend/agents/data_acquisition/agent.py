"""
Data Acquisition Agent - Processes scout-submitted images to extract product data
Uses Google Vision API for OCR and LangChain for intelligent text parsing
"""

from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field
import cv2
import numpy as np
from google.cloud import vision
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
import json
import re
from datetime import datetime
import logging
from backend.shared.config import settings

logger = logging.getLogger(__name__)


class ProductData(BaseModel):
    """Structured output from image processing"""
    product_name: str = Field(description="Name of the product in English")
    brand: Optional[str] = Field(description="Brand name if visible", default=None)
    price: Optional[float] = Field(description="Price in LKR", default=None)
    unit: Optional[str] = Field(description="Unit (kg, g, ml, etc)", default=None)
    shop_name: Optional[str] = Field(description="Shop name if visible", default=None)
    category: Optional[str] = Field(description="Product category", default=None)
    confidence_score: float = Field(description="Confidence in extraction (0-1)", default=0.0)
    raw_text: str = Field(description="Raw OCR text", default="")
    processing_timestamp: datetime = Field(default_factory=datetime.now)


class ProcessingResult(BaseModel):
    """Complete processing result"""
    success: bool
    product_data: Optional[ProductData] = None
    error_message: Optional[str] = None
    processing_time_ms: int
    image_quality_score: Optional[float] = None


class ProductDataParser(BaseOutputParser):
    """Custom parser for LangChain output"""
    
    def parse(self, text: str) -> ProductData:
        """Parse LLM output into ProductData"""
        try:
            # Try to parse as JSON first
            if text.strip().startswith('{'):
                data = json.loads(text)
                return ProductData(**data)
            
            # Fallback to regex parsing
            product_data = {}
            
            # Extract product name
            name_match = re.search(r'product[_ ]name[:\s]+([^\n]+)', text, re.IGNORECASE)
            if name_match:
                product_data['product_name'] = name_match.group(1).strip()
            
            # Extract brand
            brand_match = re.search(r'brand[:\s]+([^\n]+)', text, re.IGNORECASE)
            if brand_match:
                product_data['brand'] = brand_match.group(1).strip()
            
            # Extract price
            price_match = re.search(r'price[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
            if price_match:
                product_data['price'] = float(price_match.group(1))
            
            # Extract unit
            unit_match = re.search(r'unit[:\s]+([^\n]+)', text, re.IGNORECASE)
            if unit_match:
                product_data['unit'] = unit_match.group(1).strip()
            
            # Extract shop name
            shop_match = re.search(r'shop[_ ]name[:\s]+([^\n]+)', text, re.IGNORECASE)
            if shop_match:
                product_data['shop_name'] = shop_match.group(1).strip()
            
            product_data['raw_text'] = text
            product_data['confidence_score'] = 0.7  # Medium confidence for regex parsing
            
            return ProductData(**product_data)
            
        except Exception as e:
            logger.error(f"Error parsing LLM output: {e}")
            return ProductData(
                product_name="Unknown Product",
                raw_text=text,
                confidence_score=0.1
            )


class DataAcquisitionAgent:
    """
    Main agent for processing scout images and extracting product data
    """
    
    def __init__(self):
        # Initialize Google Vision client
        self.vision_client = vision.ImageAnnotatorClient()
        
        # Initialize LangChain LLM
        self.llm = OpenAI(
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            model_name="gpt-3.5-turbo-instruct"
        )
        
        # Create parsing prompt for Sri Lankan context
        self.parse_prompt = PromptTemplate(
            input_variables=["ocr_text"],
            template="""
            You are an expert at extracting product information from Sri Lankan shop price tags and product labels.
            
            OCR Text from image:
            {ocr_text}
            
            Extract the following information and return as JSON:
            {{
                "product_name": "Product name in English (translate if in Sinhala/Tamil)",
                "brand": "Brand name if visible",
                "price": "Price in LKR (numbers only, no currency symbols)",
                "unit": "Unit of measurement (kg, g, ml, l, pieces, etc)",
                "shop_name": "Shop or store name if mentioned",
                "category": "Product category (groceries, dairy, beverages, etc)",
                "confidence_score": "Your confidence in the extraction (0.0 to 1.0)"
            }}
            
            Common Sri Lankan brands: Anchor, Maliban, Munchee, Kotmale, Pelwatte, CBL, etc.
            Common Sinhala/Tamil words:
            - කිරි/பால் = Milk
            - පාන්/ब्रेड = Bread  
            - බත්/चावल = Rice
            - සීනි/चीनी = Sugar
            - තේ/चाय = Tea
            
            If price is not clearly visible, set price to null.
            If product name is unclear, make your best guess based on context.
            """
        )
        
        self.parser = ProductDataParser()
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Noise reduction
            denoised = cv2.fastNlMeansDenoising(enhanced)
            
            # Sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            return sharpened
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            # Return original image if preprocessing fails
            return cv2.imread(image_path)
    
    def _assess_image_quality(self, image: np.ndarray) -> float:
        """
        Assess image quality for OCR suitability
        Returns score from 0.0 to 1.0
        """
        try:
            # Calculate Laplacian variance (focus measure)
            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
            
            # Normalize to 0-1 scale (empirically determined thresholds)
            focus_score = min(laplacian_var / 500, 1.0)
            
            # Calculate brightness score
            mean_brightness = np.mean(image)
            brightness_score = 1.0 - abs(mean_brightness - 127) / 127
            
            # Combined quality score
            quality_score = (focus_score * 0.7) + (brightness_score * 0.3)
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return 0.5  # Return neutral score if assessment fails
    
    def _extract_text_with_vision_api(self, image_path: str) -> str:
        """
        Extract text from image using Google Vision API
        """
        try:
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Configure text detection
            image_context = vision.ImageContext(
                language_hints=['en', 'si', 'ta']  # English, Sinhala, Tamil
            )
            
            response = self.vision_client.text_detection(
                image=image,
                image_context=image_context
            )
            
            if response.error.message:
                raise Exception(f'Vision API error: {response.error.message}')
            
            # Extract full text
            texts = response.text_annotations
            if texts:
                return texts[0].description
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error with Vision API: {e}")
            return ""
    
    def _parse_with_llm(self, ocr_text: str) -> ProductData:
        """
        Parse OCR text using LangChain and LLM
        """
        try:
            if not ocr_text.strip():
                return ProductData(
                    product_name="No text detected",
                    raw_text="",
                    confidence_score=0.0
                )
            
            # Create chain with prompt and parser
            chain = self.parse_prompt | self.llm | self.parser
            
            # Run the chain
            result = chain.invoke({"ocr_text": ocr_text})
            result.raw_text = ocr_text
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing with LLM: {e}")
            return ProductData(
                product_name="Parsing failed",
                raw_text=ocr_text,
                confidence_score=0.1
            )
    
    async def process_image(
        self, 
        image_path: str, 
        gps_coords: Optional[Tuple[float, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """
        Main method to process scout image and extract product data
        
        Args:
            image_path: Path to the uploaded image
            gps_coords: Optional GPS coordinates (latitude, longitude)
            metadata: Optional additional metadata
            
        Returns:
            ProcessingResult with extracted data or error information
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing image: {image_path}")
            
            # Preprocess image
            processed_image = self._preprocess_image(image_path)
            
            # Assess image quality
            quality_score = self._assess_image_quality(processed_image)
            logger.info(f"Image quality score: {quality_score}")
            
            # Extract text using Vision API
            ocr_text = self._extract_text_with_vision_api(image_path)
            logger.info(f"OCR extracted {len(ocr_text)} characters")
            
            # Parse with LLM
            product_data = self._parse_with_llm(ocr_text)
            
            # Adjust confidence based on image quality
            if product_data.confidence_score > 0:
                product_data.confidence_score *= quality_score
            
            # Add GPS coordinates if provided
            if gps_coords and hasattr(product_data, '__dict__'):
                product_data.__dict__['gps_latitude'] = gps_coords[0]
                product_data.__dict__['gps_longitude'] = gps_coords[1]
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ProcessingResult(
                success=True,
                product_data=product_data,
                processing_time_ms=int(processing_time),
                image_quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )
    
    def validate_product_data(self, product_data: ProductData) -> bool:
        """
        Validate extracted product data for quality
        """
        # Must have a product name
        if not product_data.product_name or product_data.product_name.strip() == "":
            return False
        
        # Confidence should be above minimum threshold
        if product_data.confidence_score < 0.3:
            return False
        
        # Price should be reasonable for Sri Lankan context (if provided)
        if product_data.price is not None:
            if product_data.price < 1 or product_data.price > 100000:  # 1 LKR to 100k LKR
                return False
        
        return True
