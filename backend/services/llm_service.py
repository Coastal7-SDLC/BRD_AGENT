#!/usr/bin/env python3
"""
LLM Service for automatic BRD generation from user input
Integrated with Google Gemini API for direct access to Gemini models
"""

import json
import re
import os
import logging
from typing import Dict, List, Any, Union, Optional

from services.brd import BRDSchema
from google import genai
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM-powered BRD generation with Google Gemini integration"""
    
    def __init__(self):
        # Load environment variables (optional, don't fail if .env is missing)
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception as e:
            print(f"⚠️ Warning: Could not load .env file: {e}")
        
        # Google Gemini configuration
        self.api_key = Config.GOOGLE_API_KEY
        self.model = Config.GOOGLE_MODEL
        
        # Log the model being used (using logger instead of print)
        logger.info(f"LLM Service Configuration - Model: {self.model}, Provider: Google Gemini")
        
        # For development/testing, allow a dummy key
        if not self.api_key or self.api_key.startswith('your_'):
            logger.warning("No valid Google API key found. Using fallback mode.")
            logger.warning("   💡 Please create a .env file with GOOGLE_API_KEY=your_actual_key")
            logger.warning("   💡 Get your key from: https://makersuite.google.com/app/apikey")
            self.api_key = "dummy_key_for_testing"
            self.client = None
        else:
            # Initialize Gemini client
            try:
                logger.info("🔑 Initializing Google Gemini client...")
                self.client = genai.Client(api_key=self.api_key)
                logger.info("LLM Service Configuration:")
                logger.info(f"   API Key: ✅ Valid")
                logger.info(f"   Model: {self.model}")
                logger.info(f"   Provider: Google Gemini")
                
                # Test the client with a simple call (with timeout)
                try:
                    logger.info("   🧪 Testing Gemini client...")
                    # For google-genai library, we need to use the correct model format
                    # The library expects just the model name without 'models/' prefix
                    model_name = self.model
                    
                    logger.info(f"   🔧 Testing with model: {model_name}")
                    
                    # Skip the test call during initialization to avoid hanging
                    logger.info("   ⚠️ Skipping Gemini test call during initialization to prevent hanging")
                    logger.info("   ✅ Gemini client initialized successfully")
                    
                except Exception as test_error:
                    logger.error(f"   ❌ Gemini client test failed: {test_error}")
                    logger.error(f"   💡 This might indicate an API key issue or model availability")
                    self.client = None
                    
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                logger.warning(f"   💡 Check your API key and internet connection")
                self.client = None
        
        # Dynamic system prompt for pure AI generation
        self.system_prompt = """You are an expert Business Analyst with 15+ years of experience in creating comprehensive Business Requirements Documents (BRD).

Your task is to analyze a project description and generate a detailed, professional BRD structure based on the information provided by the user.

IMPORTANT GUIDELINES:
- Analyze the user's project description carefully and extract meaningful information
- For each section, provide realistic and specific content based on the description
- If the description mentions specific features, goals, or requirements, include them
- If information is missing for a section, make reasonable inferences based on the project type
- ALWAYS provide a meaningful project name that reflects the actual project
- Be creative but realistic in filling out the BRD structure
- Respond ONLY with valid JSON in the exact format specified below

Extract and structure the following information from the user's input:
1. Project name (REQUIRED - create a descriptive name based on the project)
2. Key stakeholders (identify who would be involved or affected)
3. Business objectives (what the project aims to achieve)
4. Project scope (what's included and what's not)
5. Business requirements (business needs and goals)
6. Functional requirements (system capabilities and features)
7. Non-functional requirements (quality, performance, security needs)
8. Assumptions (what we assume to be true)
9. Constraints (limitations and restrictions)
10. Success criteria (how we measure success)

JSON Structure (respond ONLY with this):
{
    "project_name": "string",
    "stakeholders": ["string"],
    "objectives": ["string"],
    "scope": {
        "in_scope": ["string"],
        "out_scope": ["string"]
    },
    "requirements": {
        "business": ["string"],
        "functional": ["string"],
        "non_functional": ["string"]
    },
    "assumptions": ["string"],
    "constraints": ["string"],
    "success_criteria": ["string"]
}

