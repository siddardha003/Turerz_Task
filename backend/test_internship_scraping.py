"""
Test the advanced internship scraping functionality.
This tests the scraping logic and filters.
"""

import asyncio
from datetime import datetime

from src.internships.scraper import InternshipScraper, InternshipSearchFilter
from src.models import InternshipMode
from src.utils.logging import get_logger


async def test_internship_scraping():
    """Test internship scraping without requiring login."""
    logger = get_logger(__name__)
    
    logger.info("🧪 Testing Advanced Internship Scraping")
    
    try:
        # Test 1: Basic search
        logger.info("Test 1: Basic Python internship search")
        
        search_filter = InternshipSearchFilter(
            keywords=["python"],
            min_stipend=5000,
            exclude_unpaid=True
        )
        
        async with InternshipScraper() as scraper:
            internships = await scraper.search_internships(
                search_filter=search_filter,
                limit=5,
                extract_details=False
            )
            
            logger.info(f"✅ Found {len(internships)} Python internships")
            
            if internships:
                # Display sample results
                for i, internship in enumerate(internships[:3], 1):
                    logger.info(f"  {i}. {internship.get('title', 'N/A')} at {internship.get('company', 'N/A')}")
                    logger.info(f"     Stipend: {internship.get('stipend', 'N/A')}")
                    logger.info(f"     Location: {internship.get('location', 'N/A')}")
            
            # Test CSV export
            if internships:
                csv_file = await scraper.export_to_csv(internships, "test_python_internships.csv")
                logger.info(f"✅ Exported to: {csv_file}")
        
        # Test 2: Advanced filtering
        logger.info("\nTest 2: Advanced filtering with multiple criteria")
        
        advanced_filter = InternshipSearchFilter(
            keywords=["data", "analytics"],
            locations=["Bangalore", "Mumbai"],
            min_stipend=10000,
            max_stipend=50000,
            work_mode=InternshipMode.REMOTE,
            exclude_unpaid=True
        )
        
        async with InternshipScraper() as scraper:
            advanced_internships = await scraper.search_internships(
                search_filter=advanced_filter,
                limit=3,
                extract_details=False
            )
            
            logger.info(f"✅ Advanced filter found {len(advanced_internships)} internships")
            
            if advanced_internships:
                for internship in advanced_internships:
                    logger.info(f"  • {internship.get('title', 'N/A')} - {internship.get('stipend', 'N/A')}")
        
        # Test 3: URL building
        logger.info("\nTest 3: Testing URL construction")
        
        test_scraper = InternshipScraper()
        test_filter = InternshipSearchFilter(
            keywords=["machine learning"],
            locations=["Remote"],
            categories=["Engineering"],
            exclude_unpaid=True
        )
        
        url = test_scraper._build_search_url(test_filter)
        logger.info(f"✅ Generated URL: {url}")
        
        logger.info("\n🎉 Internship scraping tests completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_internship_scraping())
