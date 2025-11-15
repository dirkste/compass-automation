# AI Standard Operating Procedure (SOP) Automation

This document defines automated triggers and workflows that ensure the AI follows proper evaluation standards and procedures without requiring human instruction.

## 🎯 Automation Objectives

### **Primary Goal**: Create automatic AI behavior that:
1. **Detects evaluation contexts** automatically based on user requests and code state
2. **Triggers proper evaluation workflows** without human prompting
3. **Validates completion** of required steps before proceeding
4. **Prevents procedural errors** through automated safeguards

### **Human Experience**: Users can simply say "analyze the branch" and AI will automatically:
- Generate evaluation checklist
- Execute complete validation process
- Follow all documented standards
- Provide evidence-based recommendations

## 🤖 Automated Trigger System

### **Context Detection Rules**

The AI should automatically detect and respond to these scenarios:

#### **1. Integration/Merge Requests**
**Trigger Keywords**: 
- "ready to merge", "integrate branch", "merge to main"
- "analyze branch", "evaluate branch", "branch readiness"
- "integration assessment", "ready for production"

**Automatic AI Actions**:
```bash
# AI automatically executes:
1. Generate evaluation checklist: `python generate_evaluation.py <detected-branch>`
2. Execute comprehensive validation workflow
3. Document all findings with evidence
4. Provide READY/NOT READY recommendation with supporting evidence
```

#### **2. Branch Analysis Requests**
**Trigger Keywords**:
- "examine branches", "branch analysis", "what's in this branch"
- "review changes", "assess branch", "branch status"

**Automatic AI Actions**:
```bash
# AI automatically executes:
1. Review git history and changes
2. Check documentation for requirements 
3. Execute relevant test suites
4. Generate risk assessment
5. Provide evidence-based analysis
```

#### **3. Testing Validation Requests**
**Trigger Keywords**:
- "run tests", "test the system", "validate functionality"
- "E2E test", "end-to-end validation", "test workflow"

**Automatic AI Actions**:
```bash
# AI automatically executes:
1. Check all test dependencies (data, config, environment)
2. Execute complete test pyramid (unit → integration → E2E)
3. Validate full workflow completion (not just setup)
4. Document test evidence and any failures
5. Assess system readiness based on test results
```

#### **4. Code Quality Assessment**
**Trigger Keywords**:
- "code review", "quality check", "assess code changes"
- "evaluate implementation", "review commits"

**Automatic AI Actions**:
```bash
# AI automatically executes:
1. Review coding standards compliance
2. Check for breaking changes
3. Validate configuration compatibility
4. Execute quality gates (tests, linting, etc.)
5. Generate comprehensive quality report
```

## 📋 Automated Workflow Templates

### **Template 1: Branch Integration Assessment**

```markdown
## AUTOMATIC AI WORKFLOW: Branch Integration Assessment

**Detected Context**: User mentioned "<<trigger_keywords>>" for branch "<<branch_name>>"

### Phase 1: Automatic Preparation
- [ ] Generate evaluation checklist: `python generate_evaluation.py <<branch_name>>`
- [ ] Review GEMINI.md for project requirements
- [ ] Check git history: `git log --oneline <<branch_name>>`
- [ ] Identify test dependencies and data requirements

### Phase 2: Documentation Analysis  
- [ ] Read project documentation (GEMINI.md, README files)
- [ ] Review test expectations and setup requirements
- [ ] Check configuration dependencies
- [ ] Understand complete workflow requirements

### Phase 3: Test Execution & Validation
- [ ] Execute unit tests: `python run_tests.py`
- [ ] Execute integration tests with environment validation
- [ ] **CRITICAL**: Execute complete E2E tests with full workflow validation
- [ ] Verify all test data dependencies available

### Phase 4: Evidence Collection
- [ ] Document all test results with output evidence
- [ ] Record configuration validation results  
- [ ] Capture complete E2E workflow execution logs
- [ ] Assess version compatibility and system requirements

### Phase 5: Integration Readiness Decision
- [ ] Apply integration readiness criteria from CODE_EVALUATION_STANDARDS.md
- [ ] Provide READY/NOT READY/INVESTIGATION recommendation
- [ ] List specific evidence supporting decision
- [ ] Document any remaining blockers or requirements

**AI Completion Validation**: All phases must be completed before providing recommendation
```

