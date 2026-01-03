#!/usr/bin/env python3
"""
Test suite for AI Workflow Executor - Comprehensive coverage for all workflow functionality.

This test suite covers:
1. Core workflow execution logic
2. All refactored phase methods
3. Integration workflows
4. Error handling and edge cases
5. Evidence collection and decision making
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from pathlib import Path
import subprocess
import json

from tools.ai.ai_workflow_executor import (
    AIWorkflowExecutor, 
    WorkflowExecution, 
    WorkflowStep,
)
from tools.ai.ai_context_detector import WorkflowType, DetectionResult


class TestWorkflowDataClasses:
    """Test the dataclass definitions"""
    
    def test_workflow_step_creation(self):
        """Test WorkflowStep dataclass creation and defaults"""
        step = WorkflowStep(name="test_step", description="Test step")
        
        assert step.name == "test_step"
        assert step.description == "Test step"
        assert step.command is None
        assert step.function is None
        assert step.required is True
        assert step.completed is False
        assert step.evidence == {}
        assert step.error_message is None
    
    def test_workflow_step_with_values(self):
        """Test WorkflowStep with all values provided"""
        step = WorkflowStep(
            name="git_check",
            description="Check git status", 
            command="git status",
            required=False,
            completed=True,
            evidence={"branch": "main"},
            error_message="Test error"
        )
        
        assert step.name == "git_check"
        assert step.command == "git status"
        assert step.required is False
        assert step.completed is True
        assert step.evidence == {"branch": "main"}
        assert step.error_message == "Test error"
    
    def test_workflow_execution_creation(self):
        """Test WorkflowExecution dataclass creation and defaults"""
        start_time = datetime.now()
        execution = WorkflowExecution(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            branch_name="feature/test",
            start_time=start_time
        )
        
        assert execution.workflow_type == WorkflowType.INTEGRATION_ASSESSMENT
        assert execution.branch_name == "feature/test"
        assert execution.start_time == start_time
        assert execution.steps == []
        assert execution.completed is False
        assert execution.success is False
        assert execution.evidence_collected == {}
        assert execution.final_recommendation is None
        assert execution.end_time is None


class TestAIWorkflowExecutorInit:
    """Test AIWorkflowExecutor initialization"""
    
    def test_default_initialization(self):
        """Test default initialization"""
        executor = AIWorkflowExecutor()
        
        assert executor.project_root == Path(".")
        assert executor.execution_history == []
    
    def test_custom_project_root(self):
        """Test initialization with custom project root"""
        test_path = "/custom/path"
        executor = AIWorkflowExecutor(project_root=test_path)
        
        assert executor.project_root == Path(test_path)
        assert executor.execution_history == []


class TestWorkflowExecution:
    """Test main workflow execution logic"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
        self.detection_result = DetectionResult(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            detected_branch="feature/test",
            detected_target="main",
            confidence=0.9
        )
    
    def test_execute_workflow_integration_assessment(self):
        """Test execution of integration assessment workflow"""
        with patch.object(self.executor, '_execute_integration_assessment') as mock_assess:
            result = self.executor.execute_workflow(self.detection_result)
            
            # Verify workflow execution was called
            mock_assess.assert_called_once()
            
            # Verify execution object creation
            assert result.workflow_type == WorkflowType.INTEGRATION_ASSESSMENT
            assert result.branch_name == "feature/test"
            assert result.start_time is not None
            assert result.end_time is not None
            
            # Verify execution was added to history
            assert len(self.executor.execution_history) == 1
            assert self.executor.execution_history[0] == result
    
    def test_execute_workflow_test_validation(self):
        """Test execution of test validation workflow"""
        detection = DetectionResult(
            workflow_type=WorkflowType.TEST_VALIDATION,
            detected_branch="main",
            confidence=0.8
        )
        
        with patch.object(self.executor, '_execute_test_validation') as mock_test:
            result = self.executor.execute_workflow(detection)
            
            mock_test.assert_called_once()
            assert result.workflow_type == WorkflowType.TEST_VALIDATION
    
    def test_execute_workflow_code_analysis(self):
        """Test execution of code analysis workflow"""
        detection = DetectionResult(
            workflow_type=WorkflowType.CODE_ANALYSIS,
            detected_branch="develop",
            confidence=0.7
        )
        
        with patch.object(self.executor, '_execute_code_analysis') as mock_code:
            result = self.executor.execute_workflow(detection)
            
            mock_code.assert_called_once()
            assert result.workflow_type == WorkflowType.CODE_ANALYSIS
    
    def test_execute_workflow_unknown_type(self):
        """Test execution with unknown workflow type"""
        detection = DetectionResult(
            workflow_type=None,  # Unknown type
            detected_branch="main",
            confidence=0.5
        )
        
        result = self.executor.execute_workflow(detection)
        
        # Should complete successfully with no special workflow
        assert result.completed is True
        assert result.success is True
    
    def test_execute_workflow_exception_handling(self):
        """Test exception handling during workflow execution"""
        with patch.object(self.executor, '_execute_integration_assessment', side_effect=Exception("Test error")):
            result = self.executor.execute_workflow(self.detection_result)
            
            assert result.success is False
            assert result.error_message == "Test error"
            assert result.end_time is not None


