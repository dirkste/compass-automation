# Code Evaluation Standards

This document establishes mandatory standards for evaluating code changes, integration readiness, and system validation to ensure thorough and accurate assessments.

## 🎯 Core Principles

### 1. **Evidence-Based Analysis Only**
- All recommendations MUST be supported by concrete evidence
- Never assume functionality works without verification
- Document all assumptions and validate them
- Cite specific test results, logs, and documentation

### 2. **Complete Context Review**
- Read ALL relevant documentation before analysis
- Review project setup requirements (GEMINI.md, README files)
- Check historical context (git logs, commit messages)
- Understand dependencies and data requirements

### 3. **Systematic Validation**
- Follow the complete testing pyramid (unit → integration → E2E)
- Validate ALL components of a workflow, not just initial steps
- Test failure scenarios and edge cases
- Verify configuration and environmental requirements

## 📋 Pre-Evaluation Checklist

Before making ANY recommendations about code readiness:

### ☑️ **Documentation Review**
- [ ] Read project overview and setup requirements
- [ ] Review test expectations and data requirements  
- [ ] Check configuration dependencies
- [ ] Understand the complete workflow being tested
- [ ] Verify environmental prerequisites

### ☑️ **Historical Context**
- [ ] Review git history for relevant changes
- [ ] Check for removed or relocated components
- [ ] Understand previous architectural decisions
- [ ] Identify potential breaking changes

### ☑️ **Test Analysis**
- [ ] Identify what each test actually validates
- [ ] Distinguish between setup/teardown vs core functionality
- [ ] Verify test data requirements and availability
- [ ] Confirm test coverage of critical paths

## 🧪 Testing Evaluation Standards

### **Unit Tests**
**Purpose**: Validate individual component functionality
**Requirements**:
- [ ] All components can be imported
- [ ] Core logic functions correctly in isolation
- [ ] Configuration loading works
- [ ] Error handling behaves as expected

**Analysis Criteria**:
- Passing unit tests indicate component-level stability
- Do NOT assume system integration based on unit test success

### **Integration Tests**
**Purpose**: Validate component interaction and system configuration
**Requirements**:
- [ ] Components integrate correctly
- [ ] Configuration systems work end-to-end
- [ ] Version compatibility validated
- [ ] Cross-module functionality verified

**Analysis Criteria**:
- Integration test success indicates system-level readiness
- Still requires E2E validation for business workflow confidence

### **End-to-End (E2E) Tests**
**Purpose**: Validate complete business workflows in real environment
**Requirements**:
- [ ] All test data and environmental dependencies available
- [ ] Complete workflow executes from start to finish
- [ ] Business logic validated with real interactions
- [ ] Error scenarios handled appropriately

**Analysis Criteria**:
- E2E tests MUST complete the entire workflow to be considered passing
- Authentication success ≠ E2E validation
- Partial execution = incomplete validation

## ❌ Common Evaluation Errors to Avoid

### **1. Partial Test Success Misinterpretation**
**Error**: Concluding E2E success when only setup phase completed
**Example**: "Login worked, therefore E2E validation complete"
**Correct**: E2E test must complete entire business workflow

### **2. Missing Data Dependencies**
**Error**: Ignoring missing test data or configuration
**Example**: "System works fine" when required CSV files missing
**Correct**: All dependencies must be available for valid testing

### **3. Assumption-Based Recommendations**
**Error**: Making recommendations without complete validation
**Example**: "Core systems working" based on partial evidence
**Correct**: Verify ALL system components before concluding readiness

### **4. Documentation Neglect**
**Error**: Analyzing code without reading setup requirements
**Example**: Missing .gitignore patterns or data requirements
**Correct**: Always review documentation BEFORE making assessments

## 📊 Integration Readiness Criteria

For code to be considered ready for integration:

### ✅ **PASS Criteria**
- [ ] All unit tests pass (74/74 or current count)
- [ ] All integration tests pass with real system validation
- [ ] Complete E2E test execution with business workflow validation
- [ ] All documented dependencies available
- [ ] No breaking changes to existing functionality
- [ ] Version compatibility confirmed
- [ ] Error handling validated

### ❌ **FAIL Criteria**
- Any test failures (investigate root cause)
- Missing required data or configuration files
- Incomplete E2E test execution
- Undocumented breaking changes
- Version incompatibilities
- Environmental setup issues

### ⚠️ **REQUIRES INVESTIGATION**
- Skipped tests (understand why and validate reason)
- New dependencies or requirements
- Changes to core configuration systems
- Modified authentication or security components

## 🔍 Evaluation Process

### **Phase 1: Documentation Review**
1. Read project documentation (GEMINI.md, README files)
2. Review setup requirements and dependencies
3. Understand data requirements and test expectations
4. Check for recent architectural changes

### **Phase 2: Historical Analysis**
1. Review git history for context
2. Identify removed or relocated components
3. Understand previous integration decisions
4. Check for environmental changes

### **Phase 3: Test Execution & Analysis**
1. Run unit tests and analyze results
2. Execute integration tests with real system validation
3. **CRITICAL**: Run complete E2E tests with all dependencies
4. Verify all test data and environmental requirements

### **Phase 4: Risk Assessment**
1. Identify potential breaking changes
2. Assess impact on existing functionality
3. Evaluate rollback possibilities
4. Document any remaining risks

### **Phase 5: Recommendation**
1. Provide evidence-based assessment
2. Document all validation performed
3. List any remaining requirements or blockers
4. Include specific next steps if not ready

## 📝 Evaluation Report Template

```markdown
# Code Evaluation Report

## Summary
- **Branch**: [branch name]
- **Commits**: [commit range]
- **Evaluation Date**: [date]
- **Evaluator**: [name]

## Documentation Review
- [ ] Project setup requirements reviewed
- [ ] Test expectations documented
- [ ] Dependencies identified
- [ ] Data requirements confirmed

## Test Results
### Unit Tests: [X/X passed]
- [Details of any failures or issues]

### Integration Tests: [X/X passed, X skipped]
- [Details of system validation]

### E2E Tests: [PASS/FAIL/INCOMPLETE]
- [Complete workflow validation results]
- [Any missing dependencies or setup issues]

## Risk Assessment
- **Breaking Changes**: [Yes/No - list if any]
- **New Dependencies**: [list if any]
- **Environmental Requirements**: [list changes]

## Recommendation
**[READY/NOT READY/REQUIRES INVESTIGATION]**

### Evidence:
- [Specific test results supporting recommendation]
- [Documentation reviewed]
- [Validation performed]

### Requirements for Integration:
- [List any remaining blockers]
- [Specific steps needed before integration]
```

## 🚀 Implementation Guidelines

### **For Evaluators**
1. **Always use this checklist** before making recommendations
2. **Document your evaluation process** using the template
3. **Be explicit about what was and wasn't tested**
4. **Never assume - always verify**

### **For Code Authors**
1. **Provide complete setup documentation** 
2. **Include test data templates and requirements**
3. **Document any environmental dependencies**
4. **Ensure E2E tests can run with provided setup**

### **For Integration Decisions**
1. **Require completed evaluation reports**
2. **Verify all criteria met before integration**
3. **Maintain evaluation history for learning**
4. **Update standards based on lessons learned**

---

## 📚 References

- See `GEMINI.md` for project-specific setup requirements
- See `data/README.md` for test data setup
- See individual test files for specific validation criteria
- See git history for context on architectural decisions

**Remember**: Thorough evaluation prevents production issues and ensures system reliability. Take the time to do it right.