"""Integration tests for CLI binary.

These tests call the actual CLI binary to verify end-to-end behavior.
Requires the CLI to be built first: make build
"""

import os
import subprocess
import pytest


CLI_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "dist", "opennotebook", "opennotebook")


def run_cli(args, check=True):
    """Run CLI command and return result."""
    full_args = [CLI_PATH] + args
    result = subprocess.run(
        full_args,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__)),
    )
    if check and result.returncode == 2:
        pytest.fail(f"Argparse error: {result.stderr}")
    return result


def assert_no_argparse_error(result):
    """Assert result doesn't have argparse error (returncode 2)."""
    has_argparse_error = "usage:" in result.stderr.lower() and result.returncode == 2
    assert not has_argparse_error, f"Argparse error: {result.stderr}"


class TestCliHelp:
    """Test --help flag."""

    def test_help_flag(self):
        """--help should show usage."""
        result = run_cli(["--help"])
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "opennotebook" in result.stdout.lower()

    def test_version_flag(self):
        """--version should show version."""
        result = run_cli(["--version"])
        assert result.returncode == 0
        assert "opennotebook" in result.stdout.lower()

    def test_no_command_shows_help(self):
        """Running without command should show help."""
        result = run_cli([], check=False)
        output = result.stdout + result.stderr
        assert "usage:" in output.lower() or result.returncode == 0


class TestSubcommandsHelp:
    """Test subcommands show help when called without required args."""

    def test_notebook_without_args_shows_help(self):
        """'notebook' without args should show help."""
        result = run_cli(["notebook"])
        assert result.returncode == 0
        assert "notebook" in result.stdout.lower()
        assert "list" in result.stdout or "create" in result.stdout

    def test_source_without_args_shows_help(self):
        """'source' without args should show help."""
        result = run_cli(["source"])
        assert result.returncode == 0
        assert "source" in result.stdout.lower()

    def test_note_without_args_shows_help(self):
        """'note' without args should show help."""
        result = run_cli(["note"])
        assert result.returncode == 0
        assert "note" in result.stdout.lower()

    def test_chat_without_args_shows_help(self):
        """'chat' without args should show help."""
        result = run_cli(["chat"])
        assert result.returncode == 0
        assert "chat" in result.stdout.lower()

    def test_podcast_without_args_shows_help(self):
        """'podcast' without args should show help."""
        result = run_cli(["podcast"])
        assert result.returncode == 0
        assert "podcast" in result.stdout.lower()

    def test_search_without_args_shows_help(self):
        """'search' without args should show help."""
        result = run_cli(["search"])
        assert result.returncode == 0
        assert "search" in result.stdout.lower()

    def test_credential_without_args_shows_help(self):
        """'credential' without args should show help."""
        result = run_cli(["credential"])
        assert result.returncode == 0
        assert "credential" in result.stdout.lower()

    def test_model_without_args_shows_help(self):
        """'model' without args should show help."""
        result = run_cli(["model"])
        assert result.returncode == 0
        assert "model" in result.stdout.lower()


class TestNotebookActions:
    """Test notebook subcommand all actions."""

    def test_notebook_list(self):
        """'notebook list' should parse correctly."""
        result = run_cli(["notebook", "list"])
        assert_no_argparse_error(result)

    def test_notebook_create(self):
        """'notebook create' should parse correctly."""
        result = run_cli(["notebook", "create", "test-notebook"])
        assert_no_argparse_error(result)

    def test_notebook_create_with_description(self):
        """'notebook create name --description desc' should parse correctly."""
        result = run_cli(["notebook", "create", "test", "--description", "my desc"])
        assert_no_argparse_error(result)

    def test_notebook_get(self):
        """'notebook get nb-123' should parse correctly."""
        result = run_cli(["notebook", "get", "nb-123"])
        assert_no_argparse_error(result)

    def test_notebook_update(self):
        """'notebook update nb-123 --description x' should parse correctly."""
        result = run_cli(["notebook", "update", "nb-123", "--description", "new"])
        assert_no_argparse_error(result)

    def test_notebook_update_archived(self):
        """'notebook update nb-123 --archived' should parse correctly."""
        result = run_cli(["notebook", "update", "nb-123", "--archived"])
        assert_no_argparse_error(result)

    def test_notebook_delete(self):
        """'notebook delete nb-123' should parse correctly."""
        result = run_cli(["notebook", "delete", "nb-123"])
        assert_no_argparse_error(result)