class TestIntegrationAssessmentWorkflow:
    """Test the refactored integration assessment workflow"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
        self.execution = WorkflowExecution(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            branch_name="feature/test",
            start_time=datetime.now()
        )
        self.detection = DetectionResult(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            detected_branch="feature/test",
            detected_target="main",
            confidence=0.9
        )
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_path_validation_phase')
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_branch_detection_phase')
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_history_analysis_phase')
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_test_execution_phase')
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_e2e_validation_phase')
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_integration_decision_phase')
    def test_integration_assessment_phase_execution_order(self, mock_decision, mock_e2e, 
                                                         mock_test, mock_history, 
                                                         mock_branch, mock_path):
        """Test that all phases are executed in correct order"""
        # Set up mock return values
        mock_steps = [
            WorkflowStep("path_validation", "Path validation"),
            WorkflowStep("branch_detection", "Branch detection"),
            WorkflowStep("history_analysis", "History analysis"),
            WorkflowStep("test_execution", "Test execution"),
            WorkflowStep("e2e_validation", "E2E validation"),
            WorkflowStep("integration_decision", "Integration decision")
        ]
        
        mock_path.return_value = mock_steps[0]
        mock_branch.return_value = mock_steps[1]
        mock_history.return_value = mock_steps[2]
        mock_test.return_value = mock_steps[3]
        mock_e2e.return_value = mock_steps[4]
        mock_decision.return_value = mock_steps[5]
        
        # Execute the workflow
        self.executor._execute_integration_assessment(self.execution, self.detection)
        
        # Verify all phases were called
        mock_path.assert_called_once_with(self.execution)
        mock_branch.assert_called_once_with(self.execution, self.detection)
        mock_history.assert_called_once_with(self.execution, self.detection)
        mock_test.assert_called_once_with(self.execution)
        mock_e2e.assert_called_once_with(self.execution)
        mock_decision.assert_called_once_with(self.execution)
        
        # Verify steps were added to execution
        assert len(self.execution.steps) == 6
        assert all(step.name in ["path_validation", "branch_detection", "history_analysis", 
                                "test_execution", "e2e_validation", "integration_decision"] 
                  for step in self.execution.steps)
    
    def test_integration_assessment_completion_logic(self):
        """Test completion logic with various step completion states"""
        # Create mock steps with mixed completion states
        step1 = WorkflowStep("step1", "desc1", required=True, completed=True)
        step2 = WorkflowStep("step2", "desc2", required=True, completed=True)
        step3 = WorkflowStep("step3", "desc3", required=False, completed=False)  # Optional step
        
        self.execution.steps = [step1, step2, step3]
        
        with patch.object(self.executor, '_execute_path_validation_phase', return_value=step1), \
             patch.object(self.executor, '_execute_branch_detection_phase', return_value=step2), \
             patch.object(self.executor, '_execute_history_analysis_phase', return_value=step3), \
             patch.object(self.executor, '_execute_test_execution_phase', return_value=step1), \
             patch.object(self.executor, '_execute_e2e_validation_phase', return_value=step2), \
             patch.object(self.executor, '_execute_integration_decision_phase', return_value=step3):
            
            self.executor._execute_integration_assessment(self.execution, self.detection)
            
            # Should be completed because all required steps are completed
            assert self.execution.completed is True
            assert self.execution.success is True


class TestPhaseMethodsIndividually:
    """Test each extracted phase method individually"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
        self.execution = WorkflowExecution(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            branch_name="feature/test",
            start_time=datetime.now()
        )
        self.detection = DetectionResult(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            detected_branch="feature/test",
            detected_target="main",
            confidence=0.9
        )
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._review_documentation')
    def test_execute_path_validation_phase_success(self, mock_review):
        """Test path validation phase with successful documentation review"""
        mock_review.return_value = {
            "markdown/gemini.md": {"exists": True, "size": 1024},
            "readme.md": {"exists": True, "size": 512}
        }
        
        step = self.executor._execute_path_validation_phase(self.execution)
        
        assert step.name == "validate_paths"
        assert step.completed is True
        # Evidence now includes phase metadata
        assert "markdown/gemini.md" in step.evidence
        assert "readme.md" in step.evidence
        assert step.evidence["phase"] == "validate_paths"
        assert "collected_at" in step.evidence
        assert self.execution.evidence_collected["validate_paths_completed"] is True
        assert step.error_message is None
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._review_documentation')
    def test_execute_path_validation_phase_error(self, mock_review):
        """Test path validation phase with error"""
        mock_review.side_effect = Exception("File not found")
        
        step = self.executor._execute_path_validation_phase(self.execution)
        
        assert step.name == "validate_paths"
        assert step.completed is False
        assert "Phase 'validate_paths' failed: File not found" in step.error_message
        # Error evidence includes debug info
        assert step.evidence["phase"] == "validate_paths"
        assert step.evidence["error_type"] == "Exception"
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_command')
    def test_execute_branch_detection_phase_success(self, mock_execute):
        """Test branch detection phase with successful command execution"""
        mock_result = Mock()
        mock_result.stdout = "feature/test"
        mock_execute.return_value = mock_result
        
        step = self.executor._execute_branch_detection_phase(self.execution, self.detection)
        
        assert step.name == "detect_branch"
        assert step.completed is True
        assert step.evidence["current_branch"] == "feature/test"
        assert step.evidence["detected_branch"] == "feature/test" 
        assert step.evidence["branch_match"] is True
        assert step.evidence["phase"] == "detect_branch"
        assert self.execution.evidence_collected["detect_branch_completed"] is True
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_command')
    def test_execute_branch_detection_phase_mismatch(self, mock_execute):
        """Test branch detection with branch mismatch"""
        mock_result = Mock()
        mock_result.stdout = "main"
        mock_execute.return_value = mock_result
        
        step = self.executor._execute_branch_detection_phase(self.execution, self.detection)
        
        assert step.evidence["current_branch"] == "main"
        assert step.evidence["detected_branch"] == "feature/test"
        assert step.evidence["branch_match"] is False
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_command')
    def test_execute_history_analysis_phase(self, mock_execute):
        """Test history analysis phase"""
        mock_result = Mock()
        mock_result.stdout = "abc123 Latest commit\ndef456 Previous commit"
        mock_execute.return_value = mock_result
        
        step = self.executor._execute_history_analysis_phase(self.execution, self.detection)
        
        assert step.name == "analyze_history"
        assert step.completed is True
        assert step.evidence["commits"] == mock_result.stdout
        assert step.evidence["branch"] == "feature/test"
        assert self.execution.evidence_collected["history_analyzed"] is True
        
        # Verify correct git command was called
        expected_command = "git log --oneline -10 feature/test"
        mock_execute.assert_called_once_with(expected_command)
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_command')
    def test_execute_test_execution_phase_success(self, mock_execute):
        """Test test execution phase with successful tests"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "All tests passed"
        mock_execute.return_value = mock_result
        
        step = self.executor._execute_test_execution_phase(self.execution)
        
        assert step.name == "complete_test_execution"
        assert step.completed is True
        assert step.evidence["success"] is True
        assert step.evidence["output"] == "All tests passed"
        assert step.evidence["phase"] == "complete_test_execution"
        assert self.execution.evidence_collected["complete_test_execution_completed"] is True
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_command')
    def test_execute_test_execution_phase_failure(self, mock_execute):
        """Test test execution phase with test failures"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "2 tests failed"
        mock_execute.return_value = mock_result
        
        step = self.executor._execute_test_execution_phase(self.execution)
        
        assert step.evidence["success"] is False
        assert step.evidence["phase"] == "complete_test_execution"
        assert self.execution.evidence_collected["complete_test_execution_completed"] is True
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._check_e2e_dependencies')
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_command')
    def test_execute_e2e_validation_phase_with_dependencies(self, mock_execute, mock_check):
        """Test E2E validation phase when dependencies are available"""
        mock_check.return_value = True
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "E2E tests passed"
        mock_execute.return_value = mock_result
        
        step = self.executor._execute_e2e_validation_phase(self.execution)
        
        assert step.name == "e2e_validation"
        assert step.completed is True
        assert step.evidence["success"] is True
        assert step.evidence["dependencies_available"] is True
        assert self.execution.evidence_collected["e2e_validated"] is True
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._check_e2e_dependencies')
    def test_execute_e2e_validation_phase_no_dependencies(self, mock_check):
        """Test E2E validation phase when dependencies are not available"""
        mock_check.return_value = False
        
        step = self.executor._execute_e2e_validation_phase(self.execution)
        
        assert step.completed is True
        assert step.evidence["skipped"] is True
        assert step.evidence["dependencies_available"] is False
        assert self.execution.evidence_collected["e2e_validated"] == "skipped"
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._make_integration_decision')
    def test_execute_integration_decision_phase(self, mock_decision):
        """Test integration decision phase"""
        mock_decision.return_value = {
            "recommendation": "APPROVE",
            "confidence": 0.9,
            "reasons": ["All tests pass", "Code quality good"]
        }
        
        step = self.executor._execute_integration_decision_phase(self.execution)
        
        assert step.name == "integration_decision"
        assert step.completed is True
        assert step.evidence == mock_decision.return_value
        assert self.execution.final_recommendation == "APPROVE"
        assert self.execution.evidence_collected["decision_made"] is True


