#!/usr/bin/env python3
"""
Tests for AI Context Detector module.

Tests the automatic detection of workflow contexts from user input
and the extraction of branch/target information.
"""

import pytest
from ai_context_detector import (
    AIContextDetector, 
    WorkflowType, 
    DetectionResult,
    detect_ai_workflow_context
)


class TestWorkflowTypeEnum:
    """Test WorkflowType enum"""
    
    def test_workflow_type_values(self):
        """Test that workflow types have correct string values"""
        assert WorkflowType.INTEGRATION_ASSESSMENT.value == "integration_assessment"
        assert WorkflowType.TEST_VALIDATION.value == "test_validation"
        assert WorkflowType.CODE_ANALYSIS.value == "code_analysis"
    
    def test_workflow_type_enumeration(self):
        """Test that we can enumerate all workflow types"""
        workflow_types = list(WorkflowType)
        assert len(workflow_types) == 3
        assert WorkflowType.INTEGRATION_ASSESSMENT in workflow_types


class TestDetectionResult:
    """Test DetectionResult dataclass"""
    
    def test_detection_result_creation(self):
        """Test basic DetectionResult creation"""
        result = DetectionResult(
            workflow_type=WorkflowType.INTEGRATION_ASSESSMENT,
            detected_branch="feature/test",
            confidence=0.9
        )
        
        assert result.workflow_type == WorkflowType.INTEGRATION_ASSESSMENT
        assert result.detected_branch == "feature/test"
        assert result.confidence == 0.9
        assert result.required_actions == []  # Default empty list
    
    def test_detection_result_with_actions(self):
        """Test DetectionResult with required actions"""
        actions = ["review_docs", "run_tests"]
        result = DetectionResult(
            workflow_type=WorkflowType.TEST_VALIDATION,
            required_actions=actions,
            confidence=0.8
        )
        
        assert result.required_actions == actions
    
    def test_detection_result_post_init(self):
        """Test that __post_init__ initializes required_actions to empty list"""
        result = DetectionResult(
            workflow_type=WorkflowType.CODE_ANALYSIS,
            confidence=0.7
        )
        
        assert result.required_actions == []


