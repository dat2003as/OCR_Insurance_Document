"""
Result Merger Utility
"""
from typing import Dict, Any, List


class ResultMerger:
    """Strategy pattern for merging extraction results"""
    
    @staticmethod
    def merge_results(page_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge results from all pages into a single JSON object
        
        Args:
            page_results: List of extraction results from each page
            
        Returns:
            Merged dictionary with all extracted data
        """
        merged = {
            "policy_details": {},
            "insured_info": {},
            "benefits_to_claim": [],
            "payment_instructions": {},
            "declaration": {},
            "physician_report": {}
        }
        
        for page_data in page_results:
            if not isinstance(page_data, dict):
                continue
            
            for key in merged.keys():
                if key in page_data:
                    if isinstance(merged[key], list):
                        # Merge lists (avoid duplicates)
                        merged[key].extend([
                            item for item in page_data[key] 
                            if item not in merged[key]
                        ])
                    elif isinstance(merged[key], dict):
                        # Merge dictionaries
                        merged[key].update(page_data[key])
        
        return merged
    
    @staticmethod
    def merge_with_priority(
        page_results: List[Dict[str, Any]], 
        priority_pages: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Merge results with priority for specific fields
        
        Args:
            page_results: List of extraction results
            priority_pages: Dict mapping field names to page numbers with priority
            
        Example:
            priority_pages = {"patient_name": 4}  # Page 4 has priority for patient_name
        """
        merged = ResultMerger.merge_results(page_results)
        
        # Apply priority rules
        for field, priority_page in priority_pages.items():
            if priority_page <= len(page_results):
                page_data = page_results[priority_page - 1]
                # Navigate nested dict to set priority value
                keys = field.split('.')
                target = merged
                for key in keys[:-1]:
                    target = target.get(key, {})
                if keys[-1] in page_data:
                    target[keys[-1]] = page_data[keys[-1]]
        
        return merged