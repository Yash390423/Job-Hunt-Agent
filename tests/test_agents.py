"""Tests for AI agents."""
import pytest
from agents.jd_analyst import get_jd_analyst_agent
from agents.resume_cl_agent import get_resume_cl_agent
from agents.messaging_agent import get_messaging_agent


def test_jd_analyst_agent_creation():
    """Test JD analyst agent can be created."""
    agent = get_jd_analyst_agent()
    assert agent is not None
    assert agent.role == "Job Description Analyst"


def test_resume_agent_creation():
    """Test resume agent can be created."""
    agent = get_resume_cl_agent()
    assert agent is not None
    assert "Resume" in agent.role


def test_messaging_agent_creation():
    """Test messaging agent can be created."""
    agent = get_messaging_agent()
    assert agent is not None
    assert "Outreach" in agent.role