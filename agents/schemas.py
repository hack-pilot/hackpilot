from typing import List, Optional
from pydantic import BaseModel, Field

class ProjectAnalysis(BaseModel):
    """Schema for Project Analyzer output."""
    name: str = Field(..., description="Project name")
    tech_stack: List[str] = Field(..., description="Detected technologies (e.g., Python, React)")
    domain: str = Field(..., description="Project domain (e.g., AI, Fintech, E-commerce)")
    completion_percentage: float = Field(..., description="Estimated completion percentage (0-100)")
    remaining_tasks: List[str] = Field(..., description="List of incomplete features or TODOs")
    estimated_hours_left: float = Field(..., description="Estimated time to reach 100% completion")

class HackathonMatch(BaseModel):
    """Schema for a single hackathon match."""
    name: str = Field(..., description="Hackathon name")
    url: str = Field(..., description="Link to hackathon page")
    deadline: str = Field(..., description="Submission deadline ISO string")
    match_score: int = Field(..., description="Relevance score (1-10)")
    reasoning: str = Field(..., description="Why this hackathon matches the project")

class HackathonScoutOutput(BaseModel):
    """Schema for Hackathon Scout output."""
    matches: List[HackathonMatch] = Field(..., description="Top matching hackathons")

class CodeUpdate(BaseModel):
    """Schema for Code Completer output."""
    files_modified: List[str] = Field(..., description="List of paths modified")
    pr_url: str = Field(..., description="Link to the created PR")
    summary: str = Field(..., description="Brief explanation of the changes made")
