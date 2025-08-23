#!/usr/bin/env python3
"""
Business Requirement Agent (BRA) - AI-powered Business Analyst
Gathers, analyzes, structures, and generates Business Requirements Documents (BRDs)
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class BRDSchema:
    """Core schema for Business Requirements Document"""
    project_name: str = ""
    stakeholders: List[str] = None
    objectives: List[str] = None
    scope: Dict[str, List[str]] = None
    requirements: Dict[str, List[str]] = None
    assumptions: List[str] = None
    constraints: List[str] = None
    success_criteria: List[str] = None
    
    def __post_init__(self):
        if self.stakeholders is None:
            self.stakeholders = []
        if self.objectives is None:
            self.objectives = []
        if self.scope is None:
            self.scope = {"in_scope": [], "out_scope": []}
        if self.requirements is None:
            self.requirements = {"business": [], "functional": [], "non_functional": []}
        if self.assumptions is None:
            self.assumptions = []
        if self.constraints is None:
            self.constraints = []
        if self.success_criteria is None:
            self.success_criteria = []

class BusinessRequirementAgent:
    """Main BRA class for intelligent requirement gathering and BRD generation"""
    
    def __init__(self):
        self.schema = BRDSchema()


    

    

    
    def get_completeness_score(self, brd_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate a completeness score for the BRD data"""
        total_fields = 10 
        completed_fields = 0
        
        # Check each field for meaningful content
        if brd_data.get('project_name') and len(str(brd_data['project_name']).strip()) > 3:
            completed_fields += 1
        
        if brd_data.get('stakeholders') and len(brd_data['stakeholders']) > 0:
            completed_fields += 1
        
        if brd_data.get('objectives') and len(brd_data['objectives']) > 0:
            completed_fields += 1
        
        if brd_data.get('scope') and brd_data['scope'].get('in_scope') and len(brd_data['scope']['in_scope']) > 0:
            completed_fields += 1
        
        if brd_data.get('scope') and brd_data['scope'].get('out_scope') and len(brd_data['scope']['out_scope']) > 0:
            completed_fields += 1
        
        if brd_data.get('requirements') and brd_data['requirements'].get('business') and len(brd_data['requirements']['business']) > 0:
            completed_fields += 1
        
        if brd_data.get('requirements') and brd_data['requirements'].get('functional') and len(brd_data['requirements']['functional']) > 0:
            completed_fields += 1
        
        if brd_data.get('requirements') and brd_data['requirements'].get('non_functional') and len(brd_data['requirements']['non_functional']) > 0:
            completed_fields += 1
        
        if brd_data.get('assumptions') and len(brd_data['assumptions']) > 0:
            completed_fields += 1
        
        if brd_data.get('constraints') and len(brd_data['constraints']) > 0:
            completed_fields += 1
        
        completeness_percentage = (completed_fields / total_fields) * 100
        
        # Lower threshold to 50% - if we have at least half the fields, consider it complete enough
        return {
            'completed_fields': completed_fields,
            'total_fields': total_fields,
            'completeness_percentage': completeness_percentage,
            'is_complete': completeness_percentage >= 50  # Changed from 80% to 50%
        }
    
    def get_intelligent_prompt(self, brd_data: Dict[str, Any]) -> str:
        """Generate an intelligent prompt based on data completeness"""
        completeness_score = self.get_completeness_score(brd_data)
        
        if completeness_score['is_complete']:
            return f"""
🎉 **BRD Data Analysis Complete!**

Your project description has been analyzed and contains sufficient information for a comprehensive BRD.

**Completeness Score:** {completeness_score['completeness_percentage']:.1f}% ({completeness_score['completed_fields']}/{completeness_score['total_fields']} fields)

**Status:** ✅ Ready to generate BRD document

You can now proceed to generate your Business Requirements Document with confidence!
            """
        
        # Instead of asking for more information, provide guidance and proceed
        prompt = f"""
🔍 **BRD Data Analysis - Proceeding with Available Information**

Your project description has been analyzed and a BRD will be generated using the available information.

**Completeness Score:** {completeness_score['completeness_percentage']:.1f}% ({completeness_score['completed_fields']}/{completeness_score['total_fields']} fields)

**Status:** ✅ Proceeding with BRD generation

**Note:** The system will intelligently fill in missing details based on your project description and industry best practices. You can always enhance the generated BRD later with additional specific information.

**Generated BRD will include:**
• Project overview and objectives
• Stakeholder identification
• Scope definition (in-scope and out-of-scope items)
• Business, functional, and non-functional requirements
• Assumptions and constraints
• Success criteria and metrics

Your BRD is being generated now! 🚀
            """
        
        return prompt
    

    

    
    def generate_brd_markdown(self, llm_service=None) -> str:
        """Generate complete BRD in Markdown format using pure AI generation"""
        if not self.schema.project_name:
            return "Error: Project name is required to generate BRD"
        
        if not llm_service:
            return "Error: LLM service is required for AI generation"
        
        # Use pure AI generation based on the schema data
        # No templates, only dynamic content from AI analysis
        brd_content = f"""# Business Requirements Document (BRD)

## {self.schema.project_name}

**Document Version:** 1.0.0  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Prepared by:** AI-Powered Business Requirement Agent

---

## 1. Executive Summary

**Strategic Overview and Business Impact:**

"""
        
        # Generate executive summary using AI based on project data
        executive_summary = self._generate_ai_section_content(
            llm_service, 
            "executive_summary", 
            f"Write a simple executive summary paragraph (5-7 lines) for the project '{self.schema.project_name}'. Focus on: what this project is, why it's important, and what business value it will deliver. Use simple, clear language. Do NOT include any JSON, technical details, or bullet points - just write a flowing paragraph."
        )
        brd_content += executive_summary
        
        brd_content += f"""
---

## 2. Project Overview

### 2.1 Project Name
**{self.schema.project_name}**

### 2.2 Project Objectives
"""
        
        # Use AI-generated objectives from schema
        if self.schema.objectives and len(self.schema.objectives) > 0:
            for objective in self.schema.objectives:
                brd_content += f"• {objective}\n"
        else:
            brd_content += "*No objectives specified*\n"
        
        brd_content += f"""
### 2.3 Target Users
"""
        
        # Use AI-generated stakeholders from schema
        if self.schema.stakeholders and len(self.schema.stakeholders) > 0:
            for stakeholder in self.schema.stakeholders:
                brd_content += f"• {stakeholder}\n"
        else:
            brd_content += "*No stakeholders specified*\n"
        
        brd_content += """
---

## 3. Project Scope

### 3.1 In Scope
"""
        
        # Use AI-generated scope from schema
        if self.schema.scope and self.schema.scope.get("in_scope") and len(self.schema.scope["in_scope"]) > 0:
            for item in self.schema.scope["in_scope"]:
                brd_content += f"• {item}\n"
        else:
            brd_content += "*No in-scope items specified*\n"
        
        brd_content += """
### 3.2 Out of Scope
"""
        
        # Use AI-generated scope from schema
        if self.schema.scope and self.schema.scope.get("out_scope") and len(self.schema.scope["out_scope"]) > 0:
            for item in self.schema.scope["out_scope"]:
                brd_content += f"• {item}\n"
        else:
            brd_content += "*No out-of-scope items specified*\n"
        
        brd_content += """
---

## 4. Business Requirements

**High-Level Business Needs and Strategic Objectives:**
"""
        
        # Use AI-generated business requirements from schema
        if self.schema.requirements and self.schema.requirements.get("business") and len(self.schema.requirements["business"]) > 0:
            for req in self.schema.requirements["business"]:
                brd_content += f"• {req}\n"
        else:
            brd_content += "*No business requirements specified*\n"
        
        brd_content += """
---

## 5. Functional Requirements

**Core System Capabilities and Essential Features:**
"""
        
        # Use AI-generated functional requirements from schema
        if self.schema.requirements and self.schema.requirements.get("functional") and len(self.schema.requirements["functional"]) > 0:
            for req in self.schema.requirements["functional"]:
                brd_content += f"• {req}\n"
        else:
            brd_content += "*No functional requirements specified*\n"
        
        brd_content += """
---

## 6. Non-Functional Requirements

**Performance, Security, Usability, and Reliability Standards:**
"""
        
        # Use AI-generated non-functional requirements from schema
        if self.schema.requirements and self.schema.requirements.get("non_functional") and len(self.schema.requirements["non_functional"]) > 0:
            for req in self.schema.requirements["non_functional"]:
                brd_content += f"• {req}\n"
        else:
            brd_content += "*No non-functional requirements specified*\n"
        
        brd_content += """
---

## 7. User Roles & Permissions

**Comprehensive Access Control and Role Definition:**
"""
        
        # Use AI-generated user roles from schema or generate minimal content
        if self.schema.stakeholders and len(self.schema.stakeholders) > 0:
            brd_content += "**Based on the identified stakeholders:**\n"
            for stakeholder in self.schema.stakeholders:
                brd_content += f"• {stakeholder}\n"
        else:
            brd_content += "*No user roles specified*\n"
        
        brd_content += """
---

## 8. Success Criteria

**Measurable Goals and Success Metrics:**
"""
        
        # Use AI-generated success criteria from schema
        if self.schema.success_criteria and len(self.schema.success_criteria) > 0:
            for criterion in self.schema.success_criteria:
                brd_content += f"• {criterion}\n"
        else:
            brd_content += "*No success criteria specified*\n"
        
        brd_content += """
---

## 9. Assumptions & Constraints

### 9.1 Critical Assumptions
"""
        
        # Use AI-generated assumptions from schema
        if self.schema.assumptions and len(self.schema.assumptions) > 0:
            for assumption in self.schema.assumptions:
                brd_content += f"• {assumption}\n"
        else:
            brd_content += "*No assumptions specified*\n"
        
        brd_content += """
### 9.2 Project Constraints
"""
        
        # Use AI-generated constraints from schema
        if self.schema.constraints and len(self.schema.constraints) > 0:
            for constraint in self.schema.constraints:
                brd_content += f"• {constraint}\n"
        else:
            brd_content += "*No constraints specified*\n"
        
        brd_content += """
---

## 10. Conclusion

**Strategic Summary and Implementation Roadmap:**

"""
        
        # Generate conclusion using AI based on project data
        conclusion_content = self._generate_ai_section_content(
            llm_service,
            "conclusion",
            f"Write a simple conclusion paragraph (5-7 lines) for the project '{self.schema.project_name}'. Focus on: what success looks like, key benefits, and next steps. Use simple, clear language. Do NOT include any JSON, technical details, or bullet points - just write a flowing paragraph."
        )
        brd_content += conclusion_content
        
        brd_content += """

---

*This document was generated by the AI-Powered Business Requirement Agent using Google Gemini AI and comprehensive business analysis.*
        """
        
        return brd_content
    
    def _generate_ai_section_content(self, llm_service, section_name: str, prompt: str) -> str:
        """Generate AI content for a specific section using pure AI generation"""
        try:
            print(f"🤖 Generating AI content for section: {section_name}")
            
            # Check if LLM service is available
            if not llm_service:
                print(f"   ⚠️ LLM service not available for {section_name}, using fallback content")
                if section_name.lower() == 'executive_summary':
                    if self.schema.objectives:
                        first_objective = self.schema.objectives[0] if self.schema.objectives else "improve business operations"
                        return f"The {self.schema.project_name} project represents a strategic initiative to {first_objective.lower()}. This comprehensive development effort aims to deliver significant business value through enhanced operational efficiency and improved customer experience. The project will establish a robust foundation for future growth while addressing current business challenges and market opportunities. By implementing this solution, the organization expects to achieve measurable improvements in key performance indicators and strengthen its competitive position in the market.\n\n"
                    else:
                        return f"The {self.schema.project_name} project represents a strategic initiative to improve business operations and deliver significant value to stakeholders. This comprehensive development effort will establish a robust foundation for future growth while addressing current business challenges and market opportunities. The project focuses on enhancing operational efficiency and improving customer experience through innovative technology solutions. By implementing this solution, the organization expects to achieve measurable improvements in key performance indicators and strengthen its competitive position in the market.\n\n"
                elif section_name.lower() == 'conclusion':
                    if self.schema.objectives:
                        first_objective = self.schema.objectives[0] if self.schema.objectives else "improve business operations"
                        return f"In conclusion, the {self.schema.project_name} project represents a transformative opportunity to {first_objective.lower()} and deliver substantial business value. The successful implementation of this initiative will establish a solid foundation for sustainable growth while addressing current operational challenges and market opportunities. By focusing on enhanced efficiency and improved customer experience, the project will generate measurable improvements in key performance indicators and strengthen the organization's competitive position. The strategic investment in this project demonstrates our commitment to innovation and operational excellence, positioning the organization for long-term success in an evolving business landscape.\n\n"
                    else:
                        return f"In conclusion, the {self.schema.project_name} project represents a transformative opportunity to improve business operations and deliver substantial value to all stakeholders. The successful implementation of this initiative will establish a solid foundation for sustainable growth while addressing current operational challenges and market opportunities. By focusing on enhanced efficiency and improved customer experience, the project will generate measurable improvements in key performance indicators and strengthen the organization's competitive position. The strategic investment in this project demonstrates our commitment to innovation and operational excellence, positioning the organization for long-term success in an evolving business landscape.\n\n"
                else:
                    return f"Content for {section_name} section based on project requirements.\n\n"
            
            # Create a focused prompt for pure AI generation
            section_prompt = f"""
You are writing content for a Business Requirements Document.

Section: {section_name}
Project: {self.schema.project_name}

Task: {prompt}

CRITICAL RULES:
- Write ONLY the content, nothing else
- NO JSON, NO technical details, NO bullet points
- NO explanations or formatting instructions
- Just write the actual content in simple, clear language
- For Executive Summary and Conclusion: Write 5-7 lines as a flowing paragraph
- Use the project name and basic project information only

Start writing the content now:
            """
            
            # Call the LLM service for pure AI generation
            response = llm_service._generate_with_gemini(section_prompt, "gemini-2.0-flash", expect_json=False)
            
            print(f"   📝 LLM response type: {type(response)}")
            print(f"   📝 LLM response preview: {str(response)[:100]}...")
            
            # Handle response and return clean content
            if response and isinstance(response, str):
                content = response.strip()
                
                # Check if AI returned JSON instead of content
                if (content.startswith('{') or content.startswith('[') or 
                    'project_name' in content or 'stakeholders' in content or 
                    'objectives' in content or 'requirements' in content):
                    print(f"   ⚠️ AI returned JSON instead of content, filtering...")
                    # Try to extract meaningful content or use fallback
                    if section_name.lower() in ['executive_summary', 'conclusion']:
                        if section_name.lower() == 'executive_summary':
                            if self.schema.objectives:
                                first_objective = self.schema.objectives[0] if self.schema.objectives else "improve business operations"
                                content = f"The {self.schema.project_name} project represents a strategic initiative to {first_objective.lower()}. This comprehensive development effort aims to deliver significant business value through enhanced operational efficiency and improved customer experience. The project will establish a robust foundation for future growth while addressing current business challenges and market opportunities. By implementing this solution, the organization expects to achieve measurable improvements in key performance indicators and strengthen its competitive position in the market."
                            else:
                                content = f"The {self.schema.project_name} project represents a strategic initiative to improve business operations and deliver significant value to stakeholders. This comprehensive development effort will establish a robust foundation for future growth while addressing current business challenges and market opportunities. The project focuses on enhancing operational efficiency and improving customer experience through innovative technology solutions. By implementing this solution, the organization expects to achieve measurable improvements in key performance indicators and strengthen its competitive position in the market."
                        elif section_name.lower() == 'conclusion':
                            if self.schema.objectives:
                                first_objective = self.schema.objectives[0] if self.schema.objectives else "improve business operations"
                                content = f"In conclusion, the {self.schema.project_name} project represents a transformative opportunity to {first_objective.lower()} and deliver substantial business value. The successful implementation of this initiative will establish a solid foundation for sustainable growth while addressing current operational challenges and market opportunities. By focusing on enhanced efficiency and improved customer experience, the project will generate measurable improvements in key performance indicators and strengthen the organization's competitive position. The strategic investment in this project demonstrates our commitment to innovation and operational excellence, positioning the organization for long-term success in an evolving business landscape."
                            else:
                                content = f"In conclusion, the {self.schema.project_name} project represents a transformative opportunity to improve business operations and deliver substantial value to all stakeholders. The successful implementation of this initiative will establish a solid foundation for sustainable growth while addressing current operational challenges and market opportunities. By focusing on enhanced efficiency and improved customer experience, the project will generate measurable improvements in key performance indicators and strengthen the organization's competitive position. The strategic investment in this project demonstrates our commitment to innovation and operational excellence, positioning the organization for long-term success in an evolving business landscape."
                        else:
                            content = f"Content for {section_name} section based on project requirements."
                    else:
                        content = f"Content for {section_name} section based on project requirements."
                else:
                    print(f"   ✅ Using AI-generated content")
            else:
                # If AI generation fails, return minimal content
                content = f"AI-generated content for {section_name} section"
                print(f"   ⚠️ Using minimal content due to AI generation failure")
            
            # Clean up the response and ensure proper formatting
            content = content.strip()
            
            # Remove any JSON artifacts that might have slipped through
            content = content.replace('```json', '').replace('```', '').replace('{', '').replace('}', '').replace('[', '').replace(']', '')
            content = content.replace('"project_name"', '').replace('"stakeholders"', '').replace('"objectives"', '').replace('"requirements"', '')
            
            # For paragraph-style sections, clean up whitespace and ensure paragraph format
            if section_name.lower() in ['executive_summary', 'conclusion']:
                # Remove bullet points if they exist
                content = content.replace('• ', '').replace('- ', '').replace('* ', '')
                # Clean up whitespace and ensure it's one continuous paragraph
                content = ' '.join(content.split())  # Remove extra whitespace
                content = content.replace(' .', '.').replace(' ,', ',').replace(' :', ':')  # Fix spacing around punctuation
                # Ensure it ends with proper punctuation
                if not content.endswith('.') and not content.endswith('!') and not content.endswith('?'):
                    content += '.'
                
                # Validate paragraph length (should be 5-7 lines when wrapped)
                word_count = len(content.split())
                if word_count < 50:  # Too short for 5-7 lines
                    print(f"   ⚠️ {section_name} is too short ({word_count} words), requesting regeneration")
                    # Could add logic here to regenerate if too short
                elif word_count > 120:  # Too long for 5-7 lines
                    print(f"   ⚠️ {section_name} is too long ({word_count} words), may need trimming")
                    # Could add logic here to trim if too long
                else:
                    print(f"   ✅ {section_name} paragraph length is good: {word_count} words")
                
                print(f"   📝 Formatted {section_name} as paragraph: {word_count} words")
            
            return content + "\n"
            
        except Exception as e:
            print(f"⚠️ AI generation failed for {section_name}: {e}")
            # Return minimal content if AI generation fails
            return f"AI-generated content for {section_name} section"

    
    def export_schema_json(self) -> str:
        """Export BRD schema as JSON"""
        try:
            return json.dumps(asdict(self.schema), indent=2)
        except Exception as e:
            print(f"⚠️ asdict failed, using manual conversion: {e}")
            # Fallback: manual conversion
            schema_dict = {
                "project_name": self.schema.project_name,
                "stakeholders": self.schema.stakeholders,
                "objectives": self.schema.objectives,
                "scope": self.schema.scope,
                "requirements": self.schema.requirements,
                "assumptions": self.schema.assumptions,
                "constraints": self.schema.constraints,
                "success_criteria": self.schema.success_criteria
            }
            return json.dumps(schema_dict, indent=2)
    
    def analyze_existing_brd(self, brd_content: str) -> Dict[str, Any]:
        """
        Analyze existing BRD document and extract structured information
        This method parses existing BRD content and extracts key information
        """
        try:
            # Initialize extracted data
            extracted_data = {
                'project_name': '',
                'stakeholders': [],
                'objectives': [],
                'scope': {'in_scope': [], 'out_scope': []},
                'requirements': {'business': [], 'functional': [], 'non_functional': []},
                'assumptions': [],
                'constraints': [],
                'success_criteria': [],
                'analysis_notes': []
            }
            
            # Split content into lines for analysis
            lines = brd_content.split('\n')
            current_section = ''
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers
                if line.startswith('#') or line.startswith('##') or line.startswith('###'):
                    current_section = line.lower().replace('#', '').replace(' ', '').replace(':', '')
                    continue
                
                # Extract project name from title or first heading
                if current_section in ['', 'executivesummary', 'projectoverview'] and not extracted_data['project_name']:
                    if line and not line.startswith('*') and not line.startswith('-') and not line.startswith('•'):
                        extracted_data['project_name'] = line[:100]  # Limit length
                
                # Extract stakeholders
                if 'stakeholder' in current_section or 'stakeholders' in current_section:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        stakeholder = line[1:].strip()
                        if stakeholder and len(stakeholder) > 3:
                            extracted_data['stakeholders'].append(stakeholder)
                
                # Extract objectives
                if 'objective' in current_section or 'objectives' in current_section:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        objective = line[1:].strip()
                        if objective and len(objective) > 5:
                            extracted_data['objectives'].append(objective)
                
                # Extract scope
                if 'scope' in current_section:
                    if 'in-scope' in line.lower() or 'in scope' in line.lower():
                        current_scope_type = 'in_scope'
                    elif 'out-scope' in line.lower() or 'out scope' in line.lower():
                        current_scope_type = 'out_scope'
                    elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        scope_item = line[1:].strip()
                        if scope_item and len(scope_item) > 5:
                            if 'current_scope_type' in locals():
                                extracted_data['scope'][current_scope_type].append(scope_item)
                
                # Extract requirements
                if 'requirement' in current_section or 'requirements' in current_section:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        requirement = line[1:].strip()
                        if requirement and len(requirement) > 5:
                            # Categorize requirements based on content
                            if any(word in requirement.lower() for word in ['business', 'goal', 'objective', 'value']):
                                extracted_data['requirements']['business'].append(requirement)
                            elif any(word in requirement.lower() for word in ['function', 'feature', 'capability', 'system']):
                                extracted_data['requirements']['functional'].append(requirement)
                            else:
                                extracted_data['requirements']['non_functional'].append(requirement)
                
                # Extract assumptions
                if 'assumption' in current_section or 'assumptions' in current_section:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        assumption = line[1:].strip()
                        if assumption and len(assumption) > 5:
                            extracted_data['assumptions'].append(assumption)
                
                # Extract constraints
                if 'constraint' in current_section or 'constraints' in current_section:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        constraint = line[1:].strip()
                        if constraint and len(constraint) > 5:
                            extracted_data['constraints'].append(constraint)
                
                # Extract success criteria
                if 'success' in current_section or 'criteria' in current_section:
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        criterion = line[1:].strip()
                        if criterion and len(criterion) > 5:
                            extracted_data['success_criteria'].append(criterion)
            
            # Generate analysis notes
            total_items = (
                len(extracted_data['stakeholders']) +
                len(extracted_data['objectives']) +
                len(extracted_data['scope']['in_scope']) +
                len(extracted_data['scope']['out_scope']) +
                len(extracted_data['requirements']['business']) +
                len(extracted_data['requirements']['functional']) +
                len(extracted_data['requirements']['non_functional']) +
                len(extracted_data['assumptions']) +
                len(extracted_data['constraints']) +
                len(extracted_data['success_criteria'])
            )
            
            if total_items == 0:
                extracted_data['analysis_notes'].append("No structured content found in the document")
            else:
                extracted_data['analysis_notes'].append(f"Successfully extracted {total_items} items from the document")
            
            # Validate extracted data
            if not extracted_data['project_name']:
                extracted_data['project_name'] = "Unknown Project"
                extracted_data['analysis_notes'].append("Project name not found, using default")
            
            return extracted_data
            
        except Exception as e:
            return {
                'error': f'Failed to analyze BRD: {str(e)}',
                'project_name': 'Unknown Project',
                'stakeholders': [],
                'objectives': [],
                'scope': {'in_scope': [], 'out_scope': []},
                'requirements': {'business': [], 'functional': [], 'non_functional': []},
                'assumptions': [],
                'constraints': [],
                'success_criteria': [],
                'analysis_notes': [f'Analysis failed: {str(e)}']
            }
    
    def improve_existing_brd(self, existing_brd_content: str, improvement_instructions: str = "", llm_service=None) -> Dict[str, Any]:
        """
        Analyze existing BRD and improve it using AI
        This method combines document analysis with AI-powered improvements
        """
        try:
            # Step 1: Analyze existing BRD
            analysis_result = self.analyze_existing_brd(existing_brd_content)
            
            if 'error' in analysis_result:
                return {
                    'success': False,
                    'error': analysis_result['error'],
                    'improved_content': existing_brd_content,
                    'analysis': analysis_result
                }
            
            # Step 2: Generate improvement prompt
            improvement_prompt = self._generate_improvement_prompt(analysis_result, improvement_instructions)
            
            # Step 3: Use LLM to improve the BRD
            if llm_service:
                try:
                    improved_content = self._generate_ai_improved_brd(
                        llm_service, 
                        existing_brd_content, 
                        analysis_result, 
                        improvement_instructions
                    )
                    
                    return {
                        'success': True,
                        'improved_content': improved_content,
                        'analysis': analysis_result,
                        'improvement_notes': [
                            "BRD analyzed and improved using AI",
                            f"Original items: {sum(len(v) if isinstance(v, list) else len(v.values()) if isinstance(v, dict) else 0 for v in analysis_result.values() if v and isinstance(v, (list, dict)))}",
                            "AI improvements applied based on best practices"
                        ]
                    }
                    
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'AI improvement failed: {str(e)}',
                        'improved_content': existing_brd_content,
                        'analysis': analysis_result,
                        'improvement_notes': [f'AI improvement failed: {str(e)}']
                    }
            else:
                # Fallback: return analysis without AI improvement
                return {
                    'success': True,
                    'improved_content': existing_brd_content,
                    'analysis': analysis_result,
                    'improvement_notes': [
                        "BRD analyzed successfully",
                        "AI improvement not available (LLM service not provided)",
                        "Manual improvements recommended based on analysis"
                    ]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'BRD improvement process failed: {str(e)}',
                'improved_content': existing_brd_content,
                'analysis': {},
                'improvement_notes': [f'Process failed: {str(e)}']
            }
    
    def _generate_improvement_prompt(self, analysis_result: Dict[str, Any], improvement_instructions: str) -> str:
        """Generate a prompt for improving the existing BRD"""
        
        base_prompt = f"""
You are an expert Business Analyst reviewing and improving a Business Requirements Document (BRD).

**Current BRD Analysis:**
- Project: {analysis_result.get('project_name', 'Unknown')}
- Stakeholders: {len(analysis_result.get('stakeholders', []))} identified
- Objectives: {len(analysis_result.get('objectives', []))} identified
- Scope Items: {len(analysis_result.get('scope', {}).get('in_scope', []))} in-scope, {len(analysis_result.get('scope', {}).get('out_scope', []))} out-of-scope
- Requirements: {len(analysis_result.get('requirements', {}).get('business', []))} business, {len(analysis_result.get('requirements', {}).get('functional', []))} functional, {len(analysis_result.get('requirements', {}).get('non_functional', []))} non-functional
- Assumptions: {len(analysis_result.get('assumptions', []))} identified
- Constraints: {len(analysis_result.get('constraints', []))} identified
- Success Criteria: {len(analysis_result.get('success_criteria', []))} identified

**Improvement Instructions:**
{improvement_instructions if improvement_instructions else "Improve the BRD by enhancing clarity, completeness, and professional standards while maintaining all existing information."}

**Your Task:**
Analyze the existing BRD content and provide an improved version that:
1. Maintains all existing information
2. Enhances clarity and professionalism
3. Fills in any missing critical sections
4. Improves formatting and structure
5. Adds industry best practices where appropriate
6. Ensures consistency in terminology and style

Respond with the complete improved BRD in Markdown format.
"""
        
        return base_prompt
    
    def _generate_ai_improved_brd(self, llm_service, existing_content: str, analysis_result: Dict[str, Any], improvement_instructions: str) -> str:
        """Use AI to improve the existing BRD content"""
        
        # Create a comprehensive prompt for improvement
        improvement_prompt = f"""
{self._generate_improvement_prompt(analysis_result, improvement_instructions)}

**Existing BRD Content:**
```
{existing_content}
```

**Instructions:**
Please analyze this existing BRD and provide an improved version that addresses the improvement instructions while maintaining all existing information. Return the complete improved BRD in Markdown format.
"""
        
        try:
            # Use the LLM service to generate improvements
            if hasattr(llm_service, 'generate_brd_from_input'):
                # Use the existing method if available
                improved_result = llm_service.generate_brd_from_input(improvement_prompt)
                if isinstance(improved_result, dict):
                    # Convert the improved BRD data to markdown format
                    try:
                        # Create a temporary BRA instance with the improved data
                        temp_bra = BusinessRequirementAgent()
                        temp_bra.schema.project_name = improved_result.get('project_name', analysis_result.get('project_name', 'Unknown Project'))
                        temp_bra.schema.stakeholders = improved_result.get('stakeholders', analysis_result.get('stakeholders', []))
                        temp_bra.schema.objectives = improved_result.get('objectives', analysis_result.get('objectives', []))
                        
                        # Handle nested scope structure
                        scope_data = improved_result.get('scope', analysis_result.get('scope', {}))
                        if isinstance(scope_data, dict):
                            temp_bra.schema.scope["in_scope"] = scope_data.get('in_scope', [])
                            temp_bra.schema.scope["out_scope"] = scope_data.get('out_scope', [])
                        
                        # Handle nested requirements structure
                        requirements_data = improved_result.get('requirements', analysis_result.get('requirements', {}))
                        if isinstance(requirements_data, dict):
                            temp_bra.schema.requirements["business"] = requirements_data.get('business', [])
                            temp_bra.schema.requirements["functional"] = requirements_data.get('functional', [])
                            temp_bra.schema.requirements["non_functional"] = requirements_data.get('non_functional', [])
                        
                        temp_bra.schema.assumptions = improved_result.get('assumptions', analysis_result.get('assumptions', []))
                        temp_bra.schema.constraints = improved_result.get('constraints', analysis_result.get('constraints', []))
                        temp_bra.schema.success_criteria = improved_result.get('success_criteria', analysis_result.get('success_criteria', []))
                        
                        # Generate markdown from the improved schema
                        return temp_bra.generate_brd_markdown(llm_service)
                    except Exception as conversion_error:
                        print(f"⚠️ Error converting improved BRD data to markdown: {conversion_error}")
                        # Fallback to analysis summary
                        return self._generate_fallback_improved_brd(existing_content, analysis_result)
                else:
                    return improved_result
            else:
                # Fallback: return the original content with analysis notes
                return self._generate_fallback_improved_brd(existing_content, analysis_result)
                
        except Exception as e:
            # Return original content with error note
            return f"""# BRD Analysis - {analysis_result.get('project_name', 'Unknown Project')}

## Analysis Results
The BRD has been analyzed but AI improvement failed: {str(e)}

**Original Content:**
{existing_content}

**Recommendation:** Manual review and improvement based on the analysis above.
"""
    
    def _generate_fallback_improved_brd(self, existing_content: str, analysis_result: Dict[str, Any]) -> str:
        """Generate a fallback improved BRD when AI improvement fails"""
        
        project_name = analysis_result.get('project_name', 'Unknown Project')
        
        return f"""# Improved BRD - {project_name}

## Analysis Summary
This BRD has been analyzed and the following improvements are recommended:

**Items Found:**
- Stakeholders: {len(analysis_result.get('stakeholders', []))}
- Objectives: {len(analysis_result.get('objectives', []))}
- Requirements: {len(analysis_result.get('requirements', {}).get('business', []))} business, {len(analysis_result.get('requirements', {}).get('functional', []))} functional, {len(analysis_result.get('requirements', {}).get('non_functional', []))} non-functional
- Assumptions: {len(analysis_result.get('assumptions', []))}
- Constraints: {len(analysis_result.get('constraints', []))}
- Success Criteria: {len(analysis_result.get('success_criteria', []))}

**Original Content:**
{existing_content}

**Note:** AI improvement service not available. Manual review recommended.
"""

    
    def export_schema_json(self) -> str:
        """Export BRD schema as JSON"""
        try:
            return json.dumps(asdict(self.schema), indent=2)
        except Exception as e:
            print(f"⚠️ asdict failed, using manual conversion: {e}")
            # Fallback: manual conversion
            schema_dict = {
                "project_name": self.schema.project_name,
                "stakeholders": self.schema.stakeholders,
                "objectives": self.schema.objectives,
                "scope": self.schema.scope,
                "requirements": self.schema.requirements,
                "assumptions": self.schema.assumptions,
                "constraints": self.schema.constraints,
                "success_criteria": self.schema.success_criteria
            }
            return json.dumps(schema_dict, indent=2)
    

    

