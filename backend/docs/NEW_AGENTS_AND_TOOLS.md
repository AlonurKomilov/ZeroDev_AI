# Yangi AI Agentlar va Tools Tavsiyalari

## 1. Yangi Backend Agentlar (B47-B52)

### B47: Security Scanner Agent
```python
# backend/agents/security_scanner_agent.py
import ast
import re
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

from backend.core.ai_router import get_llm_adapter
from backend.core.logger import get_logger
from backend.models.analytics_model import SecurityViolationPattern

log = get_logger(__name__)

class SecurityScannerAgent:
    """
    Advanced security scanning agent that performs static code analysis,
    dependency vulnerability scanning, and security best practices validation.
    """
    
    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.ai_model = get_llm_adapter("gpt-4o-mini")
    
    def _load_vulnerability_patterns(self) -> Dict[str, List[str]]:
        """Load security vulnerability patterns from configuration"""
        return {
            "sql_injection": [
                r"execute\s*\(\s*['\"][^'\"]*\+",
                r"query\s*\(\s*['\"][^'\"]*\%s",
                r"cursor\.execute\s*\([^)]*\+[^)]*\)"
            ],
            "code_injection": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"subprocess\..*shell\s*=\s*True"
            ],
            "xss_vulnerabilities": [
                r"innerHTML\s*=\s*[^;]*\+",
                r"document\.write\s*\([^)]*\+",
                r"dangerouslySetInnerHTML"
            ],
            "hardcoded_secrets": [
                r"password\s*=\s*['\"][^'\"]{8,}",
                r"api_key\s*=\s*['\"][^'\"]{20,}",
                r"secret\s*=\s*['\"][^'\"]{16,}"
            ]
        }
    
    async def scan_project(self, project_path: str, project_id: str) -> Dict:
        """
        Comprehensive security scan of a project
        """
        log.info(f"Starting security scan for project: {project_id}")
        
        project_dir = Path(project_path)
        scan_results = {
            "project_id": project_id,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "vulnerabilities": [],
            "dependency_issues": [],
            "security_score": 0,
            "recommendations": []
        }
        
        try:
            # 1. Static code analysis
            code_issues = await self._analyze_source_code(project_dir)
            scan_results["vulnerabilities"].extend(code_issues)
            
            # 2. Dependency vulnerability scan
            deps_issues = await self._scan_dependencies(project_dir)
            scan_results["dependency_issues"].extend(deps_issues)
            
            # 3. Configuration security check
            config_issues = await self._check_security_configs(project_dir)
            scan_results["vulnerabilities"].extend(config_issues)
            
            # 4. AI-powered security review
            ai_recommendations = await self._ai_security_review(project_dir)
            scan_results["recommendations"].extend(ai_recommendations)
            
            # 5. Calculate security score
            scan_results["security_score"] = self._calculate_security_score(scan_results)
            
            log.info(f"Security scan completed. Score: {scan_results['security_score']}/100")
            
        except Exception as e:
            log.error(f"Security scan failed: {e}")
            scan_results["error"] = str(e)
        
        return scan_results
    
    async def _analyze_source_code(self, project_dir: Path) -> List[Dict]:
        """Static analysis of source code for security vulnerabilities"""
        vulnerabilities = []
        
        for file_path in project_dir.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Pattern-based vulnerability detection
                for vuln_type, patterns in self.vulnerability_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            vulnerabilities.append({
                                "type": vuln_type,
                                "severity": self._get_severity(vuln_type),
                                "file": str(file_path.relative_to(project_dir)),
                                "line": line_num,
                                "description": f"Potential {vuln_type.replace('_', ' ')} vulnerability",
                                "code_snippet": self._get_code_context(content, match.start())
                            })
                
                # AST-based analysis for complex patterns
                try:
                    tree = ast.parse(content)
                    ast_vulnerabilities = self._analyze_ast(tree, file_path, project_dir)
                    vulnerabilities.extend(ast_vulnerabilities)
                except SyntaxError:
                    log.warning(f"Could not parse {file_path} for AST analysis")
                    
            except Exception as e:
                log.warning(f"Could not analyze {file_path}: {e}")
        
        return vulnerabilities
    
    async def _scan_dependencies(self, project_dir: Path) -> List[Dict]:
        """Scan project dependencies for known vulnerabilities"""
        issues = []
        
        # Check for requirements.txt (Python)
        req_file = project_dir / "requirements.txt"
        if req_file.exists():
            try:
                result = subprocess.run([
                    "safety", "check", "-r", str(req_file), "--json"
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        issues.append({
                            "type": "dependency_vulnerability",
                            "package": vuln.get("package"),
                            "version": vuln.get("installed_version"),
                            "vulnerability_id": vuln.get("id"),
                            "severity": "high",
                            "description": vuln.get("advisory")
                        })
            except (subprocess.SubprocessError, json.JSONDecodeError) as e:
                log.warning(f"Safety check failed: {e}")
        
        # Check for package.json (Node.js)
        pkg_file = project_dir / "package.json"
        if pkg_file.exists():
            try:
                result = subprocess.run([
                    "npm", "audit", "--json"
                ], cwd=project_dir, capture_output=True, text=True)
                
                if result.stdout:
                    audit_data = json.loads(result.stdout)
                    if "vulnerabilities" in audit_data:
                        for pkg, vuln_info in audit_data["vulnerabilities"].items():
                            issues.append({
                                "type": "dependency_vulnerability",
                                "package": pkg,
                                "severity": vuln_info.get("severity", "unknown"),
                                "description": f"npm audit found {vuln_info.get('severity')} vulnerability"
                            })
            except (subprocess.SubprocessError, json.JSONDecodeError) as e:
                log.warning(f"npm audit failed: {e}")
        
        return issues
    
    async def _ai_security_review(self, project_dir: Path) -> List[str]:
        """Use AI to provide security recommendations"""
        try:
            # Gather project structure and key files
            project_info = self._gather_project_context(project_dir)
            
            prompt = f"""
            Review this project for security best practices and provide recommendations:
            
            Project structure: {project_info['structure']}
            Key configurations: {project_info['configs']}
            Dependencies: {project_info['dependencies']}
            
            Provide 5-10 specific security recommendations focusing on:
            1. Authentication and authorization
            2. Data protection
            3. Input validation
            4. Error handling
            5. Deployment security
            
            Format as a JSON list of strings.
            """
            
            response = await self.ai_model.chat_completion([
                {"role": "system", "content": "You are a security expert reviewing code for vulnerabilities."},
                {"role": "user", "content": prompt}
            ])
            
            recommendations = json.loads(response.choices[0].message.content)
            return recommendations if isinstance(recommendations, list) else []
            
        except Exception as e:
            log.warning(f"AI security review failed: {e}")
            return ["AI security review unavailable"]

security_scanner_agent = SecurityScannerAgent()
```

