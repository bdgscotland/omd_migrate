# Branch Protection Setup

This document outlines the recommended branch protection rules for the OpenMetadata Migration Tool repository.

## Main Branch Protection

To set up branch protection for the `main` branch, follow these steps:

### 1. Navigate to Branch Protection Settings

1. Go to your repository on GitHub
2. Click on **Settings** tab
3. Click on **Branches** in the left sidebar
4. Click **Add rule** next to "Branch protection rules"

### 2. Configure Protection Rules

#### Basic Settings
- **Branch name pattern**: `main`
- **Restrict pushes that create files larger than 100MB**: ✅ Checked

#### Pull Request Requirements
- **Require a pull request before merging**: ✅ Checked
  - **Require approvals**: ✅ Checked (minimum 1 approval)
  - **Dismiss stale pull request approvals when new commits are pushed**: ✅ Checked
  - **Require review from code owners**: ✅ Checked (if CODEOWNERS file exists)
  - **Restrict pushes that create files larger than 100MB**: ✅ Checked

#### Status Check Requirements
- **Require status checks to pass before merging**: ✅ Checked
- **Require branches to be up to date before merging**: ✅ Checked

**Required Status Checks** (these must pass):
- `Test Suite (3.9)`
- `Test Suite (3.10)` 
- `Test Suite (3.11)`
- `Security Scan`
- `Code Quality`
- `Integration Tests`
- `Documentation Check`
- `Build Test`
- `All Checks Passed`
- `PR Validation`
- `PR Size Check`
- `Security PR Check`
- `Dependency Check`

#### Additional Restrictions
- **Restrict pushes that create files larger than 100MB**: ✅ Checked
- **Include administrators**: ✅ Checked
- **Allow force pushes**: ❌ Unchecked
- **Allow deletions**: ❌ Unchecked

### 3. Required Status Checks Explanation

#### CI/CD Pipeline (`ci.yml`)
- **Test Suite**: Runs unit tests on Python 3.9, 3.10, and 3.11
- **Security Scan**: Trivy vulnerability scanning
- **Code Quality**: Black formatting, isort imports, complexity analysis
- **Integration Tests**: CLI testing and configuration validation
- **Documentation Check**: Ensures no sensitive info and complete docs
- **Build Test**: Validates setup scripts and requirements

#### PR Quality Checks (`pr-checks.yml`)
- **PR Validation**: Checks title format and description quality
- **PR Size Check**: Warns about overly large PRs
- **Security PR Check**: Scans for sensitive information in changes
- **Dependency Check**: Reviews dependency modifications

### 4. Team Permissions

#### Repository Roles
- **Admin**: Repository owners and maintainers
- **Maintain**: Senior contributors who can manage settings
- **Write**: Regular contributors who can create branches and PRs
- **Triage**: Can manage issues and PRs but not merge
- **Read**: Can view and clone the repository

#### Recommended Settings
- Only **Admin** and **Maintain** roles can bypass branch protection
- **Write** access contributors must follow PR process
- Enable **"Require signed commits"** for enhanced security

### 5. Code Owners (Optional)

Create a `.github/CODEOWNERS` file to automatically request reviews:

```
# Global owners
* @repository-admin @lead-maintainer

# Core files
export.py @core-team
import.py @core-team
config.yaml @core-team

# Documentation
README.md @docs-team
.github/ @devops-team

# CI/CD
.github/workflows/ @devops-team
Makefile @devops-team
```

## Development Workflow

### For Contributors

1. **Fork the repository** (for external contributors)
2. **Create a feature branch**: `git checkout -b feat/your-feature`
3. **Make changes** following the coding standards
4. **Run tests locally**: `make test`
5. **Push branch**: `git push origin feat/your-feature`
6. **Create Pull Request** with meaningful title and description
7. **Address review feedback** and ensure all checks pass
8. **Merge** once approved and all checks are green

### For Maintainers

1. **Review PRs thoroughly** checking:
   - Code quality and standards
   - Test coverage
   - Documentation updates
   - Security implications
   - Breaking change impact

2. **Ensure all status checks pass** before merging

3. **Use appropriate merge strategy**:
   - **Squash and merge**: For feature branches (recommended)
   - **Merge commit**: For significant features with multiple commits
   - **Rebase and merge**: For clean linear history

## Emergency Procedures

### Hotfix Process

For critical security fixes or production issues:

1. **Create hotfix branch** from `main`: `git checkout -b hotfix/urgent-fix`
2. **Make minimal necessary changes**
3. **Create PR** with `[HOTFIX]` prefix in title
4. **Expedited review** with focus on security and impact
5. **Deploy immediately** after merge

### Branch Protection Override

Administrators can temporarily disable branch protection for:
- Emergency deployments
- Repository maintenance
- Fixing broken CI/CD

**⚠️ Important**: Always re-enable protection immediately after emergency actions.

## Monitoring and Maintenance

### Regular Reviews

- **Monthly**: Review and update required status checks
- **Quarterly**: Assess branch protection effectiveness
- **After incidents**: Update rules based on lessons learned

### Metrics to Track

- PR merge time
- Failed status check frequency
- Security scan results
- Code coverage trends

## Troubleshooting

### Common Issues

1. **Status check not appearing**:
   - Ensure workflow file is on the target branch
   - Check workflow syntax with `yamllint`
   - Verify job names match exactly

2. **Force push blocked**:
   - Use `git revert` instead of force push
   - Create new branch if history rewrite needed

3. **CI failing on main**:
   - Hotfix via emergency process
   - Consider temporary protection bypass

### Getting Help

- Check GitHub documentation on branch protection
- Review workflow logs for detailed error messages
- Contact repository maintainers for assistance