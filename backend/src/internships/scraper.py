"""
Advanced internship search and scraping module.
Handles detailed extraction, filtering, and analysis of Internshala internships.
"""

import asyncio
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
import re
import uuid
from urllib.parse import urljoin
from selenium.webdriver.common.by import By

from src.browser.manager_selenium import BrowserManager
from src.models import InternshipSummary, InternshipMode
from src.utils.logging import get_logger
from src.utils.date_parser import parse_stipend_amount, parse_relative_date
from src.config import config


class InternshipSearchFilter:
    """Advanced filtering options for internship search."""
    
    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        min_stipend: Optional[int] = None,
        max_stipend: Optional[int] = None,
        duration_weeks: Optional[int] = None,
        work_mode: Optional[InternshipMode] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None,
        company_types: Optional[List[str]] = None,  # startup, mnc, etc.
        categories: Optional[List[str]] = None,  # engineering, marketing, etc.
        part_time_allowed: Optional[bool] = None,
        with_job_offer: Optional[bool] = None,
        exclude_unpaid: bool = False
    ):
        self.keywords = keywords or []
        self.locations = locations or []
        self.min_stipend = min_stipend
        self.max_stipend = max_stipend
        self.duration_weeks = duration_weeks
        self.work_mode = work_mode
        self.start_date_from = start_date_from
        self.start_date_to = start_date_to
        self.company_types = company_types or []
        self.categories = categories or []
        self.part_time_allowed = part_time_allowed
        self.with_job_offer = with_job_offer
        self.exclude_unpaid = exclude_unpaid