### **Template 2: Automated Test Validation**

```markdown
## AUTOMATIC AI WORKFLOW: Test Validation

**Detected Context**: User requested testing for "<<component/system>>"

### Phase 1: Dependency Verification
- [ ] Check test data availability (data/mva.csv, config files)
- [ ] Verify environment setup (browser/driver versions)
- [ ] Validate configuration files present and accessible
- [ ] Confirm Python environment and package dependencies

### Phase 2: Test Pyramid Execution
- [ ] Unit Tests: Execute and validate component isolation
- [ ] Integration Tests: Verify system configuration and compatibility
- [ ] E2E Tests: **MUST complete entire business workflow**

### Phase 3: Evidence Documentation
- [ ] Capture all test execution output
- [ ] Document any failures with root cause analysis
- [ ] Record environmental validation results
- [ ] Verify complete workflow success (not just setup)

### Phase 4: System Readiness Assessment
- [ ] Assess test results against acceptance criteria
- [ ] Identify any blockers or missing dependencies
- [ ] Provide evidence-based readiness conclusion

**AI Completion Validation**: All tests must be executed and evidence collected
```

## 🔧 Implementation Mechanisms

### **1. Context Detection Engine**

```python
# AI_CONTEXT_DETECTOR.py - Automated context recognition
class AIContextDetector:
    
    INTEGRATION_TRIGGERS = [
        "ready to merge", "integrate branch", "merge to main",
        "analyze branch", "evaluate branch", "branch readiness",
        "integration assessment", "ready for production"
    ]
    
    TESTING_TRIGGERS = [
        "run tests", "test the system", "validate functionality", 
        "E2E test", "end-to-end validation", "test workflow"
    ]
    
    ANALYSIS_TRIGGERS = [
        "examine branches", "branch analysis", "review changes",
        "assess branch", "code review", "quality check"
    ]
    
    def detect_context(self, user_input: str) -> str:
        """Automatically detect required workflow based on user input"""
        input_lower = user_input.lower()
        
        if any(trigger in input_lower for trigger in self.INTEGRATION_TRIGGERS):
            return "INTEGRATION_ASSESSMENT"
        elif any(trigger in input_lower for trigger in self.TESTING_TRIGGERS):
            return "TEST_VALIDATION" 
        elif any(trigger in input_lower for trigger in self.ANALYSIS_TRIGGERS):
            return "CODE_ANALYSIS"
        else:
            return "STANDARD_RESPONSE"
```

### **2. Workflow Execution Engine**

```python
# AI_WORKFLOW_EXECUTOR.py - Automated workflow execution
class AIWorkflowExecutor:
    
    def execute_integration_assessment(self, branch_name: str):
        """Automatically execute complete integration assessment"""
        
        # Phase 1: Generate evaluation
        self.generate_evaluation_checklist(branch_name)
        
        # Phase 2: Documentation review
        self.review_documentation()
        
        # Phase 3: Test execution
        self.execute_test_pyramid()
        
        # Phase 4: Evidence collection
        self.collect_evidence()
        
        # Phase 5: Decision with validation
        return self.make_integration_decision()
    
    def validate_completion(self, workflow_type: str) -> bool:
        """Ensure all required steps completed before proceeding"""
        # Validation logic to prevent incomplete workflows
        pass
```

### **3. Validation Checkpoints**

