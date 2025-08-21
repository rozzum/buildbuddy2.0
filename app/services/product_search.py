"""
Product Search Service for AI Assistant Bot
Handles product search and provides links to specific items
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
import asyncio

logger = logging.getLogger(__name__)

class ProductSearchService:
    """Service for searching products and providing links."""
    
    def __init__(self):
        """Initialize product search service."""
        self.search_engines = {
            'russian': {
                'onliner': 'https://catalog.onliner.by/search?query={query}',
                'deal': 'https://deal.by/search?q={query}',
                'wildberries': 'https://www.wildberries.by/catalog/0/search.aspx?search={query}',
                'ozon': 'https://www.ozon.by/search/?text={query}',
                'yandex_market': 'https://market.yandex.ru/search?text={query}'
            },
            'english': {
                'amazon': 'https://www.amazon.com/s?k={query}',
                'wayfair': 'https://www.wayfair.com/search?query={query}',
                'west_elm': 'https://www.westelm.com/search?q={query}',
                'cb2': 'https://www.cb2.com/search?q={query}',
                'overstock': 'https://www.overstock.com/search?keywords={query}'
            }
        }
        
        # Common product categories and search terms
        self.product_categories = {
            'furniture': {
                'russian': ['мебель', 'диван', 'кресло', 'стол', 'стул', 'шкаф', 'комод', 'кровать'],
                'english': ['furniture', 'sofa', 'armchair', 'table', 'chair', 'cabinet', 'dresser', 'bed']
            },
            'lighting': {
                'russian': ['освещение', 'лампа', 'светильник', 'люстра', 'бра', 'торшер'],
                'english': ['lighting', 'lamp', 'chandelier', 'sconce', 'floor lamp']
            },
            'decor': {
                'russian': ['декор', 'картина', 'ваза', 'подушка', 'ковер', 'зеркало'],
                'english': ['decor', 'art', 'vase', 'pillow', 'rug', 'mirror']
            },
            'kitchen': {
                'russian': ['кухня', 'кухонный гарнитур', 'мойка', 'плита', 'холодильник'],
                'english': ['kitchen', 'kitchen set', 'sink', 'stove', 'refrigerator']
            }
        }
    
    def detect_product_query(self, text: str, language: str) -> Optional[Dict[str, any]]:
        """
        Detect if user is asking about a specific product.
        
        Args:
            text: User's text input
            language: Language ('russian' or 'english')
            
        Returns:
            Product query info or None if not a product query
        """
        text_lower = text.lower()
        
        # Check for product-related keywords
        for category, keywords in self.product_categories.items():
            for keyword in keywords[language]:
                if keyword in text_lower:
                    # Extract product name
                    product_name = self._extract_product_name(text, keyword, language)
                    if product_name:
                        return {
                            'category': category,
                            'keyword': keyword,
                            'product_name': product_name,
                            'language': language,
                            'is_specific_query': self._is_specific_query(text_lower)
                        }
        
        return None
    
    def _extract_product_name(self, text: str, keyword: str, language: str) -> Optional[str]:
        """Extract product name from text."""
        # Look for patterns like "где купить [product]", "цена [product]", etc.
        patterns = {
            'russian': [
                r'где купить (.*?)(?:\?|$|\.)',
                r'цена (.*?)(?:\?|$|\.)',
                r'стоимость (.*?)(?:\?|$|\.)',
                r'заказать (.*?)(?:\?|$|\.)',
                r'такой (.*?)(?:\?|$|\.)',
                r'этот (.*?)(?:\?|$|\.)',
                r'кресла-облака',  # Specific product names
                r'дивана',
                r'стола',
                r'шкафа'
            ],
            'english': [
                r'where to buy (.*?)(?:\?|$|\.)',
                r'price of (.*?)(?:\?|$|\.)',
                r'cost of (.*?)(?:\?|$|\.)',
                r'order (.*?)(?:\?|$|\.)',
                r'such (.*?)(?:\?|$|\.)',
                r'this (.*?)(?:\?|$|\.)',
                r'can i buy (.*?)(?:\?|$|\.)',
                r'where can i buy (.*?)(?:\?|$|\.)'
            ]
        }
        
        for pattern in patterns[language]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                product_name = match.group(1).strip()
                if product_name and len(product_name) > 2:
                    return product_name
        
        # If no pattern match, try to extract after keyword
        keyword_index = text.lower().find(keyword)
        if keyword_index != -1:
            after_keyword = text[keyword_index + len(keyword):].strip()
            if after_keyword and len(after_keyword) > 2:
                # Take first few words after keyword
                words = after_keyword.split()[:4]  # Increased to 4 words
                return ' '.join(words)
        
        # Special case: if keyword is the product itself (like "кресла-облака")
        if keyword in text.lower():
            # Extract the full product name including the keyword
            words = text.lower().split()
            for i, word in enumerate(words):
                if keyword in word:
                    # Get surrounding words for context
                    start = max(0, i-1)
                    end = min(len(words), i+2)
                    return ' '.join(words[start:end])
        
        return None
    
    def _is_specific_query(self, text: str) -> bool:
        """Check if query is specific (asking about specific product)."""
        specific_indicators = [
            'где купить', 'where to buy', 'цена', 'price', 'стоимость', 'cost',
            'заказать', 'order', 'такой', 'such', 'этот', 'this'
        ]
        return any(indicator in text for indicator in specific_indicators)
    
    def generate_product_links(self, product_query: Dict[str, any]) -> List[Dict[str, str]]:
        """
        Generate search links for the product.
        
        Args:
            product_query: Product query info
            
        Returns:
            List of search links
        """
        language = product_query['language']
        product_name = product_query['product_name']
        
        if language not in self.search_engines:
            return []
        
        links = []
        for engine_name, url_template in self.search_engines[language].items():
            # Clean product name for URL
            clean_query = product_name.replace(' ', '+').replace('&', 'and')
            search_url = url_template.format(query=clean_query)
            
            # Get display name
            display_names = {
                'russian': {
                    'onliner': 'Onliner.by',
                    'deal': 'Deal.by',
                    'wildberries': 'Wildberries',
                    'ozon': 'Ozon',
                    'yandex_market': 'Яндекс.Маркет'
                },
                'english': {
                    'amazon': 'Amazon',
                    'wayfair': 'Wayfair',
                    'west_elm': 'West Elm',
                    'cb2': 'CB2',
                    'overstock': 'Overstock'
                }
            }
            
            display_name = display_names[language].get(engine_name, engine_name.title())
            
            links.append({
                'name': display_name,
                'url': search_url,
                'engine': engine_name
            })
        
        return links
    
    def format_product_response(self, product_query: Dict[str, any], links: List[Dict[str, str]], language: str) -> str:
        """
        Format product response with links.
        
        Args:
            product_query: Product query info
            links: List of search links
            language: Language
            
        Returns:
            Formatted response
        """
        if language == 'russian':
            response = f"""Вот где можно найти {product_query['product_name']}:

Поисковые системы и магазины:"""
            
            for link in links:
                response += f"\n• {link['name']}: {link['url']}"
            
            response += """

Советы по поиску:
• Используйте точное название товара
• Добавьте бренд для более точных результатов
• Сравнивайте цены в разных магазинах
• Обращайте внимание на отзывы и рейтинги

Если нужна помощь с выбором конкретной модели или бренда, опишите подробнее что ищете."""
        else:
            response = f"""Here's where you can find {product_query['product_name']}:

Search engines and stores:"""
            
            for link in links:
                response += f"\n• {link['name']}: {link['url']}"
            
            response += """

Search tips:
• Use the exact product name
• Add brand for more accurate results
• Compare prices across different stores
• Pay attention to reviews and ratings

If you need help choosing a specific model or brand, describe in more detail what you're looking for."""
        
        return response