class TestSourceActions:
    """Test source subcommand all actions."""

    def test_source_list(self):
        """'source list' should parse correctly."""
        result = run_cli(["source", "list"])
        assert_no_argparse_error(result)

    def test_source_list_with_notebook_id(self):
        """'source list nb-123' should parse correctly."""
        result = run_cli(["source", "list", "nb-123"])
        assert_no_argparse_error(result)

    def test_source_add_file(self):
        """'source add nb-123 /path/to/file.pdf' should parse correctly."""
        result = run_cli(["source", "add", "nb-123", "/path/to/file.pdf"])
        assert_no_argparse_error(result)

    def test_source_add_url(self):
        """'source add nb-123 https://example.com/file.pdf' should parse correctly."""
        result = run_cli(["source", "add", "nb-123", "https://example.com/file.pdf"])
        assert_no_argparse_error(result)

    def test_source_get(self):
        """'source get src-456' should parse correctly."""
        result = run_cli(["source", "get", "src-456"])
        assert_no_argparse_error(result)

    def test_source_delete(self):
        """'source delete src-456' should parse correctly."""
        result = run_cli(["source", "delete", "src-456"])
        assert_no_argparse_error(result)


class TestNoteActions:
    """Test note subcommand all actions."""

    def test_note_list(self):
        """'note list' should parse correctly."""
        result = run_cli(["note", "list"])
        assert_no_argparse_error(result)

    def test_note_list_with_source_id(self):
        """'note list src-123' should parse correctly."""
        result = run_cli(["note", "list", "src-123"])
        assert_no_argparse_error(result)

    def test_note_create(self):
        """'note create src-123 "My Title"' should parse correctly."""
        result = run_cli(["note", "create", "src-123", "My Title"])
        assert_no_argparse_error(result)

    def test_note_create_with_content(self):
        """'note create src-123 title --content body' should parse correctly."""
        result = run_cli(["note", "create", "src-123", "Title", "--content", "body"])
        assert_no_argparse_error(result)

    def test_note_get(self):
        """'note get note-456' should parse correctly."""
        result = run_cli(["note", "get", "note-456"])
        assert_no_argparse_error(result)

    def test_note_update(self):
        """'note update note-456 --content x' should parse correctly."""
        result = run_cli(["note", "update", "note-456", "--content", "new content"])
        assert_no_argparse_error(result)

    def test_note_delete(self):
        """'note delete note-456' should parse correctly."""
        result = run_cli(["note", "delete", "note-456"])
        assert_no_argparse_error(result)


class TestChatActions:
    """Test chat subcommand all scenarios."""

    def test_chat_with_args(self):
        """'chat nb-123 hello world' should parse correctly."""
        result = run_cli(["chat", "nb-123", "hello world"])
        assert_no_argparse_error(result)

    def test_chat_with_model(self):
        """'chat nb-123 hello --model gpt-4' should parse correctly."""
        result = run_cli(["chat", "nb-123", "hello", "--model", "gpt-4"])
        assert_no_argparse_error(result)

    def test_chat_missing_message_shows_help(self):
        """'chat nb-123' without message should show help."""
        result = run_cli(["chat", "nb-123"])
        assert result.returncode == 0
        assert "chat" in result.stdout.lower()