class TestCommandExecution:
    """Test command execution functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
    
    @patch('subprocess.run')
    def test_execute_command_success(self, mock_run):
        """Test successful command execution"""
        mock_result = Mock()
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = self.executor._execute_command("git status")
        
        assert result == mock_result
        mock_run.assert_called_once_with(
            "git status",
            shell=True,
            cwd=Path("C:/temp/Python"),
            capture_output=True,
            text=True,
            timeout=60
        )
    
    @patch('subprocess.run')
    def test_execute_command_timeout(self, mock_run):
        """Test command execution with timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("git status", 60)
        
        with pytest.raises(subprocess.TimeoutExpired):
            self.executor._execute_command("git status")


class TestUtilityMethods:
    """Test utility methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_review_documentation_all_files_exist(self, mock_stat, mock_exists):
        """Test documentation review when all files exist"""
        mock_exists.return_value = True
        
        # Mock file stats
        mock_stat_obj = Mock()
        mock_stat_obj.st_size = 1024
        mock_stat_obj.st_mtime = 1625097600.0
        mock_stat.return_value = mock_stat_obj
        
        result = self.executor._review_documentation()
        
        expected_files = ["markdown/gemini.md", "readme.md", "markdown/code_evaluation_standards.md"]
        for file_key in expected_files:
            assert file_key in result
            assert result[file_key]["exists"] is True
            assert result[file_key]["size"] == 1024
            assert result[file_key]["modified"] == 1625097600.0
    
    @patch('pathlib.Path.exists')
    def test_review_documentation_files_missing(self, mock_exists):
        """Test documentation review when files are missing"""
        mock_exists.return_value = False
        
        result = self.executor._review_documentation()
        
        expected_files = ["markdown/gemini.md", "readme.md", "markdown/code_evaluation_standards.md"]
        for file_key in expected_files:
            assert file_key in result
            assert result[file_key]["exists"] is False


class TestTestValidationWorkflow:
    """Test test validation workflow"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
        self.execution = WorkflowExecution(
            workflow_type=WorkflowType.TEST_VALIDATION,
            branch_name="main",
            start_time=datetime.now()
        )
        self.detection = DetectionResult(
            workflow_type=WorkflowType.TEST_VALIDATION,
            detected_branch="main",
            confidence=0.8
        )
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._verify_test_dependencies')
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_command')
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._assess_system_readiness')
    def test_test_validation_workflow_success(self, mock_assess, mock_execute, mock_verify):
        """Test successful test validation workflow"""
        # Mock dependencies check
        mock_verify.return_value = {"test_data": True, "config": True}
        
        # Mock test execution
        mock_result = Mock()
        mock_result.stdout = "Tests passed"
        mock_result.returncode = 0
        mock_execute.return_value = mock_result
        
        # Mock system readiness assessment
        mock_assess.return_value = {"readiness": "READY"}
        
        self.executor._execute_test_validation(self.execution, self.detection)
        
        # Verify all steps were executed
        assert len(self.execution.steps) == 3
        assert self.execution.steps[0].name == "verify_dependencies"
        assert self.execution.steps[1].name == "execute_test_pyramid"
        assert self.execution.steps[2].name == "assess_system_readiness"
        
        # Verify completion
        assert self.execution.completed is True
        assert self.execution.success is True
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._verify_test_dependencies')
    def test_test_validation_dependency_error(self, mock_verify):
        """Test test validation with dependency verification error"""
        mock_verify.side_effect = Exception("Dependencies not found")
        
        self.executor._execute_test_validation(self.execution, self.detection)
        
        # First step should have error
        assert len(self.execution.steps) >= 1
        assert self.execution.steps[0].error_message == "Dependencies not found"


