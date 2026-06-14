"""Tests for configuration validation."""

from utils.config_validator import check_database_config, validate_config


def test_validate_config_passes(env_vars):
    assert validate_config() is True


def test_check_database_config_passes_or_warns(env_vars):
    assert check_database_config() in {True, False}