### B48: Performance Analyzer Agent
```python
# backend/agents/performance_analyzer_agent.py
import asyncio
import psutil
import time
from typing import Dict, List, Optional
import subprocess
from pathlib import Path
import json
from datetime import datetime

from backend.core.redis import get_redis
from backend.core.database import get_session
from backend.core.logger import get_logger

log = get_logger(__name__)

class PerformanceAnalyzerAgent:
    """
    Comprehensive performance analysis agent that monitors application
    performance, identifies bottlenecks, and provides optimization recommendations.
    """
    
    def __init__(self):
        self.redis = get_redis()
        self.metrics_history = []
    
    async def analyze_performance(self, project_path: str, project_id: str) -> Dict:
        """
        Comprehensive performance analysis of a running application
        """
        log.info(f"Starting performance analysis for project: {project_id}")
        
        analysis_results = {
            "project_id": project_id,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {},
            "application_metrics": {},
            "database_performance": {},
            "recommendations": [],
            "performance_score": 0
        }
        
        try:
            # 1. System resource analysis
            system_metrics = await self._analyze_system_resources()
            analysis_results["system_metrics"] = system_metrics
            
            # 2. Application performance metrics
            app_metrics = await self._analyze_application_performance(project_path)
            analysis_results["application_metrics"] = app_metrics
            
            # 3. Database performance analysis
            db_metrics = await self._analyze_database_performance()
            analysis_results["database_performance"] = db_metrics
            
            # 4. Code quality metrics
            code_metrics = await self._analyze_code_quality(project_path)
            analysis_results["code_quality"] = code_metrics
            
            # 5. Generate optimization recommendations
            recommendations = await self._generate_recommendations(analysis_results)
            analysis_results["recommendations"] = recommendations
            
            # 6. Calculate performance score
            analysis_results["performance_score"] = self._calculate_performance_score(analysis_results)
            
            # 7. Store metrics for trending
            await self._store_metrics(project_id, analysis_results)
            
            log.info(f"Performance analysis completed. Score: {analysis_results['performance_score']}/100")
            
        except Exception as e:
            log.error(f"Performance analysis failed: {e}")
            analysis_results["error"] = str(e)
        
        return analysis_results
    
    async def _analyze_system_resources(self) -> Dict:
        """Analyze system resource utilization"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            # Process analysis
            current_process = psutil.Process()
            process_info = {
                "cpu_percent": current_process.cpu_percent(),
                "memory_mb": current_process.memory_info().rss / 1024 / 1024,
                "threads": current_process.num_threads(),
                "open_files": len(current_process.open_files())
            }
            
            return {
                "cpu_usage_percent": cpu_percent,
                "memory": {
                    "total_gb": memory.total / 1024**3,
                    "available_gb": memory.available / 1024**3,
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": disk.total / 1024**3,
                    "free_gb": disk.free / 1024**3,
                    "used_percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                },
                "process": process_info
            }
        except Exception as e:
            log.error(f"System resource analysis failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_application_performance(self, project_path: str) -> Dict:
        """Analyze application-specific performance metrics"""
        metrics = {}
        
        try:
            # 1. Response time analysis
            if self.redis:
                response_times = await self._get_cached_response_times()
                if response_times:
                    metrics["response_times"] = {
                        "average_ms": sum(response_times) / len(response_times),
                        "min_ms": min(response_times),
                        "max_ms": max(response_times),
                        "p95_ms": self._calculate_percentile(response_times, 95)
                    }
            
            # 2. Cache hit rate analysis
            cache_stats = await self._analyze_cache_performance()
            metrics["cache"] = cache_stats
            
            # 3. API endpoint performance
            endpoint_stats = await self._analyze_endpoint_performance()
            metrics["endpoints"] = endpoint_stats
            
            # 4. Error rate analysis
            error_stats = await self._analyze_error_rates()
            metrics["errors"] = error_stats
            
            return metrics
            
        except Exception as e:
            log.error(f"Application performance analysis failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_database_performance(self) -> Dict:
        """Analyze database performance metrics"""
        try:
            with get_session() as session:
                # Query performance analysis
                slow_queries = await self._get_slow_queries(session)
                connection_stats = await self._get_connection_stats(session)
                
                return {
                    "slow_queries": slow_queries,
                    "connections": connection_stats,
                    "query_cache_hit_rate": await self._get_query_cache_hit_rate(session)
                }
        except Exception as e:
            log.error(f"Database performance analysis failed: {e}")
            return {"error": str(e)}
    
    async def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate performance optimization recommendations based on analysis"""
        recommendations = []
        
        # CPU recommendations
        cpu_usage = analysis_results.get("system_metrics", {}).get("cpu_usage_percent", 0)
        if cpu_usage > 80:
            recommendations.append("High CPU usage detected. Consider implementing caching or optimizing algorithms.")
        
        # Memory recommendations
        memory_info = analysis_results.get("system_metrics", {}).get("memory", {})
        if memory_info.get("used_percent", 0) > 85:
            recommendations.append("High memory usage. Consider implementing memory pooling or garbage collection optimization.")
        
        # Database recommendations
        db_metrics = analysis_results.get("database_performance", {})
        if db_metrics.get("slow_queries"):
            recommendations.append("Slow database queries detected. Consider adding indexes or query optimization.")
        
        # Cache recommendations
        cache_metrics = analysis_results.get("application_metrics", {}).get("cache", {})
        if cache_metrics.get("hit_rate", 100) < 70:
            recommendations.append("Low cache hit rate. Consider cache warming strategies or TTL optimization.")
        
        # Response time recommendations
        response_metrics = analysis_results.get("application_metrics", {}).get("response_times", {})
        if response_metrics.get("average_ms", 0) > 500:
            recommendations.append("Slow response times detected. Consider API optimization and async processing.")
        
        return recommendations

performance_analyzer_agent = PerformanceAnalyzerAgent()
```