```python
# AI_VALIDATION_GATES.py - Automated validation gates
class AIValidationGates:
    
    def validate_integration_workflow(self, workflow_data: dict) -> bool:
        """Validate integration assessment completion"""
        required_evidence = [
            'documentation_review_completed',
            'unit_tests_executed', 
            'integration_tests_executed',
            'e2e_tests_completed_full_workflow',
            'evidence_collected',
            'decision_supported_by_evidence'
        ]
        
        return all(workflow_data.get(item) for item in required_evidence)
    
    def block_incomplete_recommendations(self, assessment: dict) -> bool:
        """Prevent recommendations without proper validation"""
        if assessment.get('recommendation') and not self.validate_integration_workflow(assessment):
            raise ValueError("Cannot make recommendation without completing full evaluation workflow")
        return True
```

## 🚦 Automated Safety Mechanisms

### **1. Completion Validation Gates**

Before the AI can provide any integration recommendation:
- ✅ **Documentation Review Gate**: Must demonstrate documentation was reviewed
- ✅ **Test Execution Gate**: Must show evidence of complete test execution  
- ✅ **E2E Validation Gate**: Must prove full workflow completion (not just setup)
- ✅ **Evidence Collection Gate**: Must provide concrete evidence for conclusions

### **2. Error Prevention Triggers**

Automatic blocks for common mistakes:
- 🚫 **Block partial E2E success claims**: Require proof of complete workflow
- 🚫 **Block assumption-based recommendations**: Require concrete evidence
- 🚫 **Block incomplete dependency validation**: Verify all requirements met
- 🚫 **Block undocumented assessments**: Require evaluation checklist completion

### **3. Quality Assurance Automation**

- **Automatic Evidence Collection**: AI must capture and present concrete proof
- **Systematic Validation**: AI must follow complete evaluation process
- **Decision Justification**: AI must cite specific evidence for recommendations
- **Completeness Verification**: AI must validate all workflow steps completed

## 📝 Implementation Files

### **Core Automation Files to Create**:

1. **`ai_workflow_triggers.py`** - Context detection and workflow triggering
2. **`ai_evaluation_automation.py`** - Automated evaluation execution  
3. **`ai_validation_gates.py`** - Completion validation and error prevention
4. **`ai_evidence_collector.py`** - Automated evidence gathering and documentation

### **Integration Points**:

- **Pre-commit hooks**: Trigger automated workflows for integration commits
- **Test execution**: Automatic comprehensive validation on test requests
- **Documentation updates**: Auto-reference evaluation standards in responses
- **Git operations**: Auto-trigger evaluation workflows for branch operations

## 🎯 Expected Behavior Changes

### **Before Automation**:
Human: "Let's analyze this branch for integration"
AI: Provides basic analysis without following standards

### **After Automation**:
Human: "Let's analyze this branch for integration"  
AI: 
1. **Automatically generates**: Evaluation checklist for detected branch
2. **Automatically executes**: Complete documentation review
3. **Automatically runs**: Full test validation (unit → integration → E2E)
4. **Automatically collects**: Evidence for all findings
5. **Automatically applies**: Integration readiness criteria
6. **Automatically provides**: Evidence-based READY/NOT READY decision

### **Quality Guarantees**:
- ✅ **No partial evaluations**: Validation gates prevent incomplete assessments
- ✅ **No assumption-based conclusions**: Evidence requirements enforced automatically  
- ✅ **No missed dependencies**: Systematic validation ensures completeness
- ✅ **No procedural errors**: Automated workflow prevents standard violations

## 🚀 Implementation Priority

### **Phase 1: Core Detection** (Immediate)
- Context detection for integration requests
- Automatic evaluation checklist generation
- Basic workflow triggering

### **Phase 2: Validation Gates** (Critical)  
- Completion validation before recommendations
- Evidence collection requirements
- Error prevention mechanisms

### **Phase 3: Full Automation** (Comprehensive)
- Complete workflow automation
- Advanced context detection
- Intelligent evidence gathering

The goal is to make proper evaluation standards **automatic and invisible** to the human user while ensuring **complete compliance** with documented procedures.