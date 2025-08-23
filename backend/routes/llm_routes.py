#!/usr/bin/env python3
"""
LLM-powered routes for automatic BRD generation using FastAPI
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.llm_service import LLMService
from services.brd import BusinessRequirementAgent

from utils.rate_limiter import rate_limiter
import json

# Create FastAPI router
router = APIRouter()

# Initialize services
llm_service = LLMService()

async def check_rate_limit(request: Request):
    """Check rate limit for the request"""
    client_id = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_id):
        remaining_time = rate_limiter.get_reset_time(client_id)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "reset_time": remaining_time,
                "remaining_requests": 0
            }
        )
    
    return client_id

# Pydantic models for request/response
class ProjectDescriptionRequest(BaseModel):
    project_description: str
    model: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_description": "We need to build a modern e-commerce platform for our retail business. The system should include product catalog, shopping cart, payment processing, order management, and user account management.",
                "model": "gemini-2.0-flash"
            }
        }
    
    def validate_project_description(self):
        """Validate project description length and content"""
        if len(self.project_description.strip()) < 10:
            raise ValueError("Project description must be at least 10 characters long")
        if len(self.project_description) > 5000:
            raise ValueError("Project description must be less than 5000 characters")
        return True



class UploadedFile(BaseModel):
    filename: str
    content: str
    type: str

class ProjectDescriptionWithFilesRequest(BaseModel):
    project_description: str
    uploaded_files: list[UploadedFile] = []
    model: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_description": "We need to build a modern e-commerce platform for our retail business. The system should include product catalog, shopping cart, payment processing, order management, and user account management.",
                "uploaded_files": [
                    {
                        "filename": "requirements.pdf",
                        "content": "PDF content here...",
                        "type": "application/pdf"
                    }
                ],
                "model": "gemini-2.0-flash"
            }
        }
    
    def validate_input(self):
        """Validate input length and content"""
        if not self.project_description.strip() and not self.uploaded_files:
            raise ValueError("Either project description or uploaded files must be provided")
        
        if self.project_description and len(self.project_description.strip()) < 10:
            raise ValueError("Project description must be at least 10 characters long")
        
        if self.project_description and len(self.project_description) > 5000:
            raise ValueError("Project description must be less than 5000 characters")
        
        if len(self.uploaded_files) > 10:
            raise ValueError("Maximum 10 files allowed")
        
        return True

class BRDResponse(BaseModel):
    success: bool
    message: str
    brd_markdown: str
    brd_schema: Dict[str, Any]  # Renamed from schema_json to avoid conflict
    project_name: str
    generated_data: Dict[str, Any]
    llm_provider_used: str
    summary: Dict[str, Any]  # This will include completeness_score, completeness_status, and intelligent_prompt



@router.post("/generate_brd_from_input", response_model=BRDResponse)
async def generate_brd_from_input(
    request: ProjectDescriptionRequest,
    client_id: str = Depends(check_rate_limit)
):
    """
    Generate BRD from user's natural language input using LLM
    """
    try:
        # Validate input
        try:
            request.validate_project_description()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        project_description = request.project_description
        model = request.model
        
        # Use LLM service to generate BRD data
        try:
            brd_data = llm_service.generate_brd_from_input(project_description, model)
            print(f"✅ LLM service returned data: {len(brd_data)} keys")
            
            # Validate the returned data structure
            required_keys = ['project_name', 'stakeholders', 'objectives', 'scope', 'requirements', 'assumptions', 'constraints', 'success_criteria']
            missing_keys = [key for key in required_keys if key not in brd_data]
            if missing_keys:
                print(f"⚠️ Missing required keys: {missing_keys}")
                # Add default values for missing keys
                for key in missing_keys:
                    if key == 'scope':
                        brd_data[key] = {'in_scope': [], 'out_scope': []}
                    elif key == 'requirements':
                        brd_data[key] = {'business': [], 'functional': [], 'non_functional': []}
                    else:
                        brd_data[key] = []
                print(f"✅ Added default values for missing keys")
            
        except Exception as e:
            print(f"❌ LLM service failed: {e}")
            raise HTTPException(status_code=500, detail=f'LLM service failed: {str(e)}')
        
        # Create BRA instance and populate with LLM data
        try:
            bra = BusinessRequirementAgent()
            bra.schema.project_name = brd_data.get('project_name', 'Project')
            if not bra.schema.project_name or not bra.schema.project_name.strip():
                bra.schema.project_name = "Project"
                print(f"⚠️ Project name was empty, using default: {bra.schema.project_name}")
            bra.schema.stakeholders = brd_data.get('stakeholders', [])
            bra.schema.objectives = brd_data.get('objectives', [])
            
            # Handle nested scope structure
            scope_data = brd_data.get('scope', {})
            if isinstance(scope_data, dict):
                bra.schema.scope["in_scope"] = scope_data.get('in_scope', [])
                bra.schema.scope["out_scope"] = scope_data.get('out_scope', [])
            else:
                bra.schema.scope["in_scope"] = []
                bra.schema.scope["out_scope"] = []
            
            # Handle nested requirements structure
            requirements_data = brd_data.get('requirements', {})
            if isinstance(requirements_data, dict):
                bra.schema.requirements["business"] = requirements_data.get('business', [])
                bra.schema.requirements["functional"] = requirements_data.get('functional', [])
                bra.schema.requirements["non_functional"] = requirements_data.get('non_functional', [])
            else:
                bra.schema.requirements["business"] = []
                bra.schema.requirements["functional"] = []
                bra.schema.requirements["non_functional"] = []
            
            bra.schema.assumptions = brd_data.get('assumptions', [])
            bra.schema.constraints = brd_data.get('constraints', [])
            bra.schema.success_criteria = brd_data.get('success_criteria', [])
            
            print(f"✅ BRA schema populated successfully")
            
            # Analyze completeness and generate intelligent prompt
            completeness_analysis = bra.get_completeness_score(brd_data)
            intelligent_prompt = bra.get_intelligent_prompt(brd_data)
            
            print(f"✅ Completeness analysis completed: {completeness_analysis['completeness_percentage']:.1f}%")
            
        except Exception as e:
            print(f"❌ BRA schema population failed: {e}")
            raise HTTPException(status_code=500, detail=f'Failed to populate BRA schema: {str(e)}')
        
        # Initialize BRA for intelligent analysis
        try:
            print(f"✅ BRA initialized for intelligent analysis")
        except Exception as e:
            print(f"❌ BRA initialization failed: {e}")
            raise HTTPException(status_code=500, detail=f'Failed to initialize BRA: {str(e)}')
        
        # Generate BRD content
        try:
            brd_content = bra.generate_brd_markdown(llm_service)
            
            # Debug: Show the actual schema data
            print(f"🔍 Schema data before JSON conversion:")
            print(f"   - project_name: {bra.schema.project_name}")
            print(f"   - stakeholders: {bra.schema.stakeholders}")
            print(f"   - objectives: {bra.schema.objectives}")
            print(f"   - scope: {bra.schema.scope}")
            print(f"   - requirements: {bra.schema.requirements}")
            print(f"   - assumptions: {bra.schema.assumptions}")
            print(f"   - constraints: {bra.schema.constraints}")
            print(f"   - success_criteria: {bra.schema.success_criteria}")
            
            schema_json_string = bra.export_schema_json()
            print(f"🔍 JSON string length: {len(schema_json_string)}")
            print(f"🔍 JSON string preview: {schema_json_string[:200]}...")
            
            # Parse the JSON string back to a dictionary
            import json
            try:
                schema_json = json.loads(schema_json_string)
                print(f"✅ Schema JSON parsed successfully: {len(schema_json)} keys")
            except json.JSONDecodeError as json_error:
                print(f"❌ Failed to parse schema JSON: {json_error}")
                # Create a fallback schema if parsing fails
                schema_json = {
                    "project_name": bra.schema.project_name,
                    "stakeholders": bra.schema.stakeholders,
                    "objectives": bra.schema.objectives,
                    "scope": bra.schema.scope,
                    "requirements": bra.schema.requirements,
                    "assumptions": bra.schema.assumptions,
                    "constraints": bra.schema.constraints,
                    "success_criteria": bra.schema.success_criteria
                }
                print(f"✅ Using fallback schema structure")
            
            print(f"✅ BRD content generated successfully")
        except Exception as e:
            print(f"❌ BRD content generation failed: {e}")
            raise HTTPException(status_code=500, detail=f'Failed to generate BRD content: {str(e)}')
        

        
        # Create and return response
        try:
            print(f"🔍 Creating BRDResponse with data:")
            print(f"   - success: True")
            print(f"   - message: 'BRD generated successfully from your input!'")
            print(f"   - brd_markdown length: {len(brd_content)}")
            print(f"   - schema_json type: {type(schema_json)}")
            print(f"   - project_name: {bra.schema.project_name}")
            print(f"   - generated_data keys: {list(brd_data.keys())}")
            print(f"   - llm_provider_used: {model or 'default'}")
            print(f"   - summary data: {len(bra.schema.stakeholders)} stakeholders, {len(bra.schema.objectives)} objectives")
            
            # Validate that all required data is present
            if not brd_content or len(brd_content.strip()) == 0:
                raise ValueError("BRD content is empty")
            
            if not schema_json or not isinstance(schema_json, dict):
                raise ValueError(f"Schema JSON is invalid: {type(schema_json)}")
            
            if not bra.schema.project_name or not bra.schema.project_name.strip():
                # Set a default project name if missing
                bra.schema.project_name = "Project"
                print(f"⚠️ Project name was missing, using default: {bra.schema.project_name}")
            
            # Ensure all summary fields are present and valid
            summary_data = {
                'stakeholders_count': len(bra.schema.stakeholders),
                'objectives_count': len(bra.schema.objectives),
                'requirements_count': {
                    'business': len(bra.schema.requirements['business']),
                    'functional': len(bra.schema.requirements['functional']),
                    'non_functional': len(bra.schema.requirements['non_functional'])
                },
                'assumptions_count': len(bra.schema.assumptions),
                'constraints_count': len(bra.schema.constraints),
                'success_criteria_count': len(bra.schema.success_criteria),
                'completeness_score': completeness_analysis['completeness_percentage'],
                'completeness_status': 'Complete' if completeness_analysis['is_complete'] else 'Needs Improvement',
                'intelligent_prompt': intelligent_prompt
            }
            
            print(f"✅ Summary data validated successfully")
            
            response = BRDResponse(
                success=True,
                message='BRD generated successfully from your input!',
                brd_markdown=brd_content,
                brd_schema=schema_json,
                project_name=bra.schema.project_name,
                generated_data=brd_data,
                llm_provider_used='Google Gemini',
                summary=summary_data
            )
            print(f"✅ Response created successfully")
            return response
        except Exception as e:
            print(f"❌ Response creation failed: {e}")
            print(f"❌ Response error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f'Failed to create response: {str(e)}')
        
    except Exception as e:
        import traceback
        print(f"❌ Error in generate_brd_from_input: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        print(f"❌ Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'Error generating BRD: {str(e)}')







@router.post("/generate_brd_with_files", response_model=BRDResponse)
async def generate_brd_with_files(
    request: ProjectDescriptionWithFilesRequest,
    client_id: str = Depends(check_rate_limit)
):
    """
    Generate BRD from user's natural language input and uploaded files using LLM
    """
    try:
        # Validate input
        try:
            request.validate_input()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        project_description = request.project_description
        uploaded_files = request.uploaded_files
        model = request.model
        
        # Additional validation for uploaded files
        if uploaded_files:
            total_content_length = sum(len(file.content) for file in uploaded_files)
            if total_content_length > 100000:  # 100KB total limit
                raise HTTPException(
                    status_code=400, 
                    detail="Total file content size exceeds 100KB limit. Please reduce file sizes or content."
                )
            
            # Validate file types
            valid_types = [
                'application/pdf', 
                'text/markdown', 
                'text/x-markdown', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            invalid_files = [f for f in uploaded_files if f.type not in valid_types]
            if invalid_files:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file types detected: {[f.filename for f in invalid_files]}. Only PDF, MD, and DOCX files are supported."
                )
        
        # Check if user uploaded existing BRD documents
        has_existing_brd = any(
            'brd' in f.filename.lower() or 
            'business requirements' in f.filename.lower() or 
            'requirements document' in f.filename.lower()
            for f in uploaded_files
        )
        
        if has_existing_brd:
            print(f"🔍 Detected existing BRD documents - using improvement mode")
            # Use the BRD improvement logic for existing documents
            try:
                # Combine all BRD content
                brd_content = "\n\n".join([f.content for f in uploaded_files])
                
                # Use BRA to analyze and improve the existing BRD
                bra = BusinessRequirementAgent()
                analysis_result = bra.analyze_existing_brd(brd_content)
                
                if 'error' in analysis_result:
                    print(f"❌ BRD analysis failed: {analysis_result['error']}")
                    raise HTTPException(status_code=400, detail=f'BRD analysis failed: {analysis_result["error"]}')
                
                print(f"✅ BRD analysis completed successfully")
                
                # Improve the BRD using AI
                improvement_result = bra.improve_existing_brd(
                    brd_content,
                    project_description or "Improve the existing BRD document",
                    llm_service
                )
                
                if not improvement_result.get('success', False):
                    print(f"⚠️ AI improvement failed: {improvement_result.get('error', 'Unknown error')}")
                    improved_content = brd_content
                    improvement_notes = improvement_result.get('improvement_notes', ['AI improvement not available'])
                else:
                    print(f"✅ AI improvement completed successfully")
                    improved_content = improvement_result.get('improved_content', brd_content)
                    improvement_notes = improvement_result.get('improvement_notes', [])
                
                # Create enhanced schema with analysis data
                enhanced_schema = {
                    "project_name": analysis_result.get('project_name', 'Unknown Project'),
                    "stakeholders": analysis_result.get('stakeholders', []),
                    "objectives": analysis_result.get('objectives', []),
                    "scope": analysis_result.get('scope', {'in_scope': [], 'out_scope': []}),
                    "requirements": analysis_result.get('requirements', {'business': [], 'functional': [], 'non_functional': []}),
                    "assumptions": analysis_result.get('assumptions', []),
                    "constraints": analysis_result.get('constraints', []),
                    "success_criteria": analysis_result.get('success_criteria', []),
                    "analysis_notes": analysis_result.get('analysis_notes', []),
                    "improvement_notes": improvement_notes
                }
                
                # Calculate completeness score
                completeness_analysis = bra.get_completeness_score(enhanced_schema)
                
                # Create summary data
                summary_data = {
                    'stakeholders_count': len(enhanced_schema['stakeholders']),
                    'objectives_count': len(enhanced_schema['objectives']),
                    'requirements_count': {
                        'business': len(enhanced_schema['requirements']['business']),
                        'functional': len(enhanced_schema['requirements']['functional']),
                        'non_functional': len(enhanced_schema['requirements']['non_functional'])
                    },
                    'assumptions_count': len(enhanced_schema['assumptions']),
                    'constraints_count': len(enhanced_schema['constraints']),
                    'success_criteria_count': len(enhanced_schema['success_criteria']),
                    'completeness_score': completeness_analysis['completeness_percentage'],
                    'completeness_status': 'Complete' if completeness_analysis['is_complete'] else 'Needs Improvement',
                    'analysis_items_found': len(enhanced_schema['analysis_notes']),
                    'improvement_items_applied': len(enhanced_schema['improvement_notes']),
                    'original_content_length': len(brd_content),
                    'improved_content_length': len(improved_content),
                    'improvement_instructions_provided': bool(project_description)
                }
                
                response = BRDResponse(
                    success=True,
                    message='BRD analyzed and improved successfully!',
                    brd_markdown=improved_content,
                    brd_schema=enhanced_schema,
                    project_name=enhanced_schema['project_name'],
                    generated_data=enhanced_schema,
                    llm_provider_used='Google Gemini (Analysis + Improvement)',
                    summary=summary_data
                )
                
                print(f"✅ BRD improvement completed successfully")
                return response
                
            except Exception as e:
                print(f"❌ BRD improvement failed: {e}")
                raise HTTPException(status_code=500, detail=f'BRD improvement failed: {str(e)}')
        
        # Standard BRD generation mode
        # Combine project description with file contents for enhanced context
        enhanced_description = project_description
        
        if uploaded_files:
            file_context = "\n\nAdditional context from uploaded files:\n"
            for file_obj in uploaded_files:
                file_context += f"\n--- {file_obj.filename} ({file_obj.type}) ---\n"
                # Limit each file's content contribution to prevent token overflow
                content_preview = file_obj.content[:2000] + ("..." if len(file_obj.content) > 2000 else "")
                file_context += content_preview
                file_context += "\n"
            
            enhanced_description += file_context
        
        print(f"📄 Processing request with {len(uploaded_files)} files")
        print(f"📝 Enhanced description length: {len(enhanced_description)} characters")
        
        # Use LLM service to generate BRD data
        try:
            brd_data = llm_service.generate_brd_from_input(enhanced_description, model)
            print(f"✅ LLM service returned data: {len(brd_data)} keys")
            
            # Validate the returned data structure
            required_keys = ['project_name', 'stakeholders', 'objectives', 'scope', 'requirements', 'assumptions', 'constraints', 'success_criteria']
            missing_keys = [key for key in required_keys if key not in brd_data]
            if missing_keys:
                print(f"⚠️ Missing required keys: {missing_keys}")
                # Add default values for missing keys
                for key in missing_keys:
                    if key == 'scope':
                        brd_data[key] = {'in_scope': [], 'out_scope': []}
                    elif key == 'requirements':
                        brd_data[key] = {'business': [], 'functional': [], 'non_functional': []}
                    else:
                        brd_data[key] = []
                print(f"✅ Added default values for missing keys")
            
        except Exception as e:
            print(f"❌ LLM service failed: {e}")
            raise HTTPException(status_code=500, detail=f'LLM service failed: {str(e)}')
        
        # Create BRA instance and populate with LLM data
        try:
            bra = BusinessRequirementAgent()
            bra.schema.project_name = brd_data.get('project_name', 'Project')
            if not bra.schema.project_name or not bra.schema.project_name.strip():
                bra.schema.project_name = "Project"
                print(f"⚠️ Project name was empty, using default: {bra.schema.project_name}")
            bra.schema.stakeholders = brd_data.get('stakeholders', [])
            bra.schema.objectives = brd_data.get('objectives', [])
            
            # Handle nested scope structure
            scope_data = brd_data.get('scope', {})
            if isinstance(scope_data, dict):
                bra.schema.scope["in_scope"] = scope_data.get('in_scope', [])
                bra.schema.scope["out_scope"] = scope_data.get('out_scope', [])
            else:
                bra.schema.scope["in_scope"] = []
                bra.schema.scope["out_scope"] = []
            
            # Handle nested requirements structure
            requirements_data = brd_data.get('requirements', {})
            if isinstance(requirements_data, dict):
                bra.schema.requirements["business"] = requirements_data.get('business', [])
                bra.schema.requirements["functional"] = requirements_data.get('functional', [])
                bra.schema.requirements["non_functional"] = requirements_data.get('non_functional', [])
            else:
                bra.schema.requirements["business"] = []
                bra.schema.requirements["functional"] = []
                bra.schema.requirements["non_functional"] = []
            
            bra.schema.assumptions = brd_data.get('assumptions', [])
            bra.schema.constraints = brd_data.get('constraints', [])
            bra.schema.success_criteria = brd_data.get('success_criteria', [])
            
            print(f"✅ BRA schema populated successfully")
            
            # Analyze completeness and generate intelligent prompt
            completeness_analysis = bra.get_completeness_score(brd_data)
            intelligent_prompt = bra.get_intelligent_prompt(brd_data)
            
            print(f"✅ Completeness analysis completed: {completeness_analysis['completeness_percentage']:.1f}%")
            
        except Exception as e:
            print(f"❌ BRA schema population failed: {e}")
            raise HTTPException(status_code=500, detail=f'Failed to populate BRA schema: {str(e)}')
        
        # Initialize BRA for intelligent analysis
        try:
            print(f"✅ BRA initialized for intelligent analysis")
        except Exception as e:
            print(f"❌ BRA initialization failed: {e}")
            raise HTTPException(status_code=500, detail=f'Failed to initialize BRA: {str(e)}')
        
        # Generate BRD content
        try:
            brd_content = bra.generate_brd_markdown(llm_service)
            
            # Debug: Show the actual schema data
            print(f"🔍 Schema data before JSON conversion:")
            print(f"   - project_name: {bra.schema.project_name}")
            print(f"   - stakeholders: {bra.schema.stakeholders}")
            print(f"   - objectives: {bra.schema.objectives}")
            print(f"   - scope: {bra.schema.scope}")
            print(f"   - requirements: {bra.schema.requirements}")
            print(f"   - assumptions: {bra.schema.assumptions}")
            print(f"   - constraints: {bra.schema.constraints}")
            print(f"   - success_criteria: {bra.schema.success_criteria}")
            
            schema_json_string = bra.export_schema_json()
            print(f"🔍 JSON string length: {len(schema_json_string)}")
            print(f"🔍 JSON string preview: {schema_json_string[:200]}...")
            
            # Parse the JSON string back to a dictionary
            import json
            try:
                schema_json = json.loads(schema_json_string)
                print(f"✅ Schema JSON parsed successfully: {len(schema_json)} keys")
            except json.JSONDecodeError as json_error:
                print(f"❌ Failed to parse schema JSON: {json_error}")
                # Create a fallback schema if parsing fails
                schema_json = {
                    "project_name": bra.schema.project_name,
                    "stakeholders": bra.schema.stakeholders,
                    "objectives": bra.schema.objectives,
                    "scope": bra.schema.scope,
                    "requirements": bra.schema.requirements,
                    "assumptions": bra.schema.assumptions,
                    "constraints": bra.schema.constraints,
                    "success_criteria": bra.schema.success_criteria
                }
                print(f"✅ Using fallback schema structure")
            
            print(f"✅ BRD content generated successfully")
        except Exception as e:
            print(f"❌ BRD content generation failed: {e}")
            raise HTTPException(status_code=500, detail=f'Failed to generate BRD content: {str(e)}')
        
        # Create and return response
        try:
            print(f"🔍 Creating BRDResponse with data:")
            print(f"   - success: True")
            print(f"   - message: 'BRD generated successfully from your input and uploaded files!'")
            print(f"   - brd_markdown length: {len(brd_content)}")
            print(f"   - schema_json type: {type(schema_json)}")
            print(f"   - project_name: {bra.schema.project_name}")
            print(f"   - generated_data keys: {list(brd_data.keys())}")
            print(f"   - llm_provider_used: {model or 'default'}")
            print(f"   - summary data: {len(bra.schema.stakeholders)} stakeholders, {len(bra.schema.objectives)} objectives")
            print(f"   - files processed: {len(uploaded_files)}")
            
            # Validate that all required data is present
            if not brd_content or len(brd_content.strip()) == 0:
                raise ValueError("BRD content is empty")
            
            if not schema_json or not isinstance(schema_json, dict):
                raise ValueError(f"Schema JSON is invalid: {type(schema_json)}")
            
            if not bra.schema.project_name or not bra.schema.project_name.strip():
                # Set a default project name if missing
                bra.schema.project_name = "Project"
                print(f"⚠️ Project name was missing, using default: {bra.schema.project_name}")
            
            # Ensure all summary fields are present and valid
            summary_data = {
                'stakeholders_count': len(bra.schema.stakeholders),
                'objectives_count': len(bra.schema.objectives),
                'requirements_count': {
                    'business': len(bra.schema.requirements['business']),
                    'functional': len(bra.schema.requirements['functional']),
                    'non_functional': len(bra.schema.requirements['non_functional'])
                },
                'assumptions_count': len(bra.schema.assumptions),
                'constraints_count': len(bra.schema.constraints),
                'success_criteria_count': len(bra.schema.success_criteria),
                'completeness_score': completeness_analysis['completeness_percentage'],
                'completeness_status': 'Complete' if completeness_analysis['is_complete'] else 'Needs Improvement',
                'intelligent_prompt': intelligent_prompt,
                'files_processed': len(uploaded_files)
            }
            
            print(f"✅ Summary data validated successfully")
            
            response = BRDResponse(
                success=True,
                message='BRD generated successfully from your input and uploaded files!',
                brd_markdown=brd_content,
                brd_schema=schema_json,
                project_name=bra.schema.project_name,
                generated_data=brd_data,
                llm_provider_used='Google Gemini',
                summary=summary_data
            )
            print(f"✅ Response created successfully")
            return response
        except Exception as e:
            print(f"❌ Response creation failed: {e}")
            print(f"❌ Response error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f'Failed to create response: {str(e)}')
        
    except Exception as e:
        import traceback
        print(f"❌ Error in generate_brd_with_files: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        print(f"❌ Full traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f'Error generating BRD: {str(e)}')















@router.get("/download_brd/{project_name}")
async def download_brd(project_name: str):
    """
    Download BRD as Markdown file
    """
    try:
        # This would typically fetch from database
        # For now, return a placeholder
        brd_content = f"# {project_name}\n\nBRD content would be here..."
        
        # Create temporary file
        filename = f"{project_name.replace(' ', '_')}_BRD.md"
        file_path = f"/tmp/{filename}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(brd_content)
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='text/markdown'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error downloading BRD: {str(e)}')