### B49: Documentation Generator Agent
```python
# backend/agents/documentation_generator_agent.py
import ast
import os
import re
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

from backend.core.ai_router import get_llm_adapter
from backend.core.logger import get_logger

log = get_logger(__name__)

class DocumentationGeneratorAgent:
    """
    Intelligent documentation generator that analyzes code structure,
    extracts function signatures, and generates comprehensive documentation.
    """
    
    def __init__(self):
        self.ai_model = get_llm_adapter("gpt-4o-mini")
    
    async def generate_documentation(self, project_path: str, project_id: str) -> Dict:
        """
        Generate comprehensive documentation for a project
        """
        log.info(f"Starting documentation generation for project: {project_id}")
        
        project_dir = Path(project_path)
        doc_results = {
            "project_id": project_id,
            "generation_timestamp": datetime.utcnow().isoformat(),
            "generated_files": [],
            "api_documentation": {},
            "code_documentation": {},
            "readme_content": "",
            "architecture_diagram": ""
        }
        
        try:
            # 1. Generate README.md
            readme_content = await self._generate_readme(project_dir)
            doc_results["readme_content"] = readme_content
            await self._write_file(project_dir / "README.md", readme_content)
            doc_results["generated_files"].append("README.md")
            
            # 2. Generate API documentation
            api_docs = await self._generate_api_docs(project_dir)
            doc_results["api_documentation"] = api_docs
            if api_docs:
                await self._write_file(project_dir / "docs/API.md", api_docs["content"])
                doc_results["generated_files"].append("docs/API.md")
            
            # 3. Generate code documentation
            code_docs = await self._generate_code_docs(project_dir)
            doc_results["code_documentation"] = code_docs
            
            # 4. Generate architecture documentation
            arch_docs = await self._generate_architecture_docs(project_dir)
            if arch_docs:
                await self._write_file(project_dir / "docs/ARCHITECTURE.md", arch_docs)
                doc_results["generated_files"].append("docs/ARCHITECTURE.md")
            
            # 5. Generate deployment guide
            deploy_docs = await self._generate_deployment_docs(project_dir)
            if deploy_docs:
                await self._write_file(project_dir / "docs/DEPLOYMENT.md", deploy_docs)
                doc_results["generated_files"].append("docs/DEPLOYMENT.md")
            
            # 6. Generate changelog
            changelog = await self._generate_changelog(project_dir)
            if changelog:
                await self._write_file(project_dir / "CHANGELOG.md", changelog)
                doc_results["generated_files"].append("CHANGELOG.md")
            
            log.info(f"Documentation generation completed. Generated {len(doc_results['generated_files'])} files")
            
        except Exception as e:
            log.error(f"Documentation generation failed: {e}")
            doc_results["error"] = str(e)
        
        return doc_results
    
    async def _generate_readme(self, project_dir: Path) -> str:
        """Generate comprehensive README.md"""
        try:
            # Analyze project structure
            project_info = await self._analyze_project_structure(project_dir)
            
            # Detect project type and main technologies
            tech_stack = await self._detect_technologies(project_dir)
            
            prompt = f"""
            Generate a comprehensive README.md for this project:
            
            Project structure: {json.dumps(project_info, indent=2)}
            Technologies: {', '.join(tech_stack)}
            
            Include these sections:
            1. Project title and description
            2. Features list
            3. Tech stack
            4. Installation instructions
            5. Usage examples
            6. API documentation (if applicable)
            7. Contributing guidelines
            8. License information
            
            Make it professional and user-friendly.
            """
            
            response = await self.ai_model.chat_completion([
                {"role": "system", "content": "You are a technical writer creating project documentation."},
                {"role": "user", "content": prompt}
            ])
            
            return response.choices[0].message.content
            
        except Exception as e:
            log.error(f"README generation failed: {e}")
            return f"# {project_dir.name}\n\nProject documentation will be generated here."
    
    async def _generate_api_docs(self, project_dir: Path) -> Optional[Dict]:
        """Generate API documentation from code analysis"""
        try:
            api_endpoints = []
            
            # Find API route files
            for py_file in project_dir.rglob("*.py"):
                if "api" in str(py_file) or "routes" in str(py_file):
                    endpoints = await self._extract_api_endpoints(py_file)
                    api_endpoints.extend(endpoints)
            
            if not api_endpoints:
                return None
            
            # Generate API documentation
            prompt = f"""
            Generate API documentation for these endpoints:
            
            {json.dumps(api_endpoints, indent=2)}
            
            Include:
            1. Overview
            2. Authentication
            3. Endpoint descriptions with examples
            4. Request/response formats
            5. Error codes
            6. Rate limiting info
            
            Format as Markdown.
            """
            
            response = await self.ai_model.chat_completion([
                {"role": "system", "content": "You are documenting a REST API."},
                {"role": "user", "content": prompt}
            ])
            
            return {
                "endpoints": api_endpoints,
                "content": response.choices[0].message.content
            }
            
        except Exception as e:
            log.error(f"API documentation generation failed: {e}")
            return None
    
    async def _extract_api_endpoints(self, file_path: Path) -> List[Dict]:
        """Extract API endpoints from Python files"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with AST for function definitions
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for FastAPI decorators
                    decorators = []
                    for decorator in node.decorator_list:
                        if hasattr(decorator, 'attr'):
                            decorators.append(f"{decorator.attr}")
                        elif hasattr(decorator, 'id'):
                            decorators.append(decorator.id)
                    
                    # Check if it's an API endpoint
                    api_methods = ['get', 'post', 'put', 'delete', 'patch']
                    for method in api_methods:
                        if method in decorators:
                            # Extract route path from decorator
                            route_path = self._extract_route_path(content, node.lineno)
                            
                            endpoints.append({
                                "method": method.upper(),
                                "path": route_path or f"/{node.name}",
                                "function_name": node.name,
                                "docstring": ast.get_docstring(node),
                                "file": str(file_path.name)
                            })
                            break
        
        except Exception as e:
            log.warning(f"Could not extract endpoints from {file_path}: {e}")
        
        return endpoints

documentation_generator_agent = DocumentationGeneratorAgent()
```

