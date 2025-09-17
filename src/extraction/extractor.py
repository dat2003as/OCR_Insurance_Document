import google.generativeai as genai
from src.settings import APP_SETTINGS
import logging
logger = logging.getLogger(__name__)
class DataExtractor:
    def __init__(self, ocr_results):
        self.extracted_text = ocr_results.get("extracted_text", "")

    def extract_medical_claim_info(self):
        """Enhanced extraction for medical insurance claim forms"""
        try:
            genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract information from this medical insurance claim form. Look for both English and Chinese text.
            
            Extract the following information:
            1. Patient/Insured Name (被保險人姓名)
            2. Policy Number/Certificate Number (保單號碼)
            3. HKID/Passport Number (身份證號碼)
            4. Date of Birth (出生日期)
            5. Treatment/Admission Date (治療/入院日期)
            6. Discharge Date (出院日期)
            7. Hospital/Clinic Name (醫院/診所名稱)
            8. Doctor/Physician Name (醫生姓名)
            9. Diagnosis/Medical Condition (診斷/病情)
            10. Treatment Details (治療詳情)
            11. Claim Amount (索償金額)
            12. Bank Account Details (銀行帳戶詳情)
            
            Text:
            {self.extracted_text}
            
            Return the information in JSON format. If any information is not found, use empty string.
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            # Try to parse JSON
            import json
            try:
                # Clean the response if it contains markdown formatting
                if result.startswith('```json'):
                    result = result.replace('```json', '').replace('```', '')
                elif result.startswith('```'):
                    result = result.replace('```', '')
                
                parsed_result = json.loads(result)
                return parsed_result
            except json.JSONDecodeError:
                # If JSON parsing fails, return structured data
                return {
                    "patient_name": self.extract_patient_name(),
                    "policy_number": self.extract_policy_number(),
                    "hkid_passport": self.extract_hkid_passport(),
                    "date_of_birth": self.extract_date_of_birth(),
                    "treatment_date": self.extract_treatment_date(),
                    "discharge_date": self.extract_discharge_date(),
                    "hospital_name": self.extract_hospital_name(),
                    "doctor_name": self.extract_doctor_name(),
                    "diagnosis": self.extract_diagnosis(),
                    "treatment_details": self.extract_treatment_details(),
                    "claim_amount": self.extract_claim_amount(),
                    "bank_details": self.extract_bank_details(),
                    "extraction_method": "fallback_individual"
                }
                
        except Exception as e:
            logger.error(f"Error in medical claim extraction: {str(e)}")
            return {"error": str(e)}

    def extract_patient_name(self):
        """Extract patient/insured name"""
        try:
            genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract the patient or insured person's name from this medical form.
            Look for fields like:
            - Name of Insured/被保險人姓名
            - Patient Name/病人姓名
            - Name of Policyowner/保單持有人姓名
            
            Text: {self.extracted_text}
            
            Return only the name or "Not found".
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            return result if result != "Not found" else ""
            
        except Exception as e:
            logger.error(f"Error extracting patient name: {str(e)}")
            return ""

    def extract_policy_number(self):
        """Extract policy/certificate number"""
        try:
            genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract the policy number, certificate number, or claim sequence number.
            Look for patterns like:
            - Policy No./Cert No.
            - Certificate Number
            - Claim Sequence
            - 保單號碼
            
            Text: {self.extracted_text}
            
            Return only the number or "Not found".
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            return result if result != "Not found" else ""
            
        except Exception as e:
            logger.error(f"Error extracting policy number: {str(e)}")
            return ""

    def extract_hkid_passport(self):
        """Extract HKID or Passport number"""
        try:
            genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract HKID or Passport number from the form.
            Look for:
            - HKID/Passport No.
            - 身份證號碼
            - ID number patterns like A1234567(9)
            
            Text: {self.extracted_text}
            
            Return only the ID number or "Not found".
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            return result if result != "Not found" else ""
            
        except Exception as e:
            logger.error(f"Error extracting HKID/Passport: {str(e)}")
            return ""

    def extract_treatment_date(self):
        """Extract treatment or admission date"""
        try:
            genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract treatment date, admission date, or date of service.
            Look for:
            - Treatment Date/治療日期
            - Date of Admission/入院日期
            - Consultation date
            - Any dates in DD/MM/YYYY format
            
            Text: {self.extracted_text}
            
            Return the date in DD/MM/YYYY format or "Not found".
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            return result if result != "Not found" else ""
            
        except Exception as e:
            logger.error(f"Error extracting treatment date: {str(e)}")
            return ""

    def extract_hospital_name(self):
        """Extract hospital or clinic name"""
        try:
            genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract the hospital, clinic, or medical facility name.
            Look for hospital names in both English and Chinese.
            
            Text: {self.extracted_text}
            
            Return only the hospital/clinic name or "Not found".
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            return result if result != "Not found" else ""
            
        except Exception as e:
            logger.error(f"Error extracting hospital name: {str(e)}")
            return ""

    def extract_diagnosis(self):
        """Extract medical diagnosis or condition"""
        try:
            genai.configure(api_key=APP_SETTINGS.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract the medical diagnosis, symptoms, or medical condition described in the form.
            Look for medical terms, condition names, symptoms mentioned.
            
            Text: {self.extracted_text}
            
            Return the diagnosis/condition or "Not found".
            """
            
            response = model.generate_content(prompt)
            result = response.text.strip()
            return result if result != "Not found" else ""
            
        except Exception as e:
            logger.error(f"Error extracting diagnosis: {str(e)}")
            return ""

    def extract_all_enhanced(self):
        """Main method to extract all medical claim information"""
        return self.extract_medical_claim_info()