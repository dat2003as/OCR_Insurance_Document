"""
Data Validation Utilities
"""
import re
from typing import Dict, Any, List
from datetime import datetime


class DataValidator:
    """Validate and clean extracted data"""
    
    @staticmethod
    def validate_date(date_str: str, date_format: str = "%d/%m/%Y") -> bool:
        """
        Validate date format
        
        Args:
            date_str: Date string to validate
            date_format: Expected format (default: DD/MM/YYYY)
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_str, date_format)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_phone(phone_str: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return bool(re.match(pattern, str(phone_str)))
    
    @staticmethod
    def validate_email(email_str: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email_str)))
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep essential ones
        text = re.sub(r'[^\w\s\-\.\,\(\)\/]', '', text)
        return text.strip()
    
    @staticmethod
    def validate_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean all extracted data recursively
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            Cleaned and validated dictionary
        """
        validated = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Recursive validation for nested dicts
                validated[key] = DataValidator.validate_extracted_data(value)
            
            elif isinstance(value, str):
                # Clean and validate strings
                cleaned = DataValidator.clean_text(value)
                if cleaned:
                    validated[key] = cleaned
            
            elif isinstance(value, list):
                # Clean lists
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        cleaned = DataValidator.clean_text(item)
                        if cleaned:
                            cleaned_list.append(cleaned)
                    elif item:
                        cleaned_list.append(item)
                
                if cleaned_list:
                    validated[key] = cleaned_list
            
            elif value is not None:
                validated[key] = value
        
        return validated
    
    @staticmethod
    def validate_medical_form(merged_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate complete medical form data
        
        Returns:
            Dictionary of validation errors by section
        """
        errors = {
            "policy_details": [],
            "insured_info": [],
            "payment_instructions": [],
            "declaration": [],
            "physician_report": []
        }
        
        # Validate policy details
        policy = merged_data.get("policy_details", {})
        if not policy.get("policy_no"):
            errors["policy_details"].append("Policy number missing")
        
        # Validate insured info
        insured = merged_data.get("insured_info", {})
        if not insured.get("name"):
            errors["insured_info"].append("Insured name missing")
        
        dob = insured.get("date_of_birth")
        if dob and not DataValidator.validate_date(dob):
            errors["insured_info"].append("Invalid date of birth format")
        
        # Validate payment instructions
        payment = merged_data.get("payment_instructions", {})
        if not payment.get("payment_method"):
            errors["payment_instructions"].append("Payment method missing")
        
        # Validate declaration
        declaration = merged_data.get("declaration", {})
        if not declaration.get("signatory_name"):
            errors["declaration"].append("Signatory name missing")
        
        sig_date = declaration.get("signature_date")
        if sig_date and not DataValidator.validate_date(sig_date):
            errors["declaration"].append("Invalid signature date format")
        
        # Validate physician report
        physician = merged_data.get("physician_report", {})
        if not physician.get("final_diagnosis"):
            errors["physician_report"].append("Final diagnosis missing")
        
        # Remove empty error lists
        errors = {k: v for k, v in errors.items() if v}
        
        return errors