### B50: Database Schema Agent
```python
# backend/agents/database_schema_agent.py
import asyncio
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import subprocess

from sqlalchemy import inspect, MetaData, Table
from sqlalchemy.engine import Engine
from sqlmodel import Session

from backend.core.database import get_engine, get_session
from backend.core.ai_router import get_llm_adapter
from backend.core.logger import get_logger

log = get_logger(__name__)

class DatabaseSchemaAgent:
    """
    Database schema management agent that handles schema migrations,
    optimizations, and documentation generation.
    """
    
    def __init__(self):
        self.engine = get_engine()
        self.ai_model = get_llm_adapter("gpt-4o-mini")
    
    async def analyze_schema(self, project_id: str) -> Dict:
        """
        Comprehensive database schema analysis
        """
        log.info(f"Starting database schema analysis for project: {project_id}")
        
        analysis_results = {
            "project_id": project_id,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "schema_info": {},
            "performance_issues": [],
            "optimization_suggestions": [],
            "migration_recommendations": [],
            "documentation": ""
        }
        
        try:
            # 1. Extract current schema information
            schema_info = await self._extract_schema_info()
            analysis_results["schema_info"] = schema_info
            
            # 2. Analyze performance issues
            performance_issues = await self._analyze_performance_issues()
            analysis_results["performance_issues"] = performance_issues
            
            # 3. Generate optimization suggestions
            optimizations = await self._generate_optimizations(schema_info, performance_issues)
            analysis_results["optimization_suggestions"] = optimizations
            
            # 4. Check for migration needs
            migrations = await self._check_migration_needs(schema_info)
            analysis_results["migration_recommendations"] = migrations
            
            # 5. Generate schema documentation
            documentation = await self._generate_schema_documentation(schema_info)
            analysis_results["documentation"] = documentation
            
            log.info("Database schema analysis completed")
            
        except Exception as e:
            log.error(f"Database schema analysis failed: {e}")
            analysis_results["error"] = str(e)
        
        return analysis_results
    
    async def _extract_schema_info(self) -> Dict:
        """Extract detailed schema information"""
        try:
            inspector = inspect(self.engine)
            schema_info = {
                "tables": {},
                "indexes": {},
                "foreign_keys": {},
                "constraints": {}
            }
            
            # Get all table names
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                # Get table columns
                columns = inspector.get_columns(table_name)
                schema_info["tables"][table_name] = {
                    "columns": [],
                    "row_count": await self._get_table_row_count(table_name)
                }
                
                for column in columns:
                    schema_info["tables"][table_name]["columns"].append({
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column["nullable"],
                        "default": column.get("default"),
                        "primary_key": column.get("primary_key", False)
                    })
                
                # Get indexes
                indexes = inspector.get_indexes(table_name)
                schema_info["indexes"][table_name] = indexes
                
                # Get foreign keys
                foreign_keys = inspector.get_foreign_keys(table_name)
                schema_info["foreign_keys"][table_name] = foreign_keys
                
                # Get constraints
                constraints = inspector.get_check_constraints(table_name)
                schema_info["constraints"][table_name] = constraints
            
            return schema_info
            
        except Exception as e:
            log.error(f"Schema extraction failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_performance_issues(self) -> List[Dict]:
        """Analyze database performance issues"""
        issues = []
        
        try:
            with get_session() as session:
                # Check for missing indexes
                missing_indexes = await self._find_missing_indexes(session)
                issues.extend(missing_indexes)
                
                # Check for unused indexes
                unused_indexes = await self._find_unused_indexes(session)
                issues.extend(unused_indexes)
                
                # Check for large tables without partitioning
                large_tables = await self._find_large_unpartitioned_tables(session)
                issues.extend(large_tables)
                
                # Check for inefficient queries
                slow_queries = await self._find_slow_queries(session)
                issues.extend(slow_queries)
        
        except Exception as e:
            log.error(f"Performance analysis failed: {e}")
            issues.append({"type": "analysis_error", "description": str(e)})
        
        return issues
    
    async def _generate_optimizations(self, schema_info: Dict, performance_issues: List[Dict]) -> List[Dict]:
        """Generate database optimization suggestions using AI"""
        try:
            prompt = f"""
            Analyze this database schema and performance issues to suggest optimizations:
            
            Schema Information:
            {json.dumps(schema_info, indent=2, default=str)}
            
            Performance Issues:
            {json.dumps(performance_issues, indent=2)}
            
            Provide specific optimization suggestions including:
            1. Index recommendations
            2. Query optimization
            3. Schema design improvements
            4. Partitioning strategies
            5. Caching opportunities
            
            Format as JSON array of optimization objects with fields: type, description, priority, sql_command (if applicable)
            """
            
            response = await self.ai_model.chat_completion([
                {"role": "system", "content": "You are a database optimization expert."},
                {"role": "user", "content": prompt}
            ])
            
            optimizations = json.loads(response.choices[0].message.content)
            return optimizations if isinstance(optimizations, list) else []
            
        except Exception as e:
            log.error(f"Optimization generation failed: {e}")
            return [{"type": "generation_error", "description": str(e)}]
    
    async def create_migration(self, changes: Dict, project_id: str) -> Dict:
        """
        Create database migration based on schema changes
        """
        try:
            migration_id = f"migration_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            migration_path = Path(f"migrations/versions/{migration_id}.py")
            
            # Generate migration content
            migration_content = await self._generate_migration_content(changes, migration_id)
            
            # Write migration file
            migration_path.parent.mkdir(parents=True, exist_ok=True)
            with open(migration_path, 'w') as f:
                f.write(migration_content)
            
            return {
                "migration_id": migration_id,
                "migration_file": str(migration_path),
                "status": "created"
            }
            
        except Exception as e:
            log.error(f"Migration creation failed: {e}")
            return {"error": str(e)}

database_schema_agent = DatabaseSchemaAgent()
```

