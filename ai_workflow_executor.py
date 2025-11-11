#!/usr/bin/env python3
"""
AI Workflow Executor - Automatically executes evaluation workflows without human prompting.

This module provides automated execution of comprehensive evaluation workflows
based on detected context from user requests.
"""

import subprocess
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import sys

from ai_context_detector import WorkflowType, DetectionResult

@dataclass
class WorkflowStep:
    """Individual step in an automated workflow"""
    name: str
    description: str
    command: Optional[str] = None
    function: Optional[str] = None
    required: bool = True
    completed: bool = False
    evidence: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass 
class WorkflowExecution:
    """Complete workflow execution tracking"""
    workflow_type: WorkflowType
    branch_name: Optional[str]
    start_time: datetime
    steps: List[WorkflowStep] = field(default_factory=list)
    completed: bool = False
    success: bool = False
    evidence_collected: Dict[str, Any] = field(default_factory=dict)
    final_recommendation: Optional[str] = None
    end_time: Optional[datetime] = None

class WorkflowPhaseEngine:
    """
    Standardized phase execution engine for workflow steps.
    
    Provides consistent error handling, evidence collection, and execution
    patterns across all workflow phases.
    """
    
    def __init__(self, executor_instance):
        """Initialize with reference to the main executor"""
        self.executor = executor_instance
        
    def execute_phase(self, phase_name: str, phase_description: str, 
                     phase_function: callable, execution: WorkflowExecution,
                     command: Optional[str] = None, **kwargs) -> WorkflowStep:
        """
        Execute a workflow phase with standardized error handling and evidence collection.
        
        Args:
            phase_name: Unique identifier for the phase
            phase_description: Human-readable description
            phase_function: Function to execute for this phase
            execution: Current workflow execution context
            command: Optional shell command associated with the phase
            **kwargs: Additional arguments to pass to phase_function
            
        Returns:
            WorkflowStep with execution results and evidence
        """
        step = WorkflowStep(
            name=phase_name,
            description=phase_description,
            command=command,
            function=phase_function.__name__ if hasattr(phase_function, '__name__') else str(phase_function)
        )
        
        try:
            # Execute the phase function
            evidence = phase_function(**kwargs)
            
            # Collect and structure evidence
            step.evidence = self._collect_phase_evidence(phase_name, evidence)
            step.completed = True
            
            # Update execution context
            execution.evidence_collected[f"{phase_name}_completed"] = True
            
        except Exception as e:
            # Handle phase errors consistently
            error_context = self._handle_phase_error(phase_name, e, execution)
            step.error_message = error_context["message"]
            step.evidence = error_context["debug_info"]
        
        return step
    
    def _handle_phase_error(self, phase_name: str, error: Exception, 
                          execution: WorkflowExecution) -> Dict[str, Any]:
        """
        Standardized error handling for workflow phases.
        
        Args:
            phase_name: Name of the failed phase
            error: The exception that occurred
            execution: Current workflow execution context
            
        Returns:
            Dict with error message and debug information
        """
        error_context = {
            "message": f"Phase '{phase_name}' failed: {str(error)}",
            "debug_info": {
                "phase": phase_name,
                "error_type": type(error).__name__,
                "error_details": str(error),
                "execution_id": id(execution),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Log error for debugging
        print(f"⚠️  Workflow Phase Error: {error_context['message']}")
        
        return error_context
    
    def _collect_phase_evidence(self, phase_name: str, raw_evidence: Any) -> Dict[str, Any]:
        """
        Standardize evidence collection and formatting.
        
        Args:
            phase_name: Name of the phase generating evidence
            raw_evidence: Raw evidence data from phase execution
            
        Returns:
            Standardized evidence dictionary
        """
        if raw_evidence is None:
            return {"status": "no_evidence", "phase": phase_name}
            
        if isinstance(raw_evidence, dict):
            return {
                "phase": phase_name,
                "collected_at": datetime.now().isoformat(),
                **raw_evidence
            }
        elif isinstance(raw_evidence, (subprocess.CompletedProcess,)):
            return {
                "phase": phase_name,
                "collected_at": datetime.now().isoformat(),
                "command_output": raw_evidence.stdout,
                "command_errors": raw_evidence.stderr,
                "return_code": raw_evidence.returncode,
                "success": raw_evidence.returncode == 0
            }
        else:
            return {
                "phase": phase_name,
                "collected_at": datetime.now().isoformat(),
                "raw_data": str(raw_evidence),
                "data_type": type(raw_evidence).__name__
            }

class AIWorkflowExecutor:
    """Automatically executes evaluation workflows based on detected context"""
    
    def __init__(self, project_root: str = "."):
        """Initialize the workflow executor"""
        self.project_root = Path(project_root)
        self.execution_history: List[WorkflowExecution] = []
        self.phase_engine = WorkflowPhaseEngine(self)
        
    def execute_workflow(self, detection_result: DetectionResult) -> WorkflowExecution:
        """
        Execute appropriate workflow based on detection result
        
        Args:
            detection_result: Result from context detection
            
        Returns:
            WorkflowExecution with complete results and evidence
        """
        execution = WorkflowExecution(
            workflow_type=detection_result.workflow_type,
            branch_name=detection_result.detected_branch,
            start_time=datetime.now()
        )
        
        try:
            if detection_result.workflow_type == WorkflowType.INTEGRATION_ASSESSMENT:
                self._execute_integration_assessment(execution, detection_result)
            elif detection_result.workflow_type == WorkflowType.TEST_VALIDATION:
                self._execute_test_validation(execution, detection_result)
            elif detection_result.workflow_type == WorkflowType.CODE_ANALYSIS:
                self._execute_code_analysis(execution, detection_result)
            else:
                # Standard response - no special workflow
                execution.completed = True
                execution.success = True
                
        except Exception as e:
            execution.success = False
            execution.error_message = str(e)
        finally:
            execution.end_time = datetime.now()
            self.execution_history.append(execution)
            
        return execution
    
    def _execute_integration_assessment(self, execution: WorkflowExecution, detection: DetectionResult):
        """Execute complete integration assessment workflow using extracted phase methods"""
        
        # Execute all workflow phases using extracted methods
        phases = [
            lambda: self._execute_path_validation_phase(execution),
            lambda: self._execute_branch_detection_phase(execution, detection),
            lambda: self._execute_history_analysis_phase(execution, detection),
            lambda: self._execute_test_execution_phase(execution),
            lambda: self._execute_e2e_validation_phase(execution),
            lambda: self._execute_integration_decision_phase(execution)
        ]
        
        # Execute each phase and collect results
        for phase_func in phases:
            step = phase_func()
            execution.steps.append(step)
        
        # Mark execution as completed
        all_critical_steps_completed = all(
            step.completed for step in execution.steps if step.required
        )
        execution.completed = all_critical_steps_completed
        execution.success = all_critical_steps_completed and not any(step.error_message for step in execution.steps)
    
    def _execute_test_validation(self, execution: WorkflowExecution, detection: DetectionResult):
        """Execute comprehensive test validation workflow"""
        
        # Phase 1: Dependency verification
        step1 = WorkflowStep(
            name="verify_dependencies",
            description="Verify all test dependencies are available",
            function="verify_test_dependencies"
        )
        execution.steps.append(step1)
        
        try:
            deps = self._verify_test_dependencies()
            step1.completed = True
            step1.evidence = deps
        except Exception as e:
            step1.error_message = str(e)
        
        # Phase 2: Test pyramid execution
        step2 = WorkflowStep(
            name="execute_test_pyramid",
            description="Execute unit, integration, and E2E tests",
            command="python run_tests.py"
        )
        execution.steps.append(step2)
        
        try:
            result = self._execute_command(step2.command)
            step2.completed = True
            step2.evidence = {"output": result.stdout, "success": result.returncode == 0}
        except Exception as e:
            step2.error_message = str(e)
        
        # Phase 3: System readiness assessment
        step3 = WorkflowStep(
            name="assess_system_readiness",
            description="Assess system readiness based on test results",
            function="assess_system_readiness"
        )
        execution.steps.append(step3)
        
        try:
            assessment = self._assess_system_readiness(execution)
            step3.completed = True
            step3.evidence = assessment
            execution.final_recommendation = assessment.get("readiness", "UNKNOWN")
        except Exception as e:
            step3.error_message = str(e)
        
        execution.completed = all(step.completed for step in execution.steps)
        execution.success = execution.completed and not any(step.error_message for step in execution.steps)
    
    def _execute_code_analysis(self, execution: WorkflowExecution, detection: DetectionResult):
        """Execute code analysis workflow"""
        
        # Phase 1: Git analysis
        step1 = WorkflowStep(
            name="git_analysis",
            description="Analyze git history and changes",
            command=f"git log --oneline -5 {detection.detected_branch or 'HEAD'}"
        )
        execution.steps.append(step1)
        
        try:
            result = self._execute_command(step1.command)
            step1.completed = True
            step1.evidence = {"commits": result.stdout}
        except Exception as e:
            step1.error_message = str(e)
        
        # Phase 2: Quality check
        step2 = WorkflowStep(
            name="quality_check",
            description="Execute quality checks and tests",
            command="python run_tests.py --quiet"
        )
        execution.steps.append(step2)
        
        try:
            result = self._execute_command(step2.command)
            step2.completed = True
            step2.evidence = {"output": result.stdout, "success": result.returncode == 0}
        except Exception as e:
            step2.error_message = str(e)
        
        execution.completed = all(step.completed for step in execution.steps)
        execution.success = execution.completed
    
    # Phase extraction methods for _execute_integration_assessment refactoring
    def _execute_path_validation_phase(self, execution: WorkflowExecution) -> WorkflowStep:
        """Execute Phase 1: Path configuration validation"""
        return self.phase_engine.execute_phase(
            phase_name="validate_paths",
            phase_description="Validate project paths and configuration", 
            phase_function=self._review_documentation,
            execution=execution
        )
    
    def _execute_branch_detection_phase(self, execution: WorkflowExecution, detection: DetectionResult) -> WorkflowStep:
        """Execute Phase 2: Git branch detection and validation"""
        return self.phase_engine.execute_phase(
            phase_name="detect_branch",
            phase_description="Detect current git branch and validate context",
            phase_function=self._detect_branch_info,
            execution=execution,
            command="git branch --show-current",
            detection=detection
        )
    
    def _detect_branch_info(self, command: str = "git branch --show-current", detection: DetectionResult = None) -> Dict[str, Any]:
        """Helper method for branch detection phase"""
        result = self._execute_command(command)
        current_branch = result.stdout.strip()
        return {
            "current_branch": current_branch,
            "detected_branch": detection.detected_branch if detection else None,
            "branch_match": current_branch == (detection.detected_branch if detection else ""),
            "command_output": result.stdout,
            "return_code": result.returncode
        }
    
    def _execute_history_analysis_phase(self, execution: WorkflowExecution, detection: DetectionResult) -> WorkflowStep:
        """Execute Phase 3: Repository history analysis"""
        step = WorkflowStep(
            name="analyze_history",
            description="Analyze recent repository history and changes",
            command=f"git log --oneline -10 {detection.detected_branch or 'HEAD'}"
        )
        
        try:
            result = self._execute_command(step.command)
            step.completed = True
            step.evidence = {"commits": result.stdout, "branch": detection.detected_branch}
            execution.evidence_collected["history_analyzed"] = True
        except Exception as e:
            step.error_message = str(e)
        
        return step
    
    def _execute_test_execution_phase(self, execution: WorkflowExecution) -> WorkflowStep:
        """Execute Phase 4: Complete test execution"""
        return self.phase_engine.execute_phase(
            phase_name="complete_test_execution",
            phase_description="Execute comprehensive test suite",
            phase_function=self._execute_test_command,
            execution=execution,
            command="python run_tests.py --quiet"
        )
    
    def _execute_test_command(self, command: str = "python run_tests.py --quiet") -> Dict[str, Any]:
        """Helper method for test execution phase"""
        result = self._execute_command(command)
        test_success = result.returncode == 0
        return {
            "output": result.stdout,
            "success": test_success,
            "test_command": command,
            "return_code": result.returncode
        }
    
    def _execute_e2e_validation_phase(self, execution: WorkflowExecution) -> WorkflowStep:
        """Execute Phase 5: End-to-end validation"""
        step = WorkflowStep(
            name="e2e_validation",
            description="Execute end-to-end workflow validation",
            command="pytest -q -s tests/test_mva_complaints_tab_fixed.py::TestMVAComplaintsTab::test_mva_complaints_workflow"
        )
        
        try:
            # Check if E2E test dependencies are available
            if self._check_e2e_dependencies():
                result = self._execute_command(step.command)
                step.completed = True
                e2e_success = result.returncode == 0
                step.evidence = {
                    "output": result.stdout,
                    "success": e2e_success,
                    "dependencies_available": True
                }
                execution.evidence_collected["e2e_validated"] = e2e_success
            else:
                step.completed = True
                step.evidence = {
                    "skipped": True, 
                    "reason": "E2E dependencies not available (requires browser setup)",
                    "dependencies_available": False
                }
                execution.evidence_collected["e2e_validated"] = "skipped"
        except Exception as e:
            step.error_message = str(e)
        
        return step
    
    def _execute_integration_decision_phase(self, execution: WorkflowExecution) -> WorkflowStep:
        """Execute Phase 6: Integration readiness decision"""
        step = WorkflowStep(
            name="integration_decision",
            description="Make evidence-based integration recommendation",
            function="make_integration_decision"
        )
        
        try:
            decision = self._make_integration_decision(execution)
            step.completed = True
            step.evidence = decision
            execution.final_recommendation = decision["recommendation"]
            execution.evidence_collected["decision_made"] = True
        except Exception as e:
            step.error_message = str(e)
        
        return step
    
    def _execute_command(self, command: str) -> subprocess.CompletedProcess:
        """Execute a shell command and return result"""
        return subprocess.run(
            command, 
            shell=True, 
            cwd=self.project_root,
            capture_output=True, 
            text=True,
            timeout=60  # 60 second timeout
        )
    
    def _review_documentation(self) -> Dict[str, Any]:
        """Review project documentation for requirements"""
        evidence = {}
        
        # Check for key documentation files
        doc_files = ["markdown/GEMINI.md", "README.md", "markdown/CODE_EVALUATION_STANDARDS.md"]
        
        for doc_file in doc_files:
            file_path = self.project_root / doc_file
            if file_path.exists():
                evidence[doc_file.lower()] = {
                    "exists": True,
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                }
            else:
                evidence[doc_file.lower()] = {"exists": False}
        
        return evidence
    
    def _verify_test_dependencies(self) -> Dict[str, Any]:
        """Verify test dependencies are available"""
        dependencies = {}
        
        # Check test data
        data_file = self.project_root / "data" / "mva.csv" 
        dependencies["test_data"] = data_file.exists()
        
        # Check config files
        config_file = self.project_root / "config" / "config.json"
        dependencies["config"] = config_file.exists()
        
        # Check test runner
        test_runner = self.project_root / "run_tests.py"
        dependencies["test_runner"] = test_runner.exists()
        
        return dependencies
    
    def _check_e2e_dependencies(self) -> bool:
        """Check if E2E test dependencies are available"""
        # Check for WebDriver and browser requirements
        data_available = (self.project_root / "data" / "mva.csv").exists()
        config_available = (self.project_root / "config" / "config.json").exists()
        test_file_available = (self.project_root / "tests" / "test_mva_complaints_tab_fixed.py").exists()
        
        return data_available and config_available and test_file_available
    
    def _make_integration_decision(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Make evidence-based integration decision"""
        evidence = execution.evidence_collected
        
        # Check critical requirements
        docs_reviewed = evidence.get("documentation_reviewed", False)
        tests_passed = evidence.get("tests_executed", False) 
        history_analyzed = evidence.get("history_analyzed", False)
        
        # Determine readiness
        if docs_reviewed and tests_passed and history_analyzed:
            if evidence.get("e2e_validated") == True:
                recommendation = "READY"
                confidence = "HIGH"
            elif evidence.get("e2e_validated") == "skipped":
                recommendation = "READY_WITH_CAVEAT" 
                confidence = "MEDIUM"
            else:
                recommendation = "NOT_READY"
                confidence = "MEDIUM"
        else:
            recommendation = "NOT_READY"
            confidence = "LOW"
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "evidence_summary": evidence,
            "missing_requirements": [
                req for req in ["documentation_reviewed", "tests_executed", "history_analyzed"] 
                if not evidence.get(req, False)
            ]
        }
    
    def _assess_system_readiness(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Assess system readiness based on test results"""
        test_evidence = {}
        
        for step in execution.steps:
            if "test" in step.name.lower():
                test_evidence[step.name] = step.evidence
        
        # Determine overall readiness
        all_tests_passed = all(
            evidence.get("success", False) 
            for evidence in test_evidence.values()
            if isinstance(evidence, dict)
        )
        
        readiness = "READY" if all_tests_passed else "NOT_READY"
        
        return {
            "readiness": readiness,
            "test_evidence": test_evidence,
            "all_tests_passed": all_tests_passed
        }
    
    def get_execution_summary(self, execution: WorkflowExecution) -> str:
        """Get human-readable summary of workflow execution"""
        summary_parts = [
            f"🤖 **Automated {execution.workflow_type.value.replace('_', ' ').title()} Complete**",
            f"**Branch**: {execution.branch_name or 'current'}",
            f"**Duration**: {(execution.end_time - execution.start_time).total_seconds():.1f}s",
            f"**Status**: {'✅ SUCCESS' if execution.success else '❌ FAILED'}",
            ""
        ]
        
        # Add step results
        summary_parts.append("**Steps Executed**:")
        for i, step in enumerate(execution.steps, 1):
            status = "✅" if step.completed else "❌" 
            summary_parts.append(f"{i}. {status} {step.description}")
            if step.error_message:
                summary_parts.append(f"   ⚠️ Error: {step.error_message}")
        
        # Add final recommendation if available
        if execution.final_recommendation:
            summary_parts.extend([
                "",
                f"**Final Recommendation**: {execution.final_recommendation}"
            ])
        
        return "\n".join(summary_parts)

# Global executor instance
ai_executor = AIWorkflowExecutor()

def execute_ai_workflow(detection_result: DetectionResult, project_root: str = ".") -> WorkflowExecution:
    """
    Main function to execute automated AI workflow
    
    This should be called after context detection to automatically execute
    the appropriate evaluation workflow.
    """
    executor = AIWorkflowExecutor(project_root)
    return executor.execute_workflow(detection_result)

# Example usage and testing
if __name__ == "__main__":
    from ai_context_detector import detect_ai_workflow_context
    
    # Test workflow execution
    test_input = "Analyze the feature/next-development branch for readiness to merge"
    current_branch = "feature/next-development"
    
    print("🤖 Testing Automated AI Workflow Execution\n")
    
    # Step 1: Context detection
    detection = detect_ai_workflow_context(test_input, current_branch)
    print(f"Detected workflow: {detection.workflow_type.value}")
    print(f"Confidence: {detection.confidence:.2f}")
    print(f"Required actions: {len(detection.required_actions)}")
    
    # Step 2: Workflow execution  
    execution = execute_ai_workflow(detection)
    
    # Step 3: Results summary
    print(f"\n{ai_executor.get_execution_summary(execution)}")