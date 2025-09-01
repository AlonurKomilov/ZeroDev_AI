"""
Test cases for Review Agent

This module tests the Review Agent functionality including:
- Patch application
- Linting execution  
- Test execution
- Project type detection
- Error handling
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.agents.review_agent import ReviewAgent


@pytest.fixture
def review_agent():
    """Create a Review Agent instance for testing."""
    return ReviewAgent()


@pytest.fixture
def sample_python_project(tmp_path):
    """Create a sample Python project for testing."""
    # Create a basic Python project structure
    (tmp_path / "main.py").write_text("""
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
""")
    
    (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")
    
    (tmp_path / "README.md").write_text("# Test Project\n\nA sample project for testing.")
    
    # Create a test file
    (tmp_path / "test_main.py").write_text("""
import pytest
from main import hello_world

def test_hello_world():
    # This is a basic test
    assert hello_world() is None  # Function doesn't return anything
""")
    
    return tmp_path


@pytest.fixture
def sample_js_project(tmp_path):
    """Create a sample JavaScript project for testing."""
    (tmp_path / "index.js").write_text("""
function greetUser(name) {
    return `Hello, ${name}!`;
}

module.exports = { greetUser };
""")
    
    (tmp_path / "package.json").write_text("""{
  "name": "test-project",
  "version": "1.0.0",
  "description": "A test project",
  "main": "index.js",
  "scripts": {
    "test": "echo 'No tests specified'"
  }
}""")
    
    return tmp_path


class TestReviewAgent:
    """Test cases for Review Agent functionality."""

    def test_has_python_files_with_python_files(self, review_agent, sample_python_project):
        """Test detection of Python files in a project."""
        assert review_agent._has_python_files(sample_python_project) == True

    def test_has_python_files_without_python_files(self, review_agent, tmp_path):
        """Test detection when no Python files exist."""
        (tmp_path / "README.md").write_text("Just a readme")
        assert review_agent._has_python_files(tmp_path) == False

    def test_has_js_files_with_js_files(self, review_agent, sample_js_project):
        """Test detection of JavaScript files in a project."""
        assert review_agent._has_js_files(sample_js_project) == True

    def test_has_js_files_without_js_files(self, review_agent, tmp_path):
        """Test detection when no JavaScript files exist."""
        (tmp_path / "README.md").write_text("Just a readme")
        assert review_agent._has_js_files(tmp_path) == False

    def test_run_general_checks(self, review_agent, sample_python_project):
        """Test general project validation checks."""
        result = review_agent._run_general_checks(sample_python_project)
        
        assert result["success"] == True
        assert "checks" in result
        # Note: The method uses 'warnings', not 'issues' for missing files
        expected_keys = ["checks", "warnings", "success"]
        for key in expected_keys:
            assert key in result
        
        # Should find README.md
        readme_found = any("Documentation" in check for check in result["checks"])
        assert readme_found == True

    def test_run_general_checks_missing_files(self, review_agent, tmp_path):
        """Test general checks with missing required files."""
        # Create minimal project without README
        (tmp_path / "main.py").write_text("print('hello')")
        
        result = review_agent._run_general_checks(tmp_path)
        
        assert result["success"] == True  # Still successful, but with warnings
        assert len(result["warnings"]) > 0  # Should have warnings about missing files

    @patch('subprocess.run')
    def test_run_python_linting_success(self, mock_subprocess, review_agent, sample_python_project):
        """Test successful Python linting."""
        # Mock successful flake8 run
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        result = review_agent._run_python_linting(sample_python_project)
        
        assert result["success"] == True
        assert any("flake8: PASSED" in tool for tool in result["tools_used"])

    @patch('subprocess.run')
    def test_run_python_linting_failure(self, mock_subprocess, review_agent, sample_python_project):
        """Test Python linting with issues found."""
        # Mock flake8 failure
        mock_subprocess.return_value = MagicMock(
            returncode=1, 
            stdout="main.py:1:1: F401 'unused_import' imported but unused"
        )
        
        result = review_agent._run_python_linting(sample_python_project)
        
        assert result["success"] == False
        assert any("flake8: FAILED" in tool for tool in result["tools_used"])
        assert len(result["issues"]) > 0

    @patch('subprocess.run')
    def test_run_python_tests_success(self, mock_subprocess, review_agent, sample_python_project):
        """Test successful Python test execution."""
        # Mock successful pytest run
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="2 passed in 0.1s"
        )
        
        result = review_agent._run_python_tests(sample_python_project)
        
        assert result["success"] == True
        assert result["tests_run"] == 2

    @patch('subprocess.run')
    def test_run_python_tests_failure(self, mock_subprocess, review_agent, sample_python_project):
        """Test Python test execution with failures."""
        # Mock pytest failure
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="1 failed, 1 passed in 0.2s"
        )
        
        result = review_agent._run_python_tests(sample_python_project)
        
        assert result["success"] == False
        assert result["failed"] == 1

    def test_generate_lint_summary(self, review_agent):
        """Test lint summary generation."""
        mock_results = {
            "python": {"tools_used": ["flake8: PASSED", "black: PASSED"]},
            "javascript": {"tools_used": ["eslint: FAILED"]},
            "general": {"checks": ["check1", "check2"]}
        }
        
        summary = review_agent._generate_lint_summary(mock_results)
        
        assert "Python: flake8: PASSED, black: PASSED" in summary
        assert "JavaScript: eslint: FAILED" in summary
        assert "General: 2 checks" in summary

    def test_generate_test_summary(self, review_agent):
        """Test test summary generation."""
        mock_results = {
            "python": {"tests_run": 5, "failed": 1},
            "javascript": {"success": True, "framework": "npm"},
            "general": {"checks": ["check1"], "warnings": ["warning1"]}
        }
        
        summary = review_agent._generate_test_summary(mock_results)
        
        assert "Python: 5 tests run, 1 failed" in summary
        assert "JS (npm): passed" in summary
        assert "General: 1 checks, 1 warnings" in summary

    def test_run_linting_comprehensive(self, review_agent, sample_python_project):
        """Test the main linting method with a real project."""
        result = review_agent._run_linting(sample_python_project)
        
        assert "success" in result
        assert "python" in result
        assert "summary" in result
        assert isinstance(result["summary"], str)

    def test_run_tests_comprehensive(self, review_agent, sample_python_project):
        """Test the main testing method with a real project."""
        result = review_agent._run_tests(sample_python_project)
        
        assert "success" in result
        assert "python" in result
        assert "summary" in result
        assert isinstance(result["summary"], str)

    @patch('backend.services.project_storage.project_storage_service.get_project_path')
    def test_review_patch_nonexistent_project(self, mock_get_path, review_agent):
        """Test review_patch with nonexistent project."""
        mock_get_path.return_value = Path("/nonexistent/path")
        
        # Use proper UUID strings for testing
        result = review_agent.review_patch(
            "12345678-1234-5678-1234-567812345678", 
            "87654321-4321-8765-4321-876543218765", 
            "some patch"
        )
        
        assert result["success"] == False
        assert "does not exist" in result["error"]

    # Integration-style tests would go here
    # These would test the full patch application flow
    # but require more complex setup with actual git repos