### B51: API Testing Agent
```python
# backend/agents/api_testing_agent.py
import asyncio
import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import time

from backend.core.logger import get_logger
from backend.core.ai_router import get_llm_adapter

log = get_logger(__name__)

class APITestingAgent:
    """
    Comprehensive API testing agent that performs automated testing,
    load testing, and API validation.
    """
    
    def __init__(self):
        self.ai_model = get_llm_adapter("gpt-4o-mini")
        self.base_url = "http://localhost:8000"
    
    async def run_comprehensive_tests(self, project_id: str, api_spec: Optional[Dict] = None) -> Dict:
        """
        Run comprehensive API tests
        """
        log.info(f"Starting comprehensive API tests for project: {project_id}")
        
        test_results = {
            "project_id": project_id,
            "test_timestamp": datetime.utcnow().isoformat(),
            "functional_tests": {},
            "performance_tests": {},
            "security_tests": {},
            "integration_tests": {},
            "test_summary": {},
            "recommendations": []
        }
        
        try:
            # 1. Discover API endpoints
            if not api_spec:
                api_spec = await self._discover_api_endpoints()
            
            # 2. Functional testing
            functional_results = await self._run_functional_tests(api_spec)
            test_results["functional_tests"] = functional_results
            
            # 3. Performance testing
            performance_results = await self._run_performance_tests(api_spec)
            test_results["performance_tests"] = performance_results
            
            # 4. Security testing
            security_results = await self._run_security_tests(api_spec)
            test_results["security_tests"] = security_results
            
            # 5. Integration testing
            integration_results = await self._run_integration_tests(api_spec)
            test_results["integration_tests"] = integration_results
            
            # 6. Generate test summary
            test_summary = self._generate_test_summary(test_results)
            test_results["test_summary"] = test_summary
            
            # 7. AI-generated recommendations
            recommendations = await self._generate_recommendations(test_results)
            test_results["recommendations"] = recommendations
            
            log.info("Comprehensive API testing completed")
            
        except Exception as e:
            log.error(f"API testing failed: {e}")
            test_results["error"] = str(e)
        
        return test_results
    
    async def _run_functional_tests(self, api_spec: Dict) -> Dict:
        """Run functional API tests"""
        results = {
            "endpoints_tested": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }
        
        for endpoint in api_spec.get("endpoints", []):
            method = endpoint["method"]
            path = endpoint["path"]
            
            # Test different scenarios
            test_cases = self._generate_test_cases(endpoint)
            
            for test_case in test_cases:
                test_result = await self._execute_test_case(method, path, test_case)
                results["test_details"].append(test_result)
                results["endpoints_tested"] += 1
                
                if test_result["status"] == "passed":
                    results["tests_passed"] += 1
                else:
                    results["tests_failed"] += 1
        
        return results
    
    async def _run_performance_tests(self, api_spec: Dict) -> Dict:
        """Run performance tests on API endpoints"""
        results = {
            "load_test_results": {},
            "response_times": {},
            "throughput": {},
            "error_rates": {}
        }
        
        # Select critical endpoints for load testing
        critical_endpoints = [ep for ep in api_spec.get("endpoints", []) if ep["method"] == "GET"][:3]
        
        for endpoint in critical_endpoints:
            path = endpoint["path"]
            
            # Run load test
            load_results = await self._run_load_test(endpoint, concurrent_users=10, duration=30)
            results["load_test_results"][path] = load_results
            
            # Measure response times
            response_times = await self._measure_response_times(endpoint, requests=50)
            results["response_times"][path] = response_times
        
        return results
    
    async def _run_security_tests(self, api_spec: Dict) -> Dict:
        """Run security tests on API endpoints"""
        results = {
            "authentication_tests": {},
            "authorization_tests": {},
            "injection_tests": {},
            "rate_limiting_tests": {}
        }
        
        for endpoint in api_spec.get("endpoints", []):
            path = endpoint["path"]
            
            # Test authentication
            auth_results = await self._test_authentication(endpoint)
            results["authentication_tests"][path] = auth_results
            
            # Test for injection vulnerabilities
            injection_results = await self._test_injections(endpoint)
            results["injection_tests"][path] = injection_results
            
            # Test rate limiting
            rate_limit_results = await self._test_rate_limiting(endpoint)
            results["rate_limiting_tests"][path] = rate_limit_results
        
        return results
    
    async def _execute_test_case(self, method: str, path: str, test_case: Dict) -> Dict:
        """Execute a single test case"""
        try:
            url = f"{self.base_url}{path}"
            
            # Prepare request
            kwargs = {
                "timeout": 30,
                "headers": test_case.get("headers", {}),
            }
            
            if test_case.get("json_data"):
                kwargs["json"] = test_case["json_data"]
            elif test_case.get("form_data"):
                kwargs["data"] = test_case["form_data"]
            
            # Execute request
            start_time = time.time()
            response = requests.request(method, url, **kwargs)
            end_time = time.time()
            
            # Validate response
            validation_result = self._validate_response(response, test_case.get("expected", {}))
            
            return {
                "test_name": test_case["name"],
                "method": method,
                "path": path,
                "status": "passed" if validation_result["valid"] else "failed",
                "response_time_ms": (end_time - start_time) * 1000,
                "status_code": response.status_code,
                "validation": validation_result,
                "error": validation_result.get("error")
            }
            
        except Exception as e:
            return {
                "test_name": test_case["name"],
                "method": method,
                "path": path,
                "status": "failed",
                "error": str(e)
            }

api_testing_agent = APITestingAgent()
```