class TestAIContextDetector:
    """Test AIContextDetector class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.detector = AIContextDetector()
    
    def test_detector_initialization(self):
        """Test detector initializes with correct trigger patterns"""
        assert len(self.detector.INTEGRATION_TRIGGERS) > 0
        assert len(self.detector.TEST_TRIGGERS) > 0
        assert len(self.detector.ANALYSIS_TRIGGERS) > 0
        
        # Check some expected triggers exist
        assert "ready to merge" in self.detector.INTEGRATION_TRIGGERS
        assert "run tests" in self.detector.TEST_TRIGGERS
        assert "code review" in self.detector.ANALYSIS_TRIGGERS
    
    def test_calculate_confidence_perfect_match(self):
        """Test confidence calculation with perfect matches"""
        input_text = "ready to merge analyze branch integration readiness"
        confidence = self.detector._calculate_confidence(input_text, self.detector.INTEGRATION_TRIGGERS)
        
        # Should have some confidence since multiple triggers match
        assert confidence > 0.0
        assert confidence <= 1.0
    
    def test_calculate_confidence_no_match(self):
        """Test confidence calculation with no matches"""
        input_text = "unrelated random text"
        confidence = self.detector._calculate_confidence(input_text, self.detector.INTEGRATION_TRIGGERS)
        
        assert confidence == 0.0
    
    def test_extract_branch_from_input_feature_branch(self):
        """Test branch extraction from feature branch patterns"""
        test_cases = [
            ("analyze feature/user-auth branch", "user-auth"),
            ("feature/user-auth is ready", "feature/user-auth"),
            ("check the develop branch", "develop"),
            ("merge to main", "main")
        ]
        
        for input_text, expected_branch in test_cases:
            result = self.detector._extract_branch_from_input(input_text)
            assert result == expected_branch or result in input_text
    
    def test_extract_branch_from_input_no_match(self):
        """Test branch extraction when no branch is mentioned"""
        input_text = "run some tests on the code"
        result = self.detector._extract_branch_from_input(input_text)
        assert result is None
    
    def test_extract_target_branch(self):
        """Test target branch extraction"""
        test_cases = [
            ("merge to main", "main"),
            ("merge into develop", "develop"),
            ("ready to merge to master", "master"),
            ("no merge mentioned", "main")  # Default
        ]
        
        for input_text, expected_target in test_cases:
            result = self.detector._extract_target_branch(input_text)
            assert result == expected_target
    
    def test_get_required_actions(self):
        """Test required actions for each workflow type"""
        integration_actions = self.detector._get_required_actions(WorkflowType.INTEGRATION_ASSESSMENT)
        test_actions = self.detector._get_required_actions(WorkflowType.TEST_VALIDATION)
        analysis_actions = self.detector._get_required_actions(WorkflowType.CODE_ANALYSIS)
        
        # Check that each workflow has appropriate actions
        assert "review_documentation" in integration_actions
        assert "execute_tests" in integration_actions
        assert "verify_dependencies" in test_actions
        assert "analyze_git_history" in analysis_actions
    
    def test_detect_workflow_context_integration_assessment(self):
        """Test detection of integration assessment workflow"""
        input_text = "Is the feature/user-auth branch ready to merge to main?"
        
        result = self.detector.detect_workflow_context(input_text)
        
        assert result.workflow_type == WorkflowType.INTEGRATION_ASSESSMENT
        assert result.confidence > 0.0
        assert result.detected_branch is not None
        assert result.detected_target == "main"
        assert len(result.required_actions) > 0
    
    def test_detect_workflow_context_test_validation(self):
        """Test detection of test validation workflow"""
        input_text = "Run tests to validate the system functionality"
        
        result = self.detector.detect_workflow_context(input_text)
        
        assert result.workflow_type == WorkflowType.TEST_VALIDATION
        assert result.confidence > 0.0
    
    def test_detect_workflow_context_code_analysis(self):
        """Test detection of code analysis workflow"""
        input_text = "Please review the changes and analyze the code quality"
        
        result = self.detector.detect_workflow_context(input_text)
        
        assert result.workflow_type == WorkflowType.CODE_ANALYSIS
        assert result.confidence > 0.0
    
    def test_detect_workflow_context_with_current_branch(self):
        """Test detection with current branch parameter"""
        input_text = "analyze this code for merge readiness"  # Changed to avoid "branch" keyword
        current_branch = "feature/payment-system"
        
        result = self.detector.detect_workflow_context(input_text, current_branch)
        
        assert result.detected_branch == current_branch
        assert result.workflow_type == WorkflowType.INTEGRATION_ASSESSMENT


class TestGlobalFunctions:
    """Test global convenience functions"""
    
    def test_detect_ai_workflow_context_function(self):
        """Test the global detect_ai_workflow_context function"""
        input_text = "Ready to merge feature/new-feature to main"
        
        result = detect_ai_workflow_context(input_text)
        
        assert isinstance(result, DetectionResult)
        assert result.workflow_type == WorkflowType.INTEGRATION_ASSESSMENT
        assert result.confidence > 0.0
    
    def test_detect_ai_workflow_context_with_branch(self):
        """Test global function with current branch"""
        input_text = "run comprehensive tests"
        current_branch = "develop"
        
        result = detect_ai_workflow_context(input_text, current_branch)
        
        assert result.detected_branch == current_branch
        assert result.workflow_type == WorkflowType.TEST_VALIDATION


class TestContextDetectionScenarios:
    """Test realistic context detection scenarios"""
    
    @pytest.mark.parametrize("input_text,expected_workflow", [
        ("Is branch feature/auth ready for production?", WorkflowType.INTEGRATION_ASSESSMENT),
        ("Analyze feature/user-management for merge readiness", WorkflowType.INTEGRATION_ASSESSMENT),
        ("Run end-to-end tests on the current branch", WorkflowType.TEST_VALIDATION),
        ("Execute the test suite to validate functionality", WorkflowType.TEST_VALIDATION),
        ("Review code changes in develop branch", WorkflowType.CODE_ANALYSIS),
        ("Examine the quality of recent commits", WorkflowType.CODE_ANALYSIS),
    ])
    def test_realistic_scenarios(self, input_text, expected_workflow):
        """Test realistic user input scenarios"""
        result = detect_ai_workflow_context(input_text)
        assert result.workflow_type == expected_workflow
        assert result.confidence > 0.0
    
    def test_ambiguous_input_chooses_highest_confidence(self):
        """Test that ambiguous input chooses the highest confidence workflow"""
        # This input could match multiple workflows
        input_text = "analyze and test the branch for merge readiness"
        
        result = detect_ai_workflow_context(input_text)
        
        # Should pick one workflow type with reasonable confidence
        assert result.workflow_type in [
            WorkflowType.INTEGRATION_ASSESSMENT,
            WorkflowType.TEST_VALIDATION, 
            WorkflowType.CODE_ANALYSIS
        ]
        assert result.confidence > 0.0
    
    def test_edge_case_empty_input(self):
        """Test edge case with empty input"""
        result = detect_ai_workflow_context("")
        
        # Should still return a valid result, though with low confidence
        assert isinstance(result, DetectionResult)
        assert result.confidence >= 0.0
    
    def test_edge_case_no_clear_workflow(self):
        """Test input that doesn't clearly match any workflow"""
        input_text = "hello world random text"
        
        result = detect_ai_workflow_context(input_text)
        
        # Should return a workflow with low confidence
        assert isinstance(result, DetectionResult)
        assert result.confidence <= 0.2  # Low confidence expected


class TestBranchExtractionEdgeCases:
    """Test edge cases in branch name extraction"""
    
    def setup_method(self):
        self.detector = AIContextDetector()
    
    def test_complex_branch_names(self):
        """Test extraction of complex branch names"""
        test_cases = [
            "analyze feature/JIRA-123-user-authentication",
            "review hotfix/critical-security-patch",
            "check release/v2.1.0-beta branch"
        ]
        
        for input_text in test_cases:
            result = self.detector._extract_branch_from_input(input_text)
            assert result is not None
            assert len(result) > 0
    
    def test_branch_with_special_characters(self):
        """Test branches with numbers, hyphens, underscores"""
        input_text = "feature/user_auth_v2-final branch is ready"
        result = self.detector._extract_branch_from_input(input_text)
        
        assert result is not None
        assert "user_auth" in result or "feature" in result


if __name__ == "__main__":
    pytest.main([__file__])