class TestPodcastActions:
    """Test podcast subcommand all actions."""

    def test_podcast_list(self):
        """'podcast list' should parse correctly."""
        result = run_cli(["podcast", "list"], check=False)
        assert_no_argparse_error(result)

    def test_podcast_list_with_notebook_id(self):
        """'podcast list nb-123' should parse correctly."""
        result = run_cli(["podcast", "list", "nb-123"], check=False)
        assert_no_argparse_error(result)

    def test_podcast_create(self):
        """'podcast create nb-123' should parse correctly."""
        result = run_cli(["podcast", "create", "nb-123"], check=False)
        assert_no_argparse_error(result)

    def test_podcast_create_with_title(self):
        """'podcast create nb-123 --title My Podcast' should parse correctly."""
        result = run_cli(["podcast", "create", "nb-123", "--title", "My Podcast"], check=False)
        assert_no_argparse_error(result)

    def test_podcast_get(self):
        """'podcast get ep-456' should parse correctly."""
        result = run_cli(["podcast", "get", "ep-456"], check=False)
        assert_no_argparse_error(result)

    def test_podcast_retry(self):
        """'podcast retry ep-456' should parse correctly."""
        result = run_cli(["podcast", "retry", "ep-456"], check=False)
        assert_no_argparse_error(result)


class TestSearchActions:
    """Test search subcommand all scenarios."""

    def test_search_with_query(self):
        """'search hello world' should parse correctly."""
        result = run_cli(["search", "hello world"])
        assert_no_argparse_error(result)

    def test_search_with_type(self):
        """'search hello --type vector' should parse correctly."""
        result = run_cli(["search", "hello", "--type", "vector"])
        assert_no_argparse_error(result)

    def test_search_with_limit(self):
        """'search hello --limit 5' should parse correctly."""
        result = run_cli(["search", "hello", "--limit", "5"])
        assert_no_argparse_error(result)

    def test_search_without_query_shows_help(self):
        """'search' without query should show help."""
        result = run_cli(["search"])
        assert result.returncode == 0
        assert "search" in result.stdout.lower()


class TestCredentialActions:
    """Test credential subcommand all actions."""

    def test_credential_list(self):
        """'credential list' should parse correctly."""
        result = run_cli(["credential", "list"])
        assert_no_argparse_error(result)

    def test_credential_create(self):
        """'credential create --name x --provider openai' should parse correctly."""
        result = run_cli(["credential", "create", "--name", "my-key", "--provider", "openai"])
        assert_no_argparse_error(result)

    def test_credential_create_with_api_key(self):
        """'credential create --name x --provider openai --api-key sk-xxx' should parse."""
        result = run_cli(["credential", "create", "--name", "my-key", "--provider", "openai", "--api-key", "sk-123"])
        assert_no_argparse_error(result)

    def test_credential_test(self):
        """'credential test cred-456' should parse correctly."""
        result = run_cli(["credential", "test", "cred-456"])
        assert_no_argparse_error(result)

    def test_credential_delete(self):
        """'credential delete cred-456' should parse correctly."""
        result = run_cli(["credential", "delete", "cred-456"])
        assert_no_argparse_error(result)


class TestModelActions:
    """Test model subcommand all actions."""

    def test_model_list(self):
        """'model list' should parse correctly."""
        result = run_cli(["model", "list"])
        assert_no_argparse_error(result)

    def test_model_list_with_provider(self):
        """'model list --provider openai' should parse correctly."""
        result = run_cli(["model", "list", "--provider", "openai"])
        assert_no_argparse_error(result)

    def test_model_discover(self):
        """'model discover --provider openai' should parse correctly."""
        result = run_cli(["model", "discover", "--provider", "openai"])
        assert_no_argparse_error(result)


class TestGlobalFlags:
    """Test global flags."""

    def test_custom_server_flag(self):
        """--server flag should be accepted."""
        result = run_cli(["--server", "http://custom:8080", "notebook"])
        assert_no_argparse_error(result)

    def test_custom_password_flag(self):
        """--password flag should be accepted."""
        result = run_cli(["--password", "secret", "notebook"])
        assert_no_argparse_error(result)

    def test_combined_flags(self):
        """Multiple global flags should work together."""
        result = run_cli([
            "--server", "http://localhost:5055",
            "--password", "open-notebook-change-me",
            "notebook"
        ])
        assert_no_argparse_error(result)

    def test_server_and_action_together(self):
        """--server with action should work."""
        result = run_cli(["--server", "http://custom:8080", "notebook", "list"])
        assert_no_argparse_error(result)

    def test_password_and_action_together(self):
        """--password with action should work."""
        result = run_cli(["--password", "secret", "notebook", "list"])
        assert_no_argparse_error(result)