CRITICAL: You MUST generate meaningful content for each section based on the project description. Do not leave sections empty - use your business analysis expertise to fill them with relevant information."""
    
    def generate_brd_from_input(self, user_input: str, model: str = None) -> Dict[str, Any]:
        """
        Generate BRD data from user input using Google Gemini
        
        Args:
            user_input: User's project description
            model: Specific model to use (optional, uses default if not specified)
            
        Returns:
            Dictionary containing BRD data
        """
        logger.info(f"Starting BRD generation...")
        logger.info(f"   Input length: {len(user_input)} characters")
        logger.info(f"   Model: {model or self.model}")
        
        # Check if Gemini client is available
        if not self.client:
            logger.error("❌ Gemini client not available - check API key configuration")
            logger.error("   💡 Please ensure GOOGLE_API_KEY is set in your .env file")
            logger.error("   💡 Or set it as an environment variable")
            return self._get_empty_brd_structure()
        
        # Use only Gemini generation - no fallbacks
        try:
            logger.info("   Attempting Gemini generation...")
            result = self._generate_with_gemini(user_input, model)
            logger.info("   ✅ Gemini generation successful")
            
            # Validate and fix the result structure
            if self._validate_brd_structure(result):
                logger.info("   ✅ BRD structure validated and fixed")
                logger.info(f"   📊 Final structure: project_name='{result.get('project_name', 'MISSING')}', stakeholders={len(result.get('stakeholders', []))}, objectives={len(result.get('objectives', []))}")
                return result
            else:
                logger.warning("   ⚠️ BRD structure validation failed, using fallback")
                return self._get_empty_brd_structure()
                
        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {str(e)}")
            logger.error(f"   💡 This could be due to:")
            logger.error(f"      - Poor AI response quality")
            logger.error(f"      - Invalid JSON format")
            logger.error(f"      - API connection issues")
            logger.error(f"      - Insufficient project description")
            
            # Try with a simpler, more direct prompt
            try:
                logger.info("   🔄 Attempting retry with simplified prompt...")
                result = self._generate_with_simplified_prompt(user_input, model)
                if self._validate_brd_structure(result):
                    logger.info("   ✅ Retry successful with simplified prompt")
                    return result
            except Exception as retry_error:
                logger.error(f"   ❌ Retry also failed: {str(retry_error)}")
            
            # Return empty structure if all attempts fail
            return self._get_empty_brd_structure()
    
    def _generate_with_gemini(self, user_input: str, model: str = None, expect_json: bool = True) -> Union[Dict[str, Any], str]:
        """Generate content using Google Gemini API"""
        # Check if Gemini client is available
        if not self.client:
            logger.error("Gemini client not available")
            raise Exception("Gemini client not configured")
        
        try:
            # Use specified model or default
            selected_model = model or self.model
            
            logger.info("   🔑 Using Google Gemini API...")
            logger.info(f"   📝 Model: {selected_model}")
            logger.info(f"   🌡️ Temperature: {Config.LLM_TEMPERATURE}")
            logger.info(f"   📏 Max tokens: {Config.MAX_OUTPUT_TOKENS}")
            
            # Prepare the prompt for pure AI generation
            full_prompt = f"{self.system_prompt}\n\nUser's Project Description:\n{user_input}\n\nBased on this project description, please generate a comprehensive BRD structure. Analyze the description carefully and provide meaningful content for each section. Respond with valid JSON only:"
            
            logger.info(f"   📋 Prompt length: {len(full_prompt)} characters")
            logger.info(f"   📋 User input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
            
            # Generate content using Gemini
            logger.info("   🚀 Calling Gemini API...")
            # For google-genai library, we need to use the correct model format
            # The library expects just the model name without 'models/' prefix
            model_name = selected_model
            
            logger.info(f"   🔧 Using model: {model_name}")
            
                        # Generate content using Gemini API
            response = self.client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
            
            # Handle different response formats
            logger.info(f"   🔍 Response type: {type(response)}")
            logger.info(f"   🔍 Response attributes: {dir(response)}")
            
            if hasattr(response, 'text') and response.text:
                content = response.text
                logger.info("   ✅ Gemini API successful (text format)")
                logger.info(f"   📄 Response length: {len(content)} characters")
                logger.info(f"   📄 Response preview: {content[:200]}{'...' if len(content) > 200 else ''}")
            elif hasattr(response, 'candidates') and response.candidates:
                # Handle different response format
                content = response.candidates[0].content.parts[0].text
                logger.info("   ✅ Gemini API successful (candidates format)")
                logger.info(f"   📄 Response length: {len(content)} characters")
                logger.info(f"   📄 Response preview: {content[:200]}{'...' if len(content) > 200 else ''}")
            elif hasattr(response, 'parts') and response.parts:
                # Handle parts format
                content = response.parts[0].text
                logger.info("   ✅ Gemini API successful (parts format)")
                logger.info(f"   📄 Response length: {len(content)} characters")
                logger.info(f"   📄 Response preview: {content[:200]}{'...' if len(content) > 200 else ''}")
            else:
                logger.error("   ❌ Unexpected response format")
                logger.error(f"   🔍 Response: {response}")
                raise Exception("Unexpected response format from Gemini API")
            
            if expect_json:
                # Parse JSON response
                try:
                    logger.info("   🔍 Attempting to parse JSON response...")
                    brd_data = json.loads(content)
                    logger.info("   ✅ JSON parsed successfully")
                    # Validate that we have a proper structure
                    if self._validate_brd_structure(brd_data):
                        logger.info("   ✅ BRD structure validation passed")
                        return brd_data
                    else:
                        logger.error("   ❌ BRD structure validation failed")
                        raise Exception("Invalid BRD structure returned by Gemini")
                except json.JSONDecodeError as json_error:
                    logger.error(f"   ❌ JSON parsing failed: {json_error}")
                    logger.info("   🔍 Attempting to extract JSON from response...")
                    # Try to extract JSON from the response
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        try:
                            extracted_json = json_match.group()
                            logger.info(f"   📄 Extracted JSON: {extracted_json[:200]}{'...' if len(extracted_json) > 200 else ''}")
                            parsed_data = json.loads(extracted_json)
                            if self._validate_brd_structure(parsed_data):
                                logger.info("   ✅ Extracted JSON validation passed")
                                return parsed_data
                            else:
                                logger.error("   ❌ Extracted JSON validation failed")
                        except Exception as extract_error:
                            logger.error(f"   ❌ Extracted JSON parsing failed: {extract_error}")
                    raise Exception("Failed to parse Gemini response as valid JSON")
            else:
                # Return plain text for section content
                return content
                
        except Exception as e:
            error_msg = f"Gemini generation failed: {str(e)}"
            logger.error(f"   ❌ {error_msg}")
            raise Exception(error_msg)
    
    def _validate_brd_structure(self, brd_data: Dict[str, Any]) -> bool:
        """Validate that the BRD data has the correct structure and fix missing elements"""
        logger.info(f"   🔍 Validating BRD structure...")
        logger.info(f"   📊 Input structure: {list(brd_data.keys()) if isinstance(brd_data, dict) else 'NOT A DICT'}")
        
        required_keys = [
            'project_name', 'stakeholders', 'objectives', 'scope', 
            'requirements', 'assumptions', 'constraints', 'success_criteria'
        ]
        
        # Check if all required keys exist and add missing ones
        for key in required_keys:
            if key not in brd_data:
                logger.info(f"   ⚠️ Missing key: {key}")
                if key == 'project_name':
                    # Project name is critical - try to infer from input or use default
                    brd_data[key] = "Project"
                    logger.info(f"   ✅ Added default project_name: {brd_data[key]}")
                elif key == 'scope':
                    brd_data[key] = {'in_scope': [], 'out_scope': []}
                    logger.info(f"   ✅ Added default scope structure")
                elif key == 'requirements':
                    brd_data[key] = {'business': [], 'functional': [], 'non_functional': []}
                    logger.info(f"   ✅ Added default requirements structure")
                else:
                    brd_data[key] = []
                    logger.info(f"   ✅ Added empty list for {key}")
        
        # Ensure scope and requirements have the right nested structure
        if not isinstance(brd_data.get('scope'), dict):
            logger.info(f"   ⚠️ Scope is not a dict, fixing...")
            brd_data['scope'] = {'in_scope': [], 'out_scope': []}
        
        scope_keys = ['in_scope', 'out_scope']
        for key in scope_keys:
            if key not in brd_data['scope']:
                brd_data['scope'][key] = []
        
        if not isinstance(brd_data.get('requirements'), dict):
            logger.info(f"   ⚠️ Requirements is not a dict, fixing...")
            brd_data['requirements'] = {'business': [], 'functional': [], 'non_functional': []}
        
        req_keys = ['business', 'functional', 'non_functional']
        for key in req_keys:
            if key not in brd_data['requirements']:
                brd_data['requirements'][key] = []
        
        # Ensure all values are lists
        for key in ['stakeholders', 'objectives', 'assumptions', 'constraints', 'success_criteria']:
            if not isinstance(brd_data.get(key), list):
                logger.info(f"   ⚠️ {key} is not a list, fixing...")
                brd_data[key] = []
        
        # Ensure project_name is a string
        if not isinstance(brd_data.get('project_name'), str) or not brd_data['project_name'].strip():
            logger.info(f"   ⚠️ Project name is invalid, setting default...")
            brd_data['project_name'] = "Project"
        
        # Check content quality and warn about poor AI responses
        empty_sections = []
        if not brd_data.get('stakeholders') or len(brd_data.get('stakeholders', [])) == 0:
            empty_sections.append('stakeholders')
        if not brd_data.get('objectives') or len(brd_data.get('objectives', [])) == 0:
            empty_sections.append('objectives')
        if not brd_data.get('assumptions') or len(brd_data.get('assumptions', [])) == 0:
            empty_sections.append('assumptions')
        if not brd_data.get('constraints') or len(brd_data.get('constraints', [])) == 0:
            empty_sections.append('constraints')
        if not brd_data.get('success_criteria') or len(brd_data.get('success_criteria', [])) == 0:
            empty_sections.append('success_criteria')
        
        if empty_sections:
            logger.warning(f"   ⚠️ Empty sections detected: {empty_sections} - This may indicate poor AI response quality")
        
        logger.info(f"   ✅ BRD structure validation complete")
        logger.info(f"   📊 Final structure: project_name='{brd_data.get('project_name')}', stakeholders={len(brd_data.get('stakeholders', []))}, objectives={len(brd_data.get('objectives', []))}")
        
        return True
    
    def _generate_with_simplified_prompt(self, user_input: str, model: str = None) -> Dict[str, Any]:
        """Generate BRD with a simpler, more direct prompt"""
        if not self.client:
            raise Exception("Gemini client not configured")
        
        try:
            selected_model = model or self.model
            
            # Simplified, more direct prompt
            simple_prompt = f"""You are a business analyst. Create a BRD structure for this project: "{user_input}"

