from typing import Dict, List, Optional

class KnowledgeBase:
    """Manages the internal knowledge base for Informatica access."""
    
    INTERNAL_KNOWLEDGE_BASE = {
        "typical_new_user_access": "For new Informatica users, typical access includes Informatica Server, YellowBrick, and DB2. To request this, you will need to provide your department/team and user ID through the Service Portal. Your department lead can confirm specific group names.",
        "request_production_access_policy": "Production (P1, P2) access to Informatica is typically read-only and requires explicit approval from your department lead and a change management ticket (CMT). Specific 'myAccess Groups' for production environments are highly restricted.",
        "development_qa_access": "Development (D1, D2) and QA (Q3, Q4) Informatica repositories generally have more flexible access. Access groups vary by project and team. Please specify the exact repository ID (e.g., D1 or Q3) when requesting access via the Service Portal.",
        "how_to_submit_access_request": "All Informatica access requests must be submitted through the IT Service Portal at https://your-service-portal.com/access-request. Please provide all necessary details, including your department, user ID, and the specific Informatica system/repository required. Attaching any chat transcripts can be helpful.",
        "db2_yellowbrick_access": "Access to DB2 and YellowBrick data warehouses is typically managed through specific 'myAccess Groups' linked to your project or department. New users are often provisioned default reader access, with write access requiring additional approval. Specify 'DB2' or 'YellowBrick' in your request.",
        "contact_human_support": "I apologize, but I am a virtual assistant and cannot directly perform actions like creating tickets or connecting you to a human agent. For those requests, please contact the IT Helpdesk directly at 1-800-555-HELP or submit a ticket via the IT Service Portal for a human agent.",
        "who_manages_informatica_access": "Informatica access is managed by the IT Access Management team, typically following predefined policies and requiring approvals from department leads or system owners.",
        "what_resources_available_informatica": "The Resources Available in Informatica include Data Integration, Data Quality, Data Governance, Master Data Management, and more. Specific resources can vary based on your Informatica setup.",
        "what_repositories_available_informatica": "The repositories available in Informatica include D1, D2, D3, Q1, Q2, Q3, T1, and others specific to different environments and projects."
    }
    
    @classmethod
    def get_answer(cls, query_key: str) -> Optional[str]:
        """Retrieve answer from knowledge base."""
        return cls.INTERNAL_KNOWLEDGE_BASE.get(query_key)
    
    @classmethod
    def get_all_keys(cls) -> List[str]:
        """Get all available knowledge base keys."""
        return list(cls.INTERNAL_KNOWLEDGE_BASE.keys())


class RepositoryAccess:
    """Manages repository access groups."""
    
    REPOSITORY_ACCESS_GROUPS = {
        "D1": ["ZNA_INFA_PC_D1_RWX", "D1_IPC_RS", "Autoserv_DV1"],
        "D2": ["ZNA_INFA_PC_D2_RWX", "D2_IPC_RS", "Autoserv_DV2"],
        "D3": ["ZNA_INFA_PC_D3_RWX", "D3_IPC_RS", "Autoserv_DV3"],
        "D4": ["ZNA_INFA_PC_D4_RWX", "D4_IPC_RS", "Autoserv_DV4"],
        "D5": ["ZNA_INFA_PC_D5_RWX", "D5_IPC_RS", "Autoserv_DV5"],
        "D6": ["ZNA_INFA_PC_D6_RWX", "D6_IPC_RS", "Autoserv_DV6"],
        "D7": ["ZNA_INFA_PC_D7_RWX", "D7_IPC_RS", "Autoserv_DV7"],
        "D8": ["ZNA_INFA_PC_D8_RWX", "D8_IPC_RS", "Autoserv_DV8"],
        "D9": ["ZNA_INFA_PC_D9_RWX", "D9_IPC_RS", "Autoserv_BDQ"],
        "Q1": ["ZNA_INFA_PC_Q1_RX", "Q1_IPC_RS", "Autoserv_QA1"],
        "Q2": ["ZNA_INFA_PC_Q2_RX", "Q2_IPC_RS", "Autoserv_QA2"],
        "Q3": ["informatica_qa3_read", "informatica_qa3_write", "db2_qa3_access", "yellowbrick_qa3_reader"],
        "Q4": ["informatica_qa4_read", "informatica_qa4_write", "db2_qa4_access", "yellowbrick_qa4_reader"],
        "T1": ["informatica_test_read", "informatica_test_write", "db2_test_access", "yellowbrick_test_reader"],
        "P1": ["informatica_prod1_read", "db2_prod1_read", "yellowbrick_prod1_read"],
        "P2": ["informatica_prod2_read", "db2_prod2_read", "yellowbrick_prod2_read"]
    }
    
    @classmethod
    def get_access_groups(cls, repository_id: str) -> Optional[List[str]]:
        """Get access groups for a specific repository."""
        return cls.REPOSITORY_ACCESS_GROUPS.get(repository_id.upper())
    
    @classmethod
    def get_all_repositories(cls) -> List[str]:
        """Get all available repository IDs."""
        return list(cls.REPOSITORY_ACCESS_GROUPS.keys())