class InternshipDetailExtractor:
    """Extracts detailed information from internship pages."""
    
    def __init__(self, browser_manager: BrowserManager, trace_id: Optional[str] = None):
        self.browser = browser_manager
        self.logger = get_logger(__name__, trace_id)
    
    async def extract_detailed_internship(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract comprehensive internship details from the internship page."""
        self.logger.info(f"Extracting detailed internship from: {url}")
        
        try:
            await self.browser.internshala_bot.browser.navigate_to(url)
            
            # Wait for page to load
            if not await self.browser.internshala_bot.browser.wait_for_selector(
                ".internship_details, .detail_view, .internship-detail", timeout=15
            ):
                self.logger.warning(f"Internship detail page not loaded: {url}")
                return None
            
            details = {}
            
            # Basic information
            details.update(await self._extract_basic_info())
            
            # Requirements and skills
            details.update(await self._extract_requirements())
            
            # Application details
            details.update(await self._extract_application_info())
            
            # Company information
            details.update(await self._extract_company_info())
            
            # Additional metadata
            details['scraped_at'] = datetime.now().isoformat()
            details['source_url'] = url
            
            return details
            
        except Exception as e:
            self.logger.error(f"Failed to extract detailed internship from {url}: {e}")
            return None
    
    async def _extract_basic_info(self) -> Dict[str, Any]:
        """Extract basic internship information."""
        info = {}
        
        try:
            # Title
            title_selectors = [
                ".profile_name", 
                ".internship_profile", 
                ".internship-title",
                "h1.heading_4_5"
            ]
            for selector in title_selectors:
                title = await self.browser.internshala_bot.browser.get_text_content(selector)
                if title:
                    info['title'] = title.strip()
                    break
            
            # Company
            company_selectors = [
                ".company_name",
                ".link_display_like_text",
                ".company-name"
            ]
            for selector in company_selectors:
                company = await self.browser.internshala_bot.browser.get_text_content(selector)
                if company:
                    info['company'] = company.strip()
                    break
            
            # Location
            location_selectors = [
                ".location_name",
                ".internship_location",
                ".location-info"
            ]
            for selector in location_selectors:
                location = await self.browser.internshala_bot.browser.get_text_content(selector)
                if location:
                    info['location'] = location.strip()
                    break
            
            # Duration
            duration_selectors = [
                ".duration_container",
                ".internship_duration",
                ".duration-info"
            ]
            for selector in duration_selectors:
                duration = await self.browser.internshala_bot.browser.get_text_content(selector)
                if duration:
                    info['duration'] = duration.strip()
                    break
            
            # Stipend
            stipend_selectors = [
                ".stipend_container",
                ".internship_stipend", 
                ".stipend-info"
            ]
            for selector in stipend_selectors:
                stipend = await self.browser.internshala_bot.browser.get_text_content(selector)
                if stipend:
                    info['stipend'] = stipend.strip()
                    break
            
            # Start date
            start_date_selectors = [
                ".start_date_container",
                ".internship_start_date",
                ".start-date-info"
            ]
            for selector in start_date_selectors:
                start_date = await self.browser.internshala_bot.browser.get_text_content(selector)
                if start_date:
                    info['start_date'] = start_date.strip()
                    break
            
            # Apply by date
            apply_by_selectors = [
                ".apply_by_container",
                ".internship_apply_by",
                ".apply-by-info"
            ]
            for selector in apply_by_selectors:
                apply_by = await self.browser.internshala_bot.browser.get_text_content(selector)
                if apply_by:
                    info['apply_by'] = apply_by.strip()
                    break
            
        except Exception as e:
            self.logger.warning(f"Failed to extract basic info: {e}")
        
        return info
    
    async def _extract_requirements(self) -> Dict[str, Any]:
        """Extract requirements and skills."""
        requirements = {}
        
        try:
            # Skills required
            skills_selectors = [
                ".skills_required",
                ".internship_skills",
                ".skills-section"
            ]
            for selector in skills_selectors:
                skills = await self.browser.internshala_bot.browser.get_text_content(selector)
                if skills:
                    requirements['skills_required'] = skills.strip()
                    break
            
            # Who can apply
            eligibility_selectors = [
                ".who_can_apply",
                ".eligibility_criteria",
                ".eligibility-section"
            ]
            for selector in eligibility_selectors:
                eligibility = await self.browser.internshala_bot.browser.get_text_content(selector)
                if eligibility:
                    requirements['eligibility'] = eligibility.strip()
                    break
            
            # Number of openings
            openings_selectors = [
                ".number_of_internships",
                ".openings_count",
                ".openings-info"
            ]
            for selector in openings_selectors:
                openings = await self.browser.internshala_bot.browser.get_text_content(selector)
                if openings:
                    requirements['openings'] = openings.strip()
                    break
            
            # Perks
            perks_selectors = [
                ".perks_container",
                ".internship_perks",
                ".perks-section"
            ]
            for selector in perks_selectors:
                perks = await self.browser.internshala_bot.browser.get_text_content(selector)
                if perks:
                    requirements['perks'] = perks.strip()
                    break
            
        except Exception as e:
            self.logger.warning(f"Failed to extract requirements: {e}")
        
        return requirements
    
    async def _extract_application_info(self) -> Dict[str, Any]:
        """Extract application-related information."""
        app_info = {}
        
        try:
            # Application deadline
            deadline_selectors = [
                ".application_deadline",
                ".apply_by",
                ".deadline-info"
            ]
            for selector in deadline_selectors:
                deadline = await self.browser.internshala_bot.browser.get_text_content(selector)
                if deadline:
                    app_info['application_deadline'] = deadline.strip()
                    break
            
            # Number of applicants
            applicants_selectors = [
                ".applicants_count",
                ".total_applicants",
                ".applicants-info"
            ]
            for selector in applicants_selectors:
                applicants = await self.browser.internshala_bot.browser.get_text_content(selector)
                if applicants:
                    app_info['total_applicants'] = applicants.strip()
                    break
            
            # Activity/views
            activity_selectors = [
                ".activity_container",
                ".internship_activity",
                ".activity-info"
            ]
            for selector in activity_selectors:
                activity = await self.browser.internshala_bot.browser.get_text_content(selector)
                if activity:
                    app_info['activity'] = activity.strip()
                    break
            
        except Exception as e:
            self.logger.warning(f"Failed to extract application info: {e}")
        
        return app_info
    
    async def _extract_company_info(self) -> Dict[str, Any]:
        """Extract company-related information."""
        company_info = {}
        
        try:
            # Company description
            desc_selectors = [
                ".company_description",
                ".about_company",
                ".company-about"
            ]
            for selector in desc_selectors:
                description = await self.browser.internshala_bot.browser.get_text_content(selector)
                if description:
                    company_info['company_description'] = description.strip()
                    break
            
            # Company size
            size_selectors = [
                ".company_size",
                ".team_size",
                ".company-size"
            ]
            for selector in size_selectors:
                size = await self.browser.internshala_bot.browser.get_text_content(selector)
                if size:
                    company_info['company_size'] = size.strip()
                    break
            
            # Company type
            type_selectors = [
                ".company_type",
                ".organization_type",
                ".company-type"
            ]
            for selector in type_selectors:
                comp_type = await self.browser.internshala_bot.browser.get_text_content(selector)
                if comp_type:
                    company_info['company_type'] = comp_type.strip()
                    break
            
        except Exception as e:
            self.logger.warning(f"Failed to extract company info: {e}")
        
        return company_info


class InternshipScraper:
    """Advanced internship scraper with filtering and detailed extraction."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.logger = get_logger(__name__, trace_id)
        self.browser_manager = BrowserManager(trace_id)
        self.detail_extractor = InternshipDetailExtractor(self.browser_manager, trace_id)
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.browser_manager.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.browser_manager.close()
    
    async def search_internships(
        self,
        search_filter: InternshipSearchFilter,
        limit: int = 100,
        extract_details: bool = False
    ) -> List[Dict[str, Any]]:
        """Search for internships with advanced filtering."""
        self.logger.info(f"Starting internship search with limit: {limit}")
        
        try:
            # Check authentication
            if not await self.browser_manager.check_authentication():
                self.logger.warning("User not authenticated - some features may be limited")
            
            # Build search URL
            search_url = self._build_search_url(search_filter)
            self.logger.info(f"Search URL: {search_url}")
            
            # Navigate to search page
            await self.browser_manager.internshala_bot.browser.navigate_to(search_url)
            
            # Wait for results to load
            if not await self.browser_manager.internshala_bot.browser.wait_for_selector(
                ".internship_meta, .individual_internship", timeout=15
            ):
                self.logger.warning("Search results not loaded")
                return []
            
            # Extract internship listings
            internships = await self._extract_internship_listings(limit)
            
            # Apply additional filters
            filtered_internships = self._apply_advanced_filters(internships, search_filter)
            
            # Extract detailed information if requested
            if extract_details:
                detailed_internships = []
                for internship in filtered_internships[:20]:  # Limit detailed extraction
                    if 'url' in internship:
                        details = await self.detail_extractor.extract_detailed_internship(internship['url'])
                        if details:
                            internship.update(details)
                    detailed_internships.append(internship)
                return detailed_internships
            
            return filtered_internships
            
        except Exception as e:
            self.logger.error(f"Failed to search internships: {e}")
            return []
    
    def _build_search_url(self, search_filter: InternshipSearchFilter) -> str:
        """Build search URL with filters."""
        base_url = "https://internshala.com/internships"
        params = []
        
        # Keywords
        if search_filter.keywords:
            keywords = "+".join(search_filter.keywords)
            params.append(f"keyword={keywords}")
        
        # Locations
        if search_filter.locations:
            locations = ",".join(search_filter.locations)
            params.append(f"location={locations}")
        
        # Work mode
        if search_filter.work_mode:
            if search_filter.work_mode == InternshipMode.REMOTE:
                params.append("type=work_from_home")
            elif search_filter.work_mode == InternshipMode.ON_SITE:
                params.append("type=in_office")
        
        # Categories
        if search_filter.categories:
            categories = ",".join(search_filter.categories)
            params.append(f"category={categories}")
        
        # Company types
        if search_filter.company_types:
            company_types = ",".join(search_filter.company_types)
            params.append(f"company_type={company_types}")
        
        # Duration
        if search_filter.duration_weeks:
            params.append(f"duration={search_filter.duration_weeks}")
        
        # Part time
        if search_filter.part_time_allowed is not None:
            if search_filter.part_time_allowed:
                params.append("part_time=1")
        
        # Job offer
        if search_filter.with_job_offer is not None:
            if search_filter.with_job_offer:
                params.append("job_offer=1")
        
        # Exclude unpaid
        if search_filter.exclude_unpaid:
            params.append("stipend_type=paid")
        
        if params:
            return f"{base_url}?" + "&".join(params)
        
        return base_url
    
    async def _extract_internship_listings(self, limit: int) -> List[Dict[str, Any]]:
        """Extract internship listings from search results."""
        internships = []
        
        try:
            # Scroll to load more results
            await self.browser_manager.internshala_bot.browser.scroll_to_bottom(pause_time=2)
            
            # Find internship elements
            internship_selectors = [
                ".internship_meta",
                ".individual_internship",
                ".internship-item"
            ]
            
            internship_elements = []
            for selector in internship_selectors:
                elements = self.browser_manager.internshala_bot.browser.driver.find_elements(
                    By.CSS_SELECTOR,
                    selector
                )
                if elements:
                    internship_elements = elements
                    self.logger.info(f"Found {len(elements)} internships using selector: {selector}")
                    break
            
            if not internship_elements:
                self.logger.warning("No internship elements found")
                return []
            
            for element in internship_elements[:limit]:
                try:
                    internship_data = await self._extract_single_internship(element)
                    if internship_data:
                        internships.append(internship_data)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to extract internship: {e}")
                    continue
            
            self.logger.info(f"Extracted {len(internships)} internship listings")
            return internships
            
        except Exception as e:
            self.logger.error(f"Failed to extract internship listings: {e}")
            return []
    
    async def _extract_single_internship(self, element) -> Optional[Dict[str, Any]]:
        """Extract data from a single internship element."""
        try:
            data = {}
            
            # Title
            title_selectors = [
                ".internship_summary_title",
                ".profile a",
                ".internship-title"
            ]
            for selector in title_selectors:
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, selector)
                    data['title'] = title_elem.text.strip()
                    # Get URL from title link
                    if title_elem.tag_name == 'a':
                        data['url'] = title_elem.get_attribute('href')
                    break
                except:
                    continue
            
            # Company
            company_selectors = [
                ".company_name",
                ".company a",
                ".company-name"
            ]
            for selector in company_selectors:
                try:
                    company_elem = element.find_element(By.CSS_SELECTOR, selector)
                    data['company'] = company_elem.text.strip()
                    break
                except:
                    continue
            
            # Location
            location_selectors = [
                ".location_name",
                ".location",
                ".internship-location"
            ]
            for selector in location_selectors:
                try:
                    location_elem = element.find_element(By.CSS_SELECTOR, selector)
                    data['location'] = location_elem.text.strip()
                    break
                except:
                    continue
            
            # Stipend
            stipend_selectors = [
                ".stipend",
                ".internship_stipend",
                ".stipend-amount"
            ]
            for selector in stipend_selectors:
                try:
                    stipend_elem = element.find_element(By.CSS_SELECTOR, selector)
                    data['stipend'] = stipend_elem.text.strip()
                    break
                except:
                    continue
            
            # Duration
            duration_selectors = [
                ".duration",
                ".internship_duration",
                ".duration-info"
            ]
            for selector in duration_selectors:
                try:
                    duration_elem = element.find_element(By.CSS_SELECTOR, selector)
                    data['duration'] = duration_elem.text.strip()
                    break
                except:
                    continue
            
            # Apply by
            apply_by_selectors = [
                ".apply_by",
                ".deadline",
                ".apply-deadline"
            ]
            for selector in apply_by_selectors:
                try:
                    apply_elem = element.find_element(By.CSS_SELECTOR, selector)
                    data['apply_by'] = apply_elem.text.strip()
                    break
                except:
                    continue
            
            # Posted date
            posted_selectors = [
                ".posted",
                ".post_date",
                ".posted-date"
            ]
            for selector in posted_selectors:
                try:
                    posted_elem = element.find_element(By.CSS_SELECTOR, selector)
                    data['posted_date'] = posted_elem.text.strip()
                    break
                except:
                    continue
            
            # Add metadata
            data['id'] = str(uuid.uuid4())
            data['platform'] = "internshala"
            data['scraped_at'] = datetime.now().isoformat()
            
            return data if data.get('title') else None
            
        except Exception as e:
            self.logger.warning(f"Failed to extract single internship: {e}")
            return None
    
    def _apply_advanced_filters(
        self, 
        internships: List[Dict[str, Any]], 
        search_filter: InternshipSearchFilter
    ) -> List[Dict[str, Any]]:
        """Apply advanced filtering to internship results."""
        filtered = []
        
        for internship in internships:
            try:
                # Skip if no basic data
                if not internship.get('title'):
                    continue
                
                # Stipend filtering
                if search_filter.min_stipend or search_filter.max_stipend:
                    stipend_text = internship.get('stipend', '')
                    stipend_min, stipend_max = parse_stipend_amount(stipend_text)
                    
                    if search_filter.exclude_unpaid and stipend_min is None:
                        continue
                    
                    if search_filter.min_stipend and stipend_min:
                        if stipend_min < search_filter.min_stipend:
                            continue
                    
                    if search_filter.max_stipend and stipend_max:
                        if stipend_max > search_filter.max_stipend:
                            continue
                
                # Keyword filtering (additional to URL params)
                if search_filter.keywords:
                    title_lower = internship.get('title', '').lower()
                    company_lower = internship.get('company', '').lower()
                    
                    found_keyword = False
                    for keyword in search_filter.keywords:
                        if keyword.lower() in title_lower or keyword.lower() in company_lower:
                            found_keyword = True
                            break
                    
                    if not found_keyword:
                        continue
                
                # Location filtering (additional to URL params)
                if search_filter.locations:
                    location = internship.get('location', '').lower()
                    found_location = False
                    
                    for loc in search_filter.locations:
                        if loc.lower() in location:
                            found_location = True
                            break
                    
                    if not found_location:
                        continue
                
                filtered.append(internship)
                
            except Exception as e:
                self.logger.warning(f"Filter error for internship: {e}")
                continue
        
        self.logger.info(f"Applied advanced filters: {len(internships)} -> {len(filtered)} internships")
        return filtered
    
    async def export_to_csv(
        self, 
        internships: List[Dict[str, Any]], 
        filename: Optional[str] = None
    ) -> str:
        """Export internships to CSV file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"internshala_internships_{timestamp}.csv"
        
        # Ensure exports directory exists
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        file_path = exports_dir / filename
        
        try:
            if not internships:
                self.logger.warning("No internships to export")
                return str(file_path)
            
            # Get all possible fields
            all_fields = set()
            for internship in internships:
                all_fields.update(internship.keys())
            
            # Define field order
            priority_fields = [
                'id', 'title', 'company', 'location', 'stipend', 'duration',
                'apply_by', 'posted_date', 'url', 'skills_required', 'eligibility',
                'openings', 'perks', 'company_description', 'scraped_at'
            ]
            
            # Organize fields
            fieldnames = []
            for field in priority_fields:
                if field in all_fields:
                    fieldnames.append(field)
            
            # Add remaining fields
            for field in sorted(all_fields):
                if field not in fieldnames:
                    fieldnames.append(field)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for internship in internships:
                    # Ensure all fields are present
                    row = {field: internship.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            self.logger.info(f"Exported {len(internships)} internships to {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export internships to CSV: {e}")
            raise