class TestCodeAnalysisWorkflow:
    """Test code analysis workflow"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
        self.execution = WorkflowExecution(
            workflow_type=WorkflowType.CODE_ANALYSIS,
            branch_name="develop",
            start_time=datetime.now()
        )
        self.detection = DetectionResult(
            workflow_type=WorkflowType.CODE_ANALYSIS,
            detected_branch="develop",
            confidence=0.7
        )
    
    @patch('tools.ai.ai_workflow_executor.AIWorkflowExecutor._execute_command')
    def test_code_analysis_workflow(self, mock_execute):
        """Test code analysis workflow execution"""
        # Mock git analysis
        git_result = Mock()
        git_result.stdout = "abc123 Latest commit"
        git_result.returncode = 0
        
        # Mock quality check
        quality_result = Mock()
        quality_result.stdout = "Quality checks passed"
        quality_result.returncode = 0
        
        mock_execute.side_effect = [git_result, quality_result]
        
        self.executor._execute_code_analysis(self.execution, self.detection)
        
        # Verify steps
        assert len(self.execution.steps) == 2
        assert self.execution.steps[0].name == "git_analysis"
        assert self.execution.steps[1].name == "quality_check"
        
        # Verify completion
        assert self.execution.completed is True
        assert self.execution.success is True


class TestDependencyAndUtilityMethods:
    """Test dependency verification and utility methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
    
    @patch('pathlib.Path.exists')
    def test_verify_test_dependencies_all_exist(self, mock_exists):
        """Test dependency verification when all dependencies exist"""
        mock_exists.return_value = True
        
        result = self.executor._verify_test_dependencies()
        
        assert result["test_data"] is True
        assert result["config"] is True
        assert result["test_runner"] is True
    
    @patch('pathlib.Path.exists')
    def test_verify_test_dependencies_missing(self, mock_exists):
        """Test dependency verification with missing dependencies"""
        mock_exists.return_value = False
        
        result = self.executor._verify_test_dependencies()
        
        assert result["test_data"] is False
        assert result["config"] is False  
        assert result["test_runner"] is False
    
    @patch('pathlib.Path.exists')
    def test_check_e2e_dependencies_available(self, mock_exists):
        """Test E2E dependency check when available"""
        mock_exists.return_value = True
        
        result = self.executor._check_e2e_dependencies()
        
        assert result is True
    
    @patch('pathlib.Path.exists')
    def test_check_e2e_dependencies_missing(self, mock_exists):
        """Test E2E dependency check when missing"""
        mock_exists.return_value = False
        
        result = self.executor._check_e2e_dependencies()
        
        assert result is False
    
    def test_make_integration_decision_all_evidence_positive(self):
        """Test integration decision with positive evidence"""
        execution = WorkflowExecution(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            branch_name="feature/test",
            start_time=datetime.now()
        )
        execution.evidence_collected = {
            "documentation_reviewed": True,
            "branch_detected": True,
            "history_analyzed": True,
            "tests_executed": True,
            "e2e_validated": True,
            "decision_made": True
        }
        
        result = self.executor._make_integration_decision(execution)
        
        assert result["recommendation"] == "READY"
        assert result["confidence"] == "HIGH"
        assert "evidence_summary" in result
        assert len(result["missing_requirements"]) == 0
    
    def test_make_integration_decision_mixed_evidence(self):
        """Test integration decision with mixed evidence"""
        execution = WorkflowExecution(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            branch_name="feature/test",
            start_time=datetime.now()
        )
        execution.evidence_collected = {
            "documentation_reviewed": True,
            "branch_detected": True,
            "history_analyzed": True,
            "tests_executed": False,  # Tests failed
            "e2e_validated": "skipped",
            "decision_made": False
        }
        
        result = self.executor._make_integration_decision(execution)
        
        assert result["recommendation"] == "NOT_READY"
        assert result["confidence"] in ["LOW", "MEDIUM"]
        assert len(result["missing_requirements"]) > 0
        
    def test_assess_system_readiness(self):
        """Test system readiness assessment"""
        execution = WorkflowExecution(
            workflow_type=WorkflowType.TEST_VALIDATION,
            branch_name="main",
            start_time=datetime.now()
        )
        
        # Add mock steps with test evidence
        execution.steps = [
            WorkflowStep("test_step1", "Test desc1", completed=True, evidence={"success": True}),
            WorkflowStep("test_step2", "Test desc2", completed=True, evidence={"success": True})
        ]
        
        result = self.executor._assess_system_readiness(execution)
        
        assert "readiness" in result
        assert "test_evidence" in result
        assert "all_tests_passed" in result
        assert result["readiness"] == "READY"
        assert result["all_tests_passed"] is True