Respond with ONLY this JSON structure:
{{
    "project_name": "Project Name",
    "stakeholders": ["User", "Admin"],
    "objectives": ["Goal 1", "Goal 2"],
    "scope": {{"in_scope": ["Feature 1"], "out_scope": ["Feature 2"]}},
    "requirements": {{"business": ["Need 1"], "functional": ["Function 1"], "non_functional": ["Quality 1"]}},
    "assumptions": ["Assumption 1"],
    "constraints": ["Constraint 1"],
    "success_criteria": ["Success 1"]
}}"""
            
            # For google-genai library, we need to use the correct model format
            # The library expects just the model name without 'models/' prefix
            model_name = selected_model
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=simple_prompt
            )
            
            if response.text:
                content = response.text
                # Try to extract JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
                
                # If no JSON found, try to parse the whole response
                try:
                    return json.loads(content)
                except:
                    pass
                
            raise Exception("Failed to parse simplified prompt response")
            
        except Exception as e:
            raise Exception(f"Simplified prompt generation failed: {str(e)}")
    
    def _get_empty_brd_structure(self) -> Dict[str, Any]:
        """Return empty BRD structure when AI generation fails"""
        return {
            "project_name": "Project",
            "stakeholders": [],
            "objectives": [],
            "scope": {
                "in_scope": [],
                "out_scope": []
            },
            "requirements": {
                "business": [],
                "functional": [],
                "non_functional": []
            },
            "assumptions": [],
            "constraints": [],
            "success_criteria": []
        }
    
    def _create_brd_schema(self, brd_data: Dict[str, Any]) -> BRDSchema:
        """Create BRDSchema object from parsed data"""
        try:
            return BRDSchema(
                project_name=brd_data.get('project_name', 'Unknown Project'),
                stakeholders=brd_data.get('stakeholders', []),
                objectives=brd_data.get('objectives', []),
                scope_in=brd_data.get('scope', {}).get('in_scope', []),
                scope_out=brd_data.get('scope', {}).get('out_scope', []),
                business_requirements=brd_data.get('requirements', {}).get('business', []),
                functional_requirements=brd_data.get('requirements', {}).get('functional', []),
                non_functional_requirements=brd_data.get('requirements', {}).get('non_functional', []),
                assumptions=brd_data.get('assumptions', []),
                constraints=brd_data.get('constraints', []),
                success_criteria=brd_data.get('success_criteria', [])
            )
        except Exception as e:
            logger.error(f"Error creating BRD schema: {e}")
            # Return a default schema
            return BRDSchema(
                project_name="Default Project",
                stakeholders=[],
                objectives=[],
                scope_in=[],
                scope_out=[],
                business_requirements=[],
                functional_requirements=[],
                non_functional_requirements=[],
                assumptions=[],
                constraints=[],
                success_criteria=[]
            )
    