### B52: Monitoring Agent
```python
# backend/agents/monitoring_agent.py
import asyncio
import json
import psutil
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque

from backend.core.redis import get_redis
from backend.core.database import get_session
from backend.core.logger import get_logger
from backend.models.analytics_model import SystemMetric, AlertRule

log = get_logger(__name__)

class MonitoringAgent:
    """
    Comprehensive monitoring agent that tracks system health,
    application metrics, and sends alerts based on thresholds.
    """
    
    def __init__(self):
        self.redis = get_redis()
        self.metrics_buffer = deque(maxlen=1000)
        self.alert_rules = []
        self.last_alert_times = {}
    
    async def start_monitoring(self, project_id: str) -> None:
        """
        Start continuous monitoring for a project
        """
        log.info(f"Starting monitoring for project: {project_id}")
        
        # Load alert rules
        await self._load_alert_rules()
        
        # Start monitoring loop
        while True:
            try:
                # Collect metrics
                metrics = await self._collect_metrics(project_id)
                
                # Store metrics
                await self._store_metrics(project_id, metrics)
                
                # Check alerts
                await self._check_alerts(project_id, metrics)
                
                # Generate insights
                insights = await self._generate_insights(project_id)
                if insights:
                    await self._store_insights(project_id, insights)
                
                # Wait before next collection
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                log.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_metrics(self, project_id: str) -> Dict:
        """Collect comprehensive system and application metrics"""
        timestamp = datetime.utcnow()
        
        # System metrics
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "network_io": dict(psutil.net_io_counters()._asdict()),
            "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        }
        
        # Application metrics
        app_metrics = {}
        if self.redis:
            # Redis metrics
            redis_info = await self.redis.info()
            app_metrics["redis"] = {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory": redis_info.get("used_memory", 0),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0)
            }
            
            # Cache hit rate
            hits = redis_info.get("keyspace_hits", 0)
            misses = redis_info.get("keyspace_misses", 0)
            total = hits + misses
            app_metrics["cache_hit_rate"] = (hits / total * 100) if total > 0 else 0
        
        # Database metrics
        try:
            with get_session() as session:
                # Active connections
                result = session.execute("SELECT count(*) FROM pg_stat_activity")
                app_metrics["db_connections"] = result.scalar()
                
                # Database size
                result = session.execute("SELECT pg_database_size(current_database())")
                app_metrics["db_size_bytes"] = result.scalar()
        except Exception as e:
            log.warning(f"Could not collect database metrics: {e}")
        
        # API metrics (from Redis if available)
        if self.redis:
            api_metrics = await self._collect_api_metrics()
            app_metrics.update(api_metrics)
        
        return {
            "timestamp": timestamp.isoformat(),
            "project_id": project_id,
            "system": system_metrics,
            "application": app_metrics
        }
    
    async def _check_alerts(self, project_id: str, metrics: Dict) -> None:
        """Check metrics against alert rules and send alerts"""
        current_time = datetime.utcnow()
        
        for rule in self.alert_rules:
            try:
                # Evaluate alert condition
                if self._evaluate_alert_condition(metrics, rule):
                    # Check cooldown period
                    last_alert = self.last_alert_times.get(rule["id"])
                    if last_alert and (current_time - last_alert).seconds < rule.get("cooldown", 300):
                        continue
                    
                    # Send alert
                    await self._send_alert(project_id, rule, metrics)
                    self.last_alert_times[rule["id"]] = current_time
                    
            except Exception as e:
                log.error(f"Alert evaluation failed for rule {rule.get('id')}: {e}")
    
    def _evaluate_alert_condition(self, metrics: Dict, rule: Dict) -> bool:
        """Evaluate if metrics trigger an alert condition"""
        try:
            metric_path = rule["metric_path"].split(".")
            value = metrics
            
            # Navigate to the metric value
            for key in metric_path:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return False
            
            # Evaluate condition
            threshold = rule["threshold"]
            operator = rule.get("operator", "gt")
            
            if operator == "gt":
                return float(value) > threshold
            elif operator == "lt":
                return float(value) < threshold
            elif operator == "eq":
                return float(value) == threshold
            elif operator == "gte":
                return float(value) >= threshold
            elif operator == "lte":
                return float(value) <= threshold
            
            return False
            
        except Exception as e:
            log.error(f"Condition evaluation error: {e}")
            return False
    
    async def _send_alert(self, project_id: str, rule: Dict, metrics: Dict) -> None:
        """Send alert notification"""
        try:
            alert_data = {
                "project_id": project_id,
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "severity": rule.get("severity", "warning"),
                "message": rule["message"],
                "timestamp": datetime.utcnow().isoformat(),
                "metrics_snapshot": metrics
            }
            
            # Store alert in Redis
            if self.redis:
                alert_key = f"alerts:{project_id}:{datetime.utcnow().strftime('%Y%m%d')}"
                await self.redis.lpush(alert_key, json.dumps(alert_data))
                await self.redis.expire(alert_key, 86400 * 7)  # Keep for 7 days
            
            # Log alert
            log.warning(f"ALERT [{rule['severity']}]: {rule['message']} for project {project_id}")
            
            # Send webhook notification (if configured)
            await self._send_webhook_notification(alert_data)
            
        except Exception as e:
            log.error(f"Alert sending failed: {e}")
    
    async def get_monitoring_dashboard(self, project_id: str) -> Dict:
        """Get monitoring dashboard data"""
        try:
            dashboard_data = {
                "project_id": project_id,
                "current_metrics": {},
                "historical_data": {},
                "active_alerts": [],
                "system_health": "unknown"
            }
            
            # Get current metrics
            if self.redis:
                current_key = f"metrics:{project_id}:current"
                current_data = await self.redis.get(current_key)
                if current_data:
                    dashboard_data["current_metrics"] = json.loads(current_data)
            
            # Get historical data (last 24 hours)
            historical_data = await self._get_historical_metrics(project_id, hours=24)
            dashboard_data["historical_data"] = historical_data
            
            # Get active alerts
            active_alerts = await self._get_active_alerts(project_id)
            dashboard_data["active_alerts"] = active_alerts
            
            # Calculate system health score
            health_score = self._calculate_health_score(
                dashboard_data["current_metrics"], 
                active_alerts
            )
            dashboard_data["system_health"] = health_score
            
            return dashboard_data
            
        except Exception as e:
            log.error(f"Dashboard data retrieval failed: {e}")
            return {"error": str(e)}

monitoring_agent = MonitoringAgent()
```

