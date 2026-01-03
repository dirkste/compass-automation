#!/usr/bin/env python3
"""
AI Context Detector - Automatically detects workflow contexts from user input.

This module provides automatic detection of evaluation workflows that should
be executed based on user requests and current git context.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import re


class WorkflowType(Enum):
    """Types of automated workflows that can be executed"""
    INTEGRATION_ASSESSMENT = "integration_assessment"
    TEST_VALIDATION = "test_validation" 
    CODE_ANALYSIS = "code_analysis"


@dataclass
class DetectionResult:
    """Result of workflow context detection"""
    workflow_type: WorkflowType
    detected_branch: Optional[str] = None
    detected_target: Optional[str] = None
    confidence: float = 0.0
    required_actions: List[str] = None
    
    def __post_init__(self):
        if self.required_actions is None:
            self.required_actions = []


class AIContextDetector:
    """Detects workflow context from user input and git state"""
    
    # Context detection patterns
    INTEGRATION_TRIGGERS = [
        "ready to merge", "integrate branch", "merge to main", "merge",
        "analyze branch", "evaluate branch", "branch readiness", 
        "integration assessment", "ready for production",
        "merge readiness", "integration readiness", "analyze"
    ]
    
    TEST_TRIGGERS = [
        "run tests", "test the system", "validate functionality", "tests",
        "E2E test", "end-to-end validation", "test workflow", "test",
        "validate system", "test validation", "run test suite",
        "comprehensive tests", "execute test"
    ]
    
    ANALYSIS_TRIGGERS = [
        "examine branches", "branch analysis", "review changes", "review",
        "assess branch", "code review", "quality check", "changes",
        "code analysis", "analyze code", "review commits", "examine"
    ]
    
    def detect_workflow_context(self, user_input: str, current_branch: Optional[str] = None) -> DetectionResult:
        """
        Detect the appropriate workflow type from user input.
        
        Args:
            user_input: The user's request/input
            current_branch: Current git branch (optional)
            
        Returns:
            DetectionResult with detected workflow and confidence
        """
        input_lower = user_input.lower()
        
        # Check for integration assessment triggers
        integration_confidence = self._calculate_confidence(input_lower, self.INTEGRATION_TRIGGERS)
        test_confidence = self._calculate_confidence(input_lower, self.TEST_TRIGGERS) 
        analysis_confidence = self._calculate_confidence(input_lower, self.ANALYSIS_TRIGGERS)
        
        # Determine highest confidence workflow
        confidences = {
            WorkflowType.INTEGRATION_ASSESSMENT: integration_confidence,
            WorkflowType.TEST_VALIDATION: test_confidence,
            WorkflowType.CODE_ANALYSIS: analysis_confidence
        }
        
        # Find workflow with highest confidence
        workflow_type = max(confidences.items(), key=lambda x: x[1])
        
        # If all confidences are 0, default to integration assessment
        if workflow_type[1] == 0.0:
            workflow_type = (WorkflowType.INTEGRATION_ASSESSMENT, 0.0)
        
        # Extract branch information from input, fallback to current_branch
        detected_branch = self._extract_branch_from_input(user_input)
        if not detected_branch and current_branch:
            detected_branch = current_branch
        detected_target = self._extract_target_branch(user_input)
        
        return DetectionResult(
            workflow_type=workflow_type[0],
            detected_branch=detected_branch,
            detected_target=detected_target, 
            confidence=workflow_type[1],
            required_actions=self._get_required_actions(workflow_type[0])
        )
    
    def _calculate_confidence(self, input_text: str, triggers: List[str]) -> float:
        """Calculate confidence score for a set of trigger phrases"""
        matches = sum(1 for trigger in triggers if trigger in input_text)
        if matches == 0:
            return 0.0
        # Base confidence from match ratio, plus bonus for multiple matches
        base_confidence = matches / len(triggers)
        bonus = min(matches * 0.1, 0.5)  # Cap bonus at 0.5
        return min(base_confidence + bonus, 1.0)
    
    def _extract_branch_from_input(self, input_text: str) -> Optional[str]:
        """Extract branch name from user input using common patterns"""
        # Look for common branch patterns
        patterns = [
            r'(feature/[a-zA-Z0-9/_-]+)',
            r'(hotfix/[a-zA-Z0-9/_-]+)', 
            r'(release/[a-zA-Z0-9/_.-]+)',
            r'branch[:\s]+([a-zA-Z][a-zA-Z0-9/_-]{2,})',
            r'([a-zA-Z][a-zA-Z0-9/_-]{2,})\s+branch',
            r'\b(develop)\b',
            r'\b(main)\b', 
            r'\b(master)\b'
        ]
        
        for pattern in patterns:
            if match := re.search(pattern, input_text, re.IGNORECASE):
                return match.group(1)
        
        return None
    
    def _extract_target_branch(self, input_text: str) -> str:
        """Extract target branch for merging"""
        # Look for merge target patterns - be more specific
        merge_patterns = [
            r'merge\s+(?:to|into)\s+(main|master|develop|development)',
            r'(?:to|into)\s+(main|master|develop|development)',
            r'merge\s+(main|master|develop|development)'
        ]
        
        for pattern in merge_patterns:
            if match := re.search(pattern, input_text, re.IGNORECASE):
                return match.group(1)
        
        return "main"  # Default target
    
    def _get_required_actions(self, workflow_type: WorkflowType) -> List[str]:
        """Get required actions for each workflow type"""
        action_map = {
            WorkflowType.INTEGRATION_ASSESSMENT: [
                "review_documentation",
                "analyze_git_history", 
                "execute_tests",
                "validate_e2e",
                "make_decision"
            ],
            WorkflowType.TEST_VALIDATION: [
                "verify_dependencies",
                "execute_test_pyramid",
                "assess_readiness"
            ],
            WorkflowType.CODE_ANALYSIS: [
                "analyze_git_history",
                "execute_quality_checks"
            ]
        }
        
        return action_map.get(workflow_type, [])


# Global detector instance
context_detector = AIContextDetector()


def detect_ai_workflow_context(user_input: str, current_branch: Optional[str] = None) -> DetectionResult:
    """
    Main function to detect workflow context from user input.
    
    Args:
        user_input: The user's request/input
        current_branch: Current git branch (optional)
        
    Returns:
        DetectionResult with detected workflow and metadata
    """
    return context_detector.detect_workflow_context(user_input, current_branch)


# Example usage and testing
if __name__ == "__main__":
    # Test context detection
    test_cases = [
        "Analyze the feature/next-development branch for readiness to merge",
        "Run tests to validate the system", 
        "Review the changes in the develop branch",
        "Is this branch ready to merge to main?",
        "Execute end-to-end validation"
    ]
    
    print("🤖 Testing AI Context Detection\n")
    
    for test_input in test_cases:
        detection = detect_ai_workflow_context(test_input)
        print(f"Input: '{test_input}'")
        print(f"→ Workflow: {detection.workflow_type.value}")
        print(f"→ Confidence: {detection.confidence:.2f}")
        print(f"→ Branch: {detection.detected_branch}")
        print(f"→ Target: {detection.detected_target}")
        print()