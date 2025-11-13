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
            "title": "Policy, Insured, Prior Treatment, Accident, and Condition Details",
            "prompt": """Bạn là chuyên gia trích xuất dữ liệu. Phân tích hình ảnh Biểu mẫu Yêu cầu Bồi thường này (Trang 1). 

Trích xuất **CHÍNH XÁC NỘI DUNG HIỂN THỊ** (bao gồm Hán tự, chữ cái, số) cho các trường sau:
1. Thông tin Hợp đồng và Người được bảo hiểm:
    - Policy No./Cert No. in Claim Sequence 
    - Name of Policyowner/Employee/Member (Đọc chính xác Hán tự)
    - Name of Insured (Đọc chính xác Hán tự)
    - Occupation (Đọc chính xác Hán tự)
    - HKID/Passport No. (Đọc chính xác ký tự cuối cùng trong ngoặc đơn)
    - Date of Birth (format: DD/MM/YYYY)
    - Sex (Male/Female)
    - Benefits to Claim (Trích xuất TẤT CẢ các loại quyền lợi có ô được đánh dấu, dù là dấu tích hay ký hiệu X)

2. Thông tin điều trị trước đó (Mục 4 - Chỉ trích xuất nếu được chọn là Yes):
    - Doctor's Name (Đọc chính xác chữ viết tay)
    - Address (Đọc chính xác địa chỉ được viết tay)
    - Treatment Date (DD/MM/YYYY)

3. Thông tin Tai nạn (Mục 5):
    - Was the hospitalization/surgery a result of an accident? (Yes/No)
    - Date, Time, Place, Brief Description (Nếu Yes)

4. Thông tin Trạng thái Yêu cầu (Mục 3 - Submitted to other company?):
    - Answer (Yes/No)
    - If Yes, Name of Insurance Company, Policy No., Type of claim

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
  "benefits_to_claim": ["benefit1", "benefit2", "..."],
  "prior_treatment_info": {
    "had_prior_treatment": true/false,
    "doctor_name": "...",
    "address": "...",
    "treatment_date": "DD/MM/YYYY"
  },
  "accident_info": {
    "is_result_of_accident": true/false,
    "date": "DD/MM/YYYY",
    "time": "...",
    "place": "...",
    "description": "..."
  },
  "other_claim_submission": {
    "submitted_to_other_company": true/false,
    "company_name": "...",
    "policy_no": "...",
    "claim_type": ["type1", "..."]
  }
}

Chỉ trả về JSON.""",
            "json_structure": {
                "policy_details": {},
                "insured_info": {},
                "benefits_to_claim": [],
                "prior_treatment_info": {},
                "accident_info": {},
                "other_claim_submission": {}
            }
        },
        2: {
            "title": "Payment Instructions",
            "prompt": """Phân tích hình ảnh Trang 2 (Payment Instructions). 

Trích xuất các trường được điền trong phần 'Direct Credit' hoặc 'Cheque', **ghi rõ từng phần số tài khoản**:
- Payment Method (Kiểm tra ô được đánh dấu, phải là e-Payout hoặc Cheque)
- Name of account holder (Chỉ trích xuất Ho TAI WAI)
- Bank Name (Chú ý Hán tự)
- Bank No. (Chỉ 3 số đầu của chuỗi 012000123456789)
- Branch No. (Chỉ 3 số tiếp theo, ví dụ: 000)
- Bank Account No. (Các số còn lại, ví dụ: 123456789)

Trả lời chỉ bằng JSON với cấu trúc sau:
{
  "payment_instructions": {
    "payment_method": "e-Payout/Cheque",
    "account_holder_name": "...",
    "bank_name": "...",
    "bank_no": "...",
    "branch_no": "...",
    "bank_account_no": "..."
  }
}

Chỉ trả về JSON.""",
            "json_structure": {"payment_instructions": {}}
        },
        3: {
            "title": "Declaration & Authorization",
            "prompt": """Phân tích hình ảnh Trang 3 (Declaration and Authorization). 

Trích xuất:
- Name (In BLOCK LETTERS)
- Date (DD/MM/YYYY)
- Has signature (true/false)

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
            "title": "PART II - Physician Report (Full Details)",
            "prompt": """Phân tích hình ảnh Trang 4 (PART II - Physician Section). 

Đọc chính xác chữ viết tay của bác sĩ và thuật ngữ y tế. Trích xuất tất cả các mục sau:
1. Thông tin Bệnh nhân & Ngày tháng:
    - Patient Name
    - Date of Admission (DD/MM/YYYY)
    - Date of Discharge (DD/MM/YYYY)
    - Level of hospital ward (Semi-private được đánh dấu)

2. Lịch sử Lâm sàng (Clinical History - 1):
    - Date patient first consulted you (DD/MM/YYYY)
    - Symptom duration (months/years)
    - Symptom(s)/complaint(s) relating to this hospitalization/treatment

3. Chi tiết Chẩn đoán và Phẫu thuật (Hospitalization Details - 2):
    - Final Diagnosis (Trích xuất các dòng chữ viết tay chính xác về chẩn đoán)
    - Operation procedure(s) performed (Liệt kê từng thủ thuật, chú ý chữ viết tay)
    - Mode of Anaesthesia (Chỉ trích xuất loại được đánh dấu: GA/LA/MAC/sedation - MAC được đánh dấu)
    - Can the medical test(s) and the operation procedure be done on an outpatient basis? (Yes/No)
    - If No, reason(s) (Chú ý: Severe Anaemia need intravenous iron therapy)
    - Any comorbidity? (Yes/No)
    - Is it a case of emergency? (Yes/No)

4. Ý kiến Chuyên môn (Professional Comment - 3):
    - Was the hospitalization a result of recurrent episode or chronic illness? (Yes/No)
    - Associated conditions (Trích xuất TẤT CẢ các ô được đánh dấu - N/A được đánh dấu)

5. Thông tin Bác sĩ:
    - Doctor's signature date (DD/MM/YYYY)
    - Name of attending physician/surgeon & qualifications
    - Address and Telephone No. (Nếu có)

Trả lời chỉ bằng JSON với cấu trúc sau:
{
  "physician_report": {
    "patient_name": "...",
    "admission_date": "DD/MM/YYYY",
    "discharge_date": "DD/MM/YYYY",
    "hospital_ward_level": "...",
    "clinical_history": {
      "first_consult_date": "DD/MM/YYYY",
      "symptom_duration": "...",
      "symptoms": "..."
    },
    "diagnosis_surgery": {
      "final_diagnosis": "...",
      "operation_procedures": ["...", "..."],
      "mode_of_anaesthesia": "...",
      "outpatient_possible": true/false,
      "outpatient_reason": "...",
      "comorbidity": true/false,
      "is_emergency": true/false
    },
    "professional_comment": {
      "is_recurrent_or_chronic": true/false,
      "associated_conditions": ["condition1", "..."]
    },
    "doctor_info": {
      "signature_date": "DD/MM/YYYY",
      "name_qualifications": "...",
      "address_tel": "..."
    }
  }
}

Chỉ trả về JSON.""",
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