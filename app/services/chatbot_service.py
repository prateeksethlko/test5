import json
import logging
from typing import List, Dict, Optional
from app.models.knowledge_base import KnowledgeBase, RepositoryAccess
from app.services.openai_service import OpenAIService
from app.utils.exceptions import ChatbotServiceError

logger = logging.getLogger(__name__)

class ChatbotService:
    """Service for managing chatbot interactions and business logic."""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.knowledge_base = KnowledgeBase()
        self.repository_access = RepositoryAccess()
        self.system_prompt = self._build_system_prompt()
        self.available_tools = self._build_tools()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI assistant."""
        available_keys = "\n".join([f"- '{key}'" for key in self.knowledge_base.get_all_keys()])
        available_repos = ", ".join(self.repository_access.get_all_repositories())
        
        return f"""You are a helpful and knowledgeable Virtual Assistant.
Your primary role is to help users understand tools like Yellowbrick, DB2, etc access requirements through natural, conversational interactions.

**Natural Conversation Guidelines:**
1. **Always respond naturally to greetings** - If a user says "Hi", "Hello", etc., respond with a friendly greeting first
2. **Then offer assistance** - After greeting, ask how you can help with Access management
3. **Follow structured flow only when needed** - Only use the structured questioning when the user indicates they need access information

**Structured Flow for Access Requests (use only when user needs access help):**
1. Ask if the user is a new user or existing user
2. If user is a new user, always first ask if UNIX is enabled before proceeding! If UNIX is not enabled, politely tell the user they must enable UNIX first by visiting the ServiceNow portal, and do NOT proceed with any access group help.
3. If they need access information, ask which type of repository (Development/QA/Production)
4. Ask them to be specific about repository ID (D1, D2, Q1, Q2, etc.)
5. Once you have the specific repository, provide the myAccess Groups for that repository

**Key Instructions:**
1. **Respond naturally to conversational inputs** - Don't force users into the structured flow immediately
2. **Use Available Tools:** Use the knowledge base and repository access tools to provide accurate information
3. **Be Specific:** Always ask for specific repository IDs rather than general categories when helping with access
4. **Professional but Friendly Tone:** Maintain a helpful, professional, and conversational demeanor
5. **D1,D2... means Development repositories, Q1,Q2... means QA repositories, P1,P2... means Production repositories.**

**Available Tools:**
- get_answer_from_knowledge_base(query_key: str): For general Informatica information
- get_repository_access_groups(repository_id: str): For specific repository access groups

Available knowledge base keys:
{available_keys}

Available repositories: {available_repos}
"""
    
    def _build_tools(self) -> List[Dict]:
        """Build tool definitions for OpenAI function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_answer_from_knowledge_base",
                    "description": "Retrieves answer from internal knowledge base for Informatica access queries",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query_key": {
                                "type": "string",
                                "description": f"Knowledge base key. Must be one of: {', '.join(self.knowledge_base.get_all_keys())}"
                            }
                        },
                        "required": ["query_key"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_repository_access_groups",
                    "description": "Retrieves the myAccess Groups for a specific repository ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "repository_id": {
                                "type": "string",
                                "description": f"Repository ID. Must be one of: {', '.join(self.repository_access.get_all_repositories())}"
                            }
                        },
                        "required": ["repository_id"]
                    }
                }
            }
        ]
    
    def process_chat(self, chat_history: List[Dict]) -> str:
        """Process chat interaction and return response."""
        try:
            unix_check_result = self._check_unix_prerequisite(chat_history)
            if unix_check_result:
                return unix_check_result
            
            messages = [{"role": "system", "content": self.system_prompt}] + chat_history
            
            response = self.openai_service.chat_completion(
                messages=messages, 
                tools=self.available_tools, 
                tool_choice="auto"
            )
            
            if response.get("tool_calls"):
                return self._handle_tool_calls(messages, response["tool_calls"])
            
            return response.get("content", "I couldn't generate a response. Please try again.")
            
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return "I am currently experiencing technical difficulties. Please try again later."
    
    def _check_unix_prerequisite(self, chat_history: List[Dict]) -> Optional[str]:
        """Check if new user has UNIX enabled."""
        is_new_user = False
        asked_unix = False
        unix_answer = None
        
        for message in chat_history:
            content = message.get("content", "").lower()
            role = message.get("role")
            
            if role == "user" and any(phrase in content for phrase in ["new user", "i am new", "i'm new"]):
                is_new_user = True
            
            if role == "assistant" and "unix enabled" in content:
                asked_unix = True
            
            if asked_unix and role == "user":
                if any(word in content for word in ["yes", "yep", "yeah", "i do", "enabled", "have unix"]):
                    unix_answer = "yes"
                elif any(word in content for word in ["no", "not", "don't have", "haven't", "without unix", "no unix"]):
                    unix_answer = "no"
        
        if is_new_user and not asked_unix:
            return "You're a new user. Do you have UNIX enabled on your account? (You must have UNIX enabled before proceeding with Informatica access provisioning.)"
        
        if asked_unix and unix_answer == "no":
            return ("You must first enable UNIX on your account before requesting Informatica access. "
                   "Please visit the ServiceNow portal and request UNIX enablement. "
                   "Once UNIX is enabled, you can return here and proceed with Informatica access.")
        
        return None
    
    def _handle_tool_calls(self, messages: List[Dict], tool_calls: List[Dict]) -> str:
        """Handle AI tool function calls."""
        messages.append({"role": "assistant", "tool_calls": tool_calls})
        
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            
            try:
                function_args = json.loads(tool_call["function"]["arguments"])
                
                if function_name == "get_answer_from_knowledge_base":
                    result = self._execute_knowledge_base_lookup(**function_args)
                elif function_name == "get_repository_access_groups":
                    result = self._execute_repository_lookup(**function_args)
                else:
                    result = {"status": "error", "message": f"Unknown function: {function_name}"}
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing tool arguments: {e}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps({"status": "error", "message": "Invalid arguments"})
                })
        
        final_response = self.openai_service.chat_completion(messages=messages)
        return final_response.get("content", "I encountered an issue generating a response.")
    
    def _execute_knowledge_base_lookup(self, query_key: str) -> Dict:
        """Execute knowledge base lookup."""
        logger.info(f"Knowledge base lookup: {query_key}")
        answer = self.knowledge_base.get_answer(query_key)
        if answer:
            return {"status": "success", "answer": answer}
        return {"status": "error", "message": f"Key '{query_key}' not found"}
    
    def _execute_repository_lookup(self, repository_id: str) -> Dict:
        """Execute repository access group lookup."""
        logger.info(f"Repository lookup: {repository_id}")
        groups = self.repository_access.get_access_groups(repository_id)
        if groups:
            formatted_groups = "\n".join([f"• {group}" for group in groups])
            return {
                "status": "success", 
                "answer": f"The myAccess Groups for repository {repository_id.upper()} are:\n{formatted_groups}"
            }
        return {"status": "error", "message": f"Repository '{repository_id}' not found"}
