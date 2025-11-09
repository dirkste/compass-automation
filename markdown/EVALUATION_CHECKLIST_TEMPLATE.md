# Code Evaluation Checklist Template

**Copy this template for each evaluation and fill out completely before making integration recommendations.**

---

## 📋 Evaluation Details

- **Branch Being Evaluated**: `[branch-name]`
- **Target Integration**: `[target-branch]` (usually `main`)
- **Evaluation Date**: `[YYYY-MM-DD]`
- **Evaluator**: `[name/identifier]`
- **Commit Range**: `[start-hash..end-hash]`

---

## ✅ Pre-Evaluation Requirements

### Documentation Review
- [ ] **GEMINI.md read and understood**
  - [ ] Project setup requirements clear
  - [ ] Application flow understood
  - [ ] Dependencies identified
- [ ] **README files reviewed** (if any)
- [ ] **Test documentation examined**
- [ ] **Configuration requirements understood**

### Historical Context Analysis  
- [ ] **Git history reviewed** for relevant changes
  - Command used: `git log --oneline [branch]`
  - Notable changes: `[describe key changes]`
- [ ] **Previous integration decisions** understood
- [ ] **Removed/relocated components** identified
- [ ] **Breaking changes** assessed

---

## 🧪 Test Validation

### Unit Tests
- [ ] **All unit tests executed**
  - Command: `[test command used]`
  - Result: `[X/X tests passed]`
  - Failures: `[describe any failures]`
- [ ] **Component isolation verified**
- [ ] **Core logic validated**

### Integration Tests  
- [ ] **All integration tests executed**
  - Command: `[test command used]`
  - Result: `[X/X tests passed, X skipped]`
  - Skipped reason: `[explain skips]`
- [ ] **System configuration validated**
- [ ] **Version compatibility confirmed**
- [ ] **Cross-module functionality verified**

### End-to-End (E2E) Tests
- [ ] **Complete E2E workflow executed**
  - Command: `[test command used]`
  - Result: `[PASS/FAIL/INCOMPLETE]`
  - **CRITICAL**: Full workflow completion verified (not just setup)
- [ ] **All test data dependencies available**
  - Required files: `[list required files]`
  - Availability: `[confirmed present/missing]`
- [ ] **Environmental requirements met**
  - Browser/driver versions: `[version info]`
  - Configuration: `[config status]`
- [ ] **Business logic validated end-to-end**

---

## 🔍 Dependency Analysis

### Data Requirements
- [ ] **Test data availability confirmed**
  - Required: `[list required data files]`
  - Status: `[available/missing/incomplete]`
- [ ] **Configuration files present**
  - Required: `[list config files]`
  - Status: `[verified/missing/needs update]`

### Environmental Dependencies
- [ ] **Browser/Driver compatibility verified**
  - Browser version: `[version]`
  - Driver version: `[version]`
  - Compatibility: `[compatible/mismatch/unknown]`
- [ ] **Python environment validated**
- [ ] **Package dependencies satisfied**

---

## ⚠️ Risk Assessment

### Breaking Changes
- [ ] **No breaking changes identified** OR
- [ ] **Breaking changes documented and acceptable**
  - Changes: `[describe breaking changes]`
  - Impact: `[describe impact]`
  - Mitigation: `[mitigation plan]`

### Rollback Capability
- [ ] **Rollback plan exists**
- [ ] **Previous stable state identified**
- [ ] **Rollback tested** (if high risk)

### Integration Impact
- [ ] **Existing functionality preservation verified**
- [ ] **New functionality properly integrated**
- [ ] **Configuration changes backward compatible** OR **migration plan exists**

---

## 📊 Evidence Summary

### Test Results Evidence
```
[Paste actual test execution results here]
```

### Configuration Validation Evidence
```
[Paste configuration validation results here]
```

### E2E Workflow Evidence
```
[Paste complete E2E test execution log here - MUST show complete workflow]
```

---

## 🎯 Final Assessment

### Integration Readiness: **[READY/NOT READY/REQUIRES INVESTIGATION]**

### Evidence Supporting Decision:
1. `[Specific evidence item 1]`
2. `[Specific evidence item 2]`
3. `[Specific evidence item 3]`

### Remaining Blockers (if any):
- [ ] `[Blocker 1 - specific action needed]`
- [ ] `[Blocker 2 - specific action needed]`

### Integration Requirements:
- [ ] `[Specific requirement 1]`
- [ ] `[Specific requirement 2]`

### Post-Integration Monitoring:
- [ ] `[What to monitor after integration]`
- [ ] `[Success criteria for validation]`

---

## 📝 Evaluation Notes

### What Was Tested:
`[Detailed description of validation performed]`

### What Was NOT Tested:
`[Important: List anything not validated in this evaluation]`

### Assumptions Made:
`[List any assumptions - these should be minimal and documented]`

### Recommendations:
`[Specific next steps or recommendations]`

---

**Evaluator Signature**: `[name]` - `[date]`
**Approval for Integration**: `[YES/NO]` (only if READY assessment)

---

## 📚 Reference Links

- [CODE_EVALUATION_STANDARDS.md](./CODE_EVALUATION_STANDARDS.md) - Complete evaluation standards
- [GEMINI.md](./GEMINI.md) - Project setup and requirements
- Test files: `[link to relevant test files]`
- Configuration: `[link to config files]`