## 2. Advanced Tools va Utilities

### Advanced Code Quality Tools
```python
# backend/tools/code_quality_analyzer.py
import ast
import subprocess
from pathlib import Path
from typing import Dict, List

class CodeQualityAnalyzer:
    """Advanced code quality analysis with multiple metrics"""
    
    async def analyze_project(self, project_path: str) -> Dict:
        """Comprehensive code quality analysis"""
        results = {
            "complexity_metrics": await self._analyze_complexity(project_path),
            "code_duplication": await self._detect_duplication(project_path),
            "test_coverage": await self._measure_coverage(project_path),
            "documentation_coverage": await self._measure_docs_coverage(project_path),
            "security_issues": await self._security_scan(project_path),
            "performance_hotspots": await self._find_performance_issues(project_path)
        }
        
        results["quality_score"] = self._calculate_quality_score(results)
        return results
```

### AI Model Performance Optimizer
```python
# backend/tools/ai_optimizer.py
class AIModelOptimizer:
    """Optimize AI model performance and cost"""
    
    async def optimize_model_usage(self, usage_data: Dict) -> Dict:
        """Analyze and optimize AI model usage"""
        return {
            "cost_optimization": await self._optimize_costs(usage_data),
            "performance_tuning": await self._tune_performance(usage_data),
            "cache_strategies": await self._optimize_caching(usage_data),
            "rate_limiting": await self._optimize_rate_limits(usage_data)
        }
```

