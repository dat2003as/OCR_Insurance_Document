"""
Prompt Templates and Factory for Gemini Extraction
"""
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class PagePrompt:
    """Prompt configuration for each page"""
    page_number: int
    title: str
    prompt: str
    json_structure: Dict[str, Any]


class PromptFactory:
    """Factory pattern for page prompts"""
    
    _prompts = {
        1: {
            "title": "Policy & Personal Information",
            "prompt": """Bạn là chuyên gia trích xuất dữ liệu. Phân tích hình ảnh Biểu mẫu Yêu cầu Bồi thường này (Trang 1). 

Trích xuất tất cả các giá trị điền vào cho các trường sau:
- Policy No.
- Name of Policyowner/Employee/Member
- Name of Insured
- Occupation
- HKID/Passport No.
- Date of Birth (format: DD/MM/YYYY)
- Sex (Male/Female)
- Benefits to Claim (các ô được đánh dấu)

Trả lời chỉ bằng JSON với cấu trúc sau:
{
  "policy_details": {
    "policy_no": "...",
    "policyowner_name": "..."
  },
  "insured_info": {
    "name": "...",
    "occupation": "...",
    "id_passport": "...",
    "date_of_birth": "DD/MM/YYYY",
    "sex": "Male/Female"
  },
  "benefits_to_claim": ["benefit1", "benefit2", ...]
}

Chú ý đến chữ viết tay và các ô được đánh dấu. Chỉ trả về JSON.""",
            "json_structure": {
                "policy_details": {},
                "insured_info": {},
                "benefits_to_claim": []
            }
        },
        2: {
            "title": "Payment Instructions",
            "prompt": """Phân tích hình ảnh Trang 2 (Payment Instructions). 

Trích xuất các trường được điền trong phần 'Direct Credit':
- Name of account holder
- Bank Name
- Bank No., Branch No., Bank Account No.
- Phương thức thanh toán (e-Payout/Cheque)

Trả lời chỉ bằng JSON:
{
  "payment_instructions": {
    "payment_method": "e-Payout/Cheque",
    "account_holder_name": "...",
    "bank_name": "...",
    "bank_code": "...",
    "branch_code": "...",
    "account_number": "..."
  }
}

Đọc kỹ chữ viết tay. Chỉ trả về JSON.""",
            "json_structure": {"payment_instructions": {}}
        },
        3: {
            "title": "Declaration & Authorization",
            "prompt": """Phân tích hình ảnh Trang 3 (Declaration and Authorization). 

Trích xuất:
- Name (In BLOCK LETTERS)
- Date (DD/MM/YYYY)
- Có chữ ký hay không

Trả lời chỉ bằng JSON:
{
  "declaration": {
    "signatory_name": "...",
    "signature_date": "DD/MM/YYYY",
    "has_signature": true/false
  }
}

Chỉ trả về JSON.""",
            "json_structure": {"declaration": {}}
        },
        4: {
            "title": "Physician Report",
            "prompt": """Phân tích hình ảnh Trang 4 (PART II - Physician Section). 

Đọc chính xác chữ viết tay của bác sĩ. Trích xuất:
- Patient Name
- Date of Admission/Discharge
- Final Diagnosis
- Operation procedures
- Mode of Anaesthesia
- Doctor's signature date
- Doctor name
- Hospital/Clinic name

Trả lời chỉ bằng JSON:
{
  "physician_report": {
    "patient_name": "...",
    "admission_date": "DD/MM/YYYY",
    "discharge_date": "DD/MM/YYYY",
    "final_diagnosis": "...",
    "operation_procedures": [],
    "mode_of_anaesthesia": "...",
    "doctor_signature_date": "DD/MM/YYYY",
    "doctor_name": "...",
    "hospital_clinic_name": "..."
  }
}

Đọc kỹ chữ viết tay và thuật ngữ y tế. Chỉ trả về JSON.""",
            "json_structure": {"physician_report": {}}
        }
    }
    
    @classmethod
    def get_page_prompt(cls, page_number: int) -> PagePrompt:
        """Get prompt configuration for specific page"""
        config = cls._prompts.get(page_number, cls._prompts[4])
        return PagePrompt(
            page_number=page_number,
            title=config["title"],
            prompt=config["prompt"],
            json_structure=config["json_structure"]
        )
    
    @classmethod
    def get_all_prompts(cls) -> Dict[int, PagePrompt]:
        """Get all prompt configurations"""
        return {
            page_num: cls.get_page_prompt(page_num)
            for page_num in cls._prompts.keys()
        }


# Constants for prompt management
PAGE_TITLES = {
    1: "🟢 Thông tin Cá nhân và Chính sách",
    2: "🔵 Hướng dẫn Thanh toán",
    3: "🟡 Tuyên bố và Chữ ký",
    4: "🔴 Báo cáo Y tế"
}