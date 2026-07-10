"""
Rankivo — Parallel Agent Orchestrator
Runs multiple SEO analysis modules simultaneously using Python threads.
This is the architectural equivalent of claude-seo's parallel sub-agent dispatch.

How it works:
1. Register analysis modules as "agents" with inputs/dependencies
2. Build a dependency graph
3. Execute independent agents in parallel using ThreadPoolExecutor
4. Collect and synthesize results into a unified report

Unlike claude-seo which uses Claude Code's native agent spawning,
this uses Python's built-in threading for parallel execution.
"""
import importlib
import time
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from config import _safe_print


# ──────────────────────────────────────────────
# Agent Registry
# ──────────────────────────────────────────────

class AgentDefinition:
    """Defines an analysis agent that can be run by the orchestrator."""
    
    def __init__(
        self,
        name: str,
        module_path: str,
        function_name: str,
        dependencies: list[str] = None,
        description: str = "",
        input_keys: list[str] = None,
        timeout: int = 120,
    ):
        self.name = name
        self.module_path = module_path
        self.function_name = function_name
        self.dependencies = dependencies or []
        self.description = description
        self.input_keys = input_keys or ["url"]
        self.timeout = timeout


# Built-in agent definitions
BUILTIN_AGENTS = {
    "seo_audit": AgentDefinition(
        name="seo_audit",
        module_path="seo_audit",
        function_name="audit_url",
        description="On-page SEO analysis (meta tags, headings, links, images)",
        timeout=30,
    ),
    "technical_seo": AgentDefinition(
        name="technical_seo",
        module_path="technical_seo",
        function_name="full_technical_audit",
        description="Technical SEO (robots.txt, sitemap, structured data, CWV)",
        timeout=60,
    ),
    "eeat": AgentDefinition(
        name="eeat",
        module_path="eeat",
        function_name="analyze_eear_t",
        description="E-E-A-T analysis (Experience, Expertise, Authority, Trust)",
        timeout=30,
    ),
    "schema_audit": AgentDefinition(
        name="schema_audit",
        module_path="schema_audit",
        function_name="audit_schema",
        description="Deep Schema.org audit with deprecated type tracking",
        timeout=30,
    ),
    "geo_audit": AgentDefinition(
        name="geo_audit",
        module_path="geo_audit",
        function_name="audit_geo",
        description="GEO/AEO audit (AI search readiness, passage citability)",
        timeout=30,
    ),
    "seo_images": AgentDefinition(
        name="seo_images",
        module_path="seo_images",
        function_name="analyze_images",
        description="Image optimization (alt text, formats, responsive, lazy loading)",
        timeout=60,
    ),
    "sitemap_audit": AgentDefinition(
        name="sitemap_audit",
        module_path="sitemap_audit",
        function_name="audit_sitemap",
        description="Sitemap analysis and validation",
        timeout=30,
    ),
    "hreflang_audit": AgentDefinition(
        name="hreflang_audit",
        module_path="hreflang_audit",
        function_name="audit_hreflang",
        description="Hreflang / international SEO validation",
        timeout=30,
    ),
    "local_seo": AgentDefinition(
        name="local_seo",
        module_path="local_seo",
        function_name="audit_local_seo",
        description="Local SEO (GBP, NAP, reviews, local schema)",
        timeout=30,
    ),
    "ecommerce_seo": AgentDefinition(
        name="ecommerce_seo",
        module_path="ecommerce_seo",
        function_name="audit_ecommerce",
        description="E-commerce SEO (product schema, pricing, marketplace)",
        timeout=30,
    ),
    "sxo_audit": AgentDefinition(
        name="sxo_audit",
        module_path="sxo_audit",
        function_name="audit_sxo",
        description="Search Experience Optimization (page type, intent, personas)",
        timeout=30,
    ),
    "backlinks": AgentDefinition(
        name="backlinks",
        module_path="backlinks",
        function_name="analyze_backlinks",
        description="Backlink profile analysis (Bing, Common Crawl, toxic detection)",
        input_keys=["domain"],
        timeout=60,
    ),
}


# ──────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────

class ParallelOrchestrator:
    """
    Runs multiple SEO analysis agents in parallel and synthesizes results.
    
    Usage:
        orch = ParallelOrchestrator(url="https://example.com")
        orch.register("seo_audit")  # or register_all() for everything
        results = orch.run_parallel(max_workers=6)
        report = orch.synthesize()
    """
    
    def __init__(self, url: str = "", domain: str = "", max_workers: int = 6):
        self.url = url
        self.domain = domain or self._extract_domain(url)
        self.max_workers = max_workers
        self.agents: dict[str, AgentDefinition] = {}
        self.results: dict[str, dict] = {}
        self.errors: dict[str, str] = {}
        self.timings: dict[str, float] = {}
        self._lock = Lock()
    
    def _extract_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        try:
            return urlparse(url).netloc
        except Exception:
            return url
    
    def register(self, agent_name: str):
        """Register a built-in agent for execution."""
        if agent_name in BUILTIN_AGENTS:
            self.agents[agent_name] = BUILTIN_AGENTS[agent_name]
        else:
            _safe_print(f"[orchestrator] Unknown agent: {agent_name}")
    
    def register_all(self, exclude: list[str] = None):
        """Register all built-in agents."""
        exclude = exclude or []
        for name, agent in BUILTIN_AGENTS.items():
            if name not in exclude:
                self.agents[name] = agent
    
    def register_custom(self, agent: AgentDefinition):
        """Register a custom agent."""
        self.agents[agent.name] = agent
    
    def _get_agent_args(self, agent: AgentDefinition) -> dict:
        """Build the arguments for an agent function."""
        args = {}
        for key in agent.input_keys:
            if key == "url":
                args["url"] = self.url
            elif key == "domain":
                args["domain"] = self.domain
        return args
    
    def _run_agent(self, agent_name: str) -> tuple[str, dict, float]:
        """Run a single agent. Returns (name, result, elapsed_seconds)."""
        agent = self.agents[agent_name]
        start = time.time()
        
        try:
            # Dynamic import
            module = importlib.import_module(agent.module_path)
            func = getattr(module, agent.function_name)
            
            # Build arguments
            kwargs = self._get_agent_args(agent)
            
            # Run with timeout (thread-level, not function-level)
            result = func(**kwargs)
            elapsed = round(time.time() - start, 2)
            
            return (agent_name, result, elapsed)
        
        except Exception as e:
            elapsed = round(time.time() - start, 2)
            error_result = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "agent": agent_name,
            }
            return (agent_name, error_result, elapsed)
    
    def run_parallel(self, agents_to_run: list[str] = None) -> dict:
        """
        Run all registered agents in parallel using ThreadPoolExecutor.
        
        Args:
            agents_to_run: Optional subset of agent names to run.
                          If None, runs all registered agents.
        
        Returns:
            dict mapping agent_name -> result
        """
        if agents_to_run is None:
            agents_to_run = list(self.agents.keys())
        
        # Filter to only registered agents
        agents_to_run = [a for a in agents_to_run if a in self.agents]
        
        if not agents_to_run:
            _safe_print("[orchestrator] No agents registered to run")
            return {}
        
        _safe_print(f"[orchestrator] Running {len(agents_to_run)} agents in parallel (max_workers={self.max_workers})...")
        
        total_start = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all agents
            future_to_agent = {
                executor.submit(self._run_agent, name): name
                for name in agents_to_run
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    name, result, elapsed = future.result()
                    with self._lock:
                        self.results[name] = result
                        self.timings[name] = elapsed
                    
                    status = "✅" if "error" not in result else "❌"
                    _safe_print(f"  {status} {name}: {elapsed}s")
                
                except Exception as e:
                    with self._lock:
                        self.errors[agent_name] = str(e)
                        self.timings[agent_name] = 0
                    _safe_print(f"  ❌ {agent_name}: {e}")
        
        total_elapsed = round(time.time() - total_start, 2)
        _safe_print(f"[orchestrator] All agents completed in {total_elapsed}s")
        
        return self.results
    
    def synthesize(self) -> dict:
        """
        Synthesize all agent results into a unified report.
        
        Returns a comprehensive audit report combining all modules.
        """
        # Calculate overall score
        scores = []
        all_issues = []
        all_recommendations = []
        
        module_scores = {}
        module_issue_counts = {}
        
        for name, result in self.results.items():
            if isinstance(result, dict) and "error" not in result:
                # Extract score
                score = result.get("score", result.get("composite_score", result.get("overall_score")))
                if score is not None:
                    scores.append(score)
                    module_scores[name] = score
                
                # Extract issues
                issues = result.get("issues", [])
                if issues:
                    all_issues.extend(issues)
                    module_issue_counts[name] = len(issues)
                
                # Extract recommendations
                recs = result.get("recommendations", [])
                if recs:
                    all_recommendations.extend(recs)
        
        # Calculate weighted average score
        overall_score = round(sum(scores) / len(scores)) if scores else 0
        
        # Categorize issues
        critical = [i for i in all_issues if i.get("severity") == "critical"]
        warnings = [i for i in all_issues if i.get("severity") == "warning"]
        infos = [i for i in all_issues if i.get("severity") == "info"]
        
        # Health grade
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 80:
            grade = "A"
        elif overall_score >= 70:
            grade = "B+"
        elif overall_score >= 60:
            grade = "B"
        elif overall_score >= 50:
            grade = "C+"
        elif overall_score >= 40:
            grade = "C"
        elif overall_score >= 30:
            grade = "D"
        else:
            grade = "F"
        
        report = {
            "url": self.url,
            "domain": self.domain,
            "generated_at": datetime.now().isoformat(),
            
            "overall_score": overall_score,
            "grade": grade,
            
            "module_scores": module_scores,
            "module_timings": self.timings,
            "modules_run": len(self.results),
            "modules_failed": len(self.errors),
            
            "issues_summary": {
                "total": len(all_issues),
                "critical": len(critical),
                "warnings": len(warnings),
                "info": len(infos),
            },
            
            "critical_issues": critical[:20],
            "warnings": warnings[:20],
            "info_notices": infos[:15],
            
            "recommendations": all_recommendations[:20],
            
            "module_results": self.results,
            
            "errors": self.errors,
        }
        
        return report
    
    def get_status(self) -> dict:
        """Get orchestrator status and available agents."""
        return {
            "url": self.url,
            "domain": self.domain,
            "registered_agents": list(self.agents.keys()),
            "total_agents": len(self.agents),
            "results_collected": len(self.results),
            "errors": len(self.errors),
            "available_agents": {
                name: {
                    "description": agent.description,
                    "module": agent.module_path,
                    "function": agent.function_name,
                    "dependencies": agent.dependencies,
                }
                for name, agent in BUILTIN_AGENTS.items()
            },
        }


# ──────────────────────────────────────────────
# Convenience Functions
# ──────────────────────────────────────────────

def run_full_audit(url: str, exclude: list[str] = None, max_workers: int = 6) -> dict:
    """
    Run a complete SEO audit with all modules in parallel.
    
    Args:
        URL to audit
        exclude: Agent names to skip (e.g., ['backlinks'] if no Bing key)
        max_workers: Max parallel threads
    
    Returns:
        Unified audit report
    """
    orch = ParallelOrchestrator(url=url, max_workers=max_workers)
    orch.register_all(exclude=exclude or [])
    orch.run_parallel()
    return orch.synthesize()


def run_focused_audit(url: str, modules: list[str], max_workers: int = 6) -> dict:
    """
    Run a focused audit with specific modules only.
    
    Args:
        url: URL to audit
        modules: List of agent names to run
        max_workers: Max parallel threads
    
    Returns:
        Focused audit report
    """
    orch = ParallelOrchestrator(url=url, max_workers=max_workers)
    for mod in modules:
        orch.register(mod)
    orch.run_parallel()
    return orch.synthesize()


def get_orchestrator_info() -> dict:
    """Get information about the orchestrator and available agents."""
    orch = ParallelOrchestrator()
    return orch.get_status()