## Xulosa

Bu yangi AI agentlar va tools loyihangiz uchun quyidagi imkoniyatlarni taqdim etadi:

### Yangi Qo'shilgan Agentlar:
- **B47**: Security Scanner Agent - Xavfsizlik tahlili
- **B48**: Performance Analyzer Agent - Performance monitoring
- **B49**: Documentation Generator Agent - Avtomatik hujjatlashtirish
- **B50**: Database Schema Agent - Ma'lumotlar bazasi boshqaruvi
- **B51**: API Testing Agent - API testlash
- **B52**: Monitoring Agent - Real-time monitoring

### Asosiy Afzalliklar:
1. **Xavfsizlik**: Comprehensive security scanning va vulnerability detection
2. **Performance**: Real-time performance monitoring va optimization
3. **Documentation**: Automatic documentation generation
4. **Quality**: Advanced code quality analysis
5. **Testing**: Automated API testing va validation
6. **Monitoring**: Proactive system health monitoring

### Implementatsiya Rejalari:
- **Hafta 1-2**: Security Scanner va Performance Analyzer
- **Hafta 3-4**: Documentation Generator va Database Schema Agent  
- **Hafta 5-6**: API Testing Agent va Monitoring Agent
- **Hafta 7-8**: Integration va fine-tuning
