"""
Unit tests puros: no requieren credenciales ni conexión a Azure.
Corren en cualquier agente Jenkins en segundos, ideal para feedback rápido.
"""

import json

import pytest

from src.azure_helpers import (
    build_resource_name,
    build_storage_account_name,
    is_valid_storage_account_name,
    merge_tags,
    parse_terraform_output,
)


class TestBuildResourceName:
    def test_builds_expected_format(self):
        assert build_resource_name("myapp", "test", "rg", "ab12cd") == "rg-myapp-test-ab12cd"

    def test_lowercases_output(self):
        assert build_resource_name("MyApp", "TEST", "RG", "AB12CD") == "rg-myapp-test-ab12cd"

    @pytest.mark.parametrize("project,env,rtype,suffix", [
        ("", "test", "rg", "abc"),
        ("proj", "", "rg", "abc"),
        ("proj", "test", "", "abc"),
        ("proj", "test", "rg", ""),
    ])
    def test_raises_on_missing_component(self, project, env, rtype, suffix):
        with pytest.raises(ValueError):
            build_resource_name(project, env, rtype, suffix)


class TestBuildStorageAccountName:
    def test_strips_invalid_characters(self):
        name = build_storage_account_name("my-project_01", "ab12cd")
        assert "-" not in name
        assert "_" not in name

    def test_respects_max_length(self):
        name = build_storage_account_name("a" * 40, "suffix")
        assert len(name) <= 24

    def test_is_valid_storage_account_name(self):
        assert is_valid_storage_account_name(build_storage_account_name("myapp", "ab12cd"))

    def test_rejects_uppercase_or_symbols(self):
        assert not is_valid_storage_account_name("My-Storage!")


class TestMergeTags:
    def test_merges_without_mutating_original(self):
        base = {"env": "test"}
        extra = {"owner": "jenkins"}
        merged = merge_tags(base, extra)

        assert merged == {"env": "test", "owner": "jenkins"}
        assert base == {"env": "test"}  # no debe mutarse

    def test_extra_overrides_base(self):
        base = {"env": "test"}
        merged = merge_tags(base, {"env": "prod"})
        assert merged["env"] == "prod"

    def test_no_extra_tags_returns_copy_of_base(self):
        base = {"env": "test"}
        merged = merge_tags(base)
        assert merged == base
        assert merged is not base


class TestParseTerraformOutput:
    def test_extracts_value(self):
        raw = json.dumps({"resource_group_name": {"value": "rg-test-123"}})
        assert parse_terraform_output(raw, "resource_group_name") == "rg-test-123"

    def test_raises_keyerror_for_missing_key(self):
        raw = json.dumps({"foo": {"value": "bar"}})
        with pytest.raises(KeyError):
            parse_terraform_output(raw, "missing_key")