class TestExecutionHistoryAndSummary:
    """Test execution history and summary functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
    
    def test_execution_history_tracking(self):
        """Test that executions are added to history"""
        detection = DetectionResult(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            detected_branch="test",
            confidence=0.9
        )
        
        # Execute workflow multiple times
        with patch.object(self.executor, '_execute_integration_assessment'):
            result1 = self.executor.execute_workflow(detection)
            result2 = self.executor.execute_workflow(detection)
        
        assert len(self.executor.execution_history) == 2
        assert self.executor.execution_history[0] == result1
        assert self.executor.execution_history[1] == result2
    
    def test_get_execution_summary(self):
        """Test execution summary generation"""
        # Create a mock execution with proper timing
        start_time = datetime.now()
        end_time = start_time
        
        execution = WorkflowExecution(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            branch_name="feature/1",
            start_time=start_time,
            completed=True,
            success=True,
            end_time=end_time
        )
        
        # Add some steps
        execution.steps = [
            WorkflowStep("step1", "First step", completed=True),
            WorkflowStep("step2", "Second step", completed=True)
        ]
        execution.final_recommendation = "READY"
        
        summary = self.executor.get_execution_summary(execution)
        
        # Check that summary is a string with expected content
        assert isinstance(summary, str)
        assert "Integration Assessment Complete" in summary
        assert "feature/1" in summary
        assert "SUCCESS" in summary
        assert "First step" in summary
        assert "Second step" in summary
        assert "READY" in summary


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.executor = AIWorkflowExecutor(project_root="C:/temp/Python")
    
    def test_phase_method_error_handling(self):
        """Test that phase methods handle errors gracefully"""
        execution = WorkflowExecution(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            branch_name="test",
            start_time=datetime.now()
        )
        
        with patch.object(self.executor, '_review_documentation', side_effect=Exception("Test error")):
            step = self.executor._execute_path_validation_phase(execution)
            
            assert step.completed is False
            assert "Phase 'validate_paths' failed: Test error" in step.error_message
            assert step.evidence["error_type"] == "Exception"
            assert "validate_paths_completed" not in execution.evidence_collected
    
    def test_integration_assessment_with_step_errors(self):
        """Test integration assessment when some steps have errors"""
        execution = WorkflowExecution(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            branch_name="test",
            start_time=datetime.now()
        )
        detection = DetectionResult(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            detected_branch="test",
            confidence=0.8
        )
        
        # Mock phase methods - some succeed, some fail
        successful_step = WorkflowStep("success", "Success", completed=True, required=True)
        failed_step = WorkflowStep("failure", "Failure", completed=False, 
                                 error_message="Error", required=True)
        
        with patch.object(self.executor, '_execute_path_validation_phase', return_value=successful_step), \
             patch.object(self.executor, '_execute_branch_detection_phase', return_value=failed_step), \
             patch.object(self.executor, '_execute_history_analysis_phase', return_value=successful_step), \
             patch.object(self.executor, '_execute_test_execution_phase', return_value=successful_step), \
             patch.object(self.executor, '_execute_e2e_validation_phase', return_value=successful_step), \
             patch.object(self.executor, '_execute_integration_decision_phase', return_value=successful_step):
            
            self.executor._execute_integration_assessment(execution, detection)
            
            # Should not be completed because a required step failed
            assert execution.completed is False
            assert execution.success is False
    
    def test_command_execution_with_various_errors(self):
        """Test command execution with various error conditions"""
        with patch('subprocess.run', side_effect=FileNotFoundError("Command not found")):
            with pytest.raises(FileNotFoundError):
                self.executor._execute_command("nonexistent_command")
        
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd")):
            with pytest.raises(subprocess.CalledProcessError):
                self.executor._execute_command("failing_command")
    
    def test_empty_detection_result(self):
        """Test workflow execution with minimal detection result"""
        detection = DetectionResult(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            detected_branch=None,  # No branch detected
            confidence=0.1  # Low confidence
        )
        
        with patch.object(self.executor, '_execute_integration_assessment') as mock_assess:
            result = self.executor.execute_workflow(detection)
            
            mock_assess.assert_called_once()
            assert result.branch_name is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])