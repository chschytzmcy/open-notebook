"""Tests for CLI argument parsing and command registration."""

import pytest
import sys
from io import StringIO
from unittest.mock import MagicMock, patch

sys.path.insert(0, "src")

from opennotebook.main import create_parser
from opennotebook.client import OpenNotebookClient


class TestNotebookCommand:
    """Test notebook subcommand parsing."""

    def test_notebook_list_action(self):
        """'notebook list' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["notebook", "list"])
        assert args.action == "list"
        assert args.handler is not None

    def test_notebook_create_action(self):
        """'notebook create' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["notebook", "create", "test-notebook"])
        assert args.action == "create"
        assert args.id_or_name == "test-notebook"

    def test_notebook_create_with_description(self):
        """'notebook create name --description desc' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["notebook", "create", "test", "--description", "my desc"])
        assert args.action == "create"
        assert args.id_or_name == "test"
        assert args.description == "my desc"

    def test_notebook_get_action(self):
        """'notebook get' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["notebook", "get", "nb-123"])
        assert args.action == "get"
        assert args.id_or_name == "nb-123"

    def test_notebook_update_action(self):
        """'notebook update' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["notebook", "update", "nb-123", "--description", "new desc"])
        assert args.action == "update"
        assert args.id_or_name == "nb-123"
        assert args.description == "new desc"

    def test_notebook_delete_action(self):
        """'notebook delete' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["notebook", "delete", "nb-123"])
        assert args.action == "delete"
        assert args.id_or_name == "nb-123"

    def test_notebook_archived_flag(self):
        """'notebook update' with --archived flag."""
        parser = create_parser()
        args = parser.parse_args(["notebook", "update", "nb-123", "--archived"])
        assert args.archived is True


class TestSourceCommand:
    """Test source subcommand parsing."""

    def test_source_list_action(self):
        """'source list' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["source", "list"])
        assert args.action == "list"

    def test_source_add_action(self):
        """'source add' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["source", "add", "nb-123", "/path/to/file.pdf"])
        assert args.action == "add"
        assert args.notebook_id == "nb-123"
        assert args.path == "/path/to/file.pdf"

    def test_source_add_with_url(self):
        """'source add nb url' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["source", "add", "nb-123", "https://example.com/file.pdf"])
        assert args.action == "add"
        assert args.notebook_id == "nb-123"
        assert args.path == "https://example.com/file.pdf"

    def test_source_get_action(self):
        """'source get' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["source", "get", "src-456"])
        assert args.action == "get"
        # Note: source_id is passed as notebook_id in get/delete
        assert args.notebook_id == "src-456"

    def test_source_delete_action(self):
        """'source delete' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["source", "delete", "src-456"])
        assert args.action == "delete"
        assert args.notebook_id == "src-456"


class TestNoteCommand:
    """Test note subcommand parsing."""

    def test_note_list_action(self):
        """'note list' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["note", "list"])
        assert args.action == "list"

    def test_note_list_with_source_id(self):
        """'note list src-123' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["note", "list", "src-123"])
        assert args.action == "list"
        assert args.source_id == "src-123"

    def test_note_create_action(self):
        """'note create' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["note", "create", "src-123", "My Note Title"])
        assert args.action == "create"
        assert args.source_id == "src-123"
        assert args.id_or_title == "My Note Title"

    def test_note_create_with_content(self):
        """'note create src title --content body' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["note", "create", "src-123", "Title", "--content", "body"])
        assert args.action == "create"
        assert args.content == "body"

    def test_note_get_action(self):
        """'note get' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["note", "get", "note-456"])
        assert args.action == "get"
        # Note: source_id is passed as first positional arg
        assert args.source_id == "note-456"

    def test_note_update_action(self):
        """'note update' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["note", "update", "note-456", "--content", "new content"])
        assert args.action == "update"
        assert args.source_id == "note-456"
        assert args.content == "new content"

    def test_note_delete_action(self):
        """'note delete' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["note", "delete", "note-456"])
        assert args.action == "delete"
        assert args.source_id == "note-456"


class TestChatCommand:
    """Test chat subcommand parsing."""

    def test_chat_with_args(self):
        """'chat nb-123 hello' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["chat", "nb-123", "hello world"])
        assert args.notebook_id == "nb-123"
        assert args.message == "hello world"

    def test_chat_with_model_override(self):
        """'chat' with --model should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["chat", "nb-123", "hello", "--model", "gpt-4"])
        assert args.notebook_id == "nb-123"
        assert args.message == "hello"
        assert args.model == "gpt-4"


class TestPodcastCommand:
    """Test podcast subcommand parsing."""

    def test_podcast_list_action(self):
        """'podcast list' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["podcast", "list"])
        assert args.action == "list"

    def test_podcast_list_with_notebook_id(self):
        """'podcast list nb-123' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["podcast", "list", "nb-123"])
        assert args.action == "list"
        assert args.notebook_id == "nb-123"

    def test_podcast_create_action(self):
        """'podcast create' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["podcast", "create", "nb-123"])
        assert args.action == "create"
        assert args.notebook_id == "nb-123"

    def test_podcast_create_with_title(self):
        """'podcast create nb-123 --title foo' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["podcast", "create", "nb-123", "--title", "My Podcast"])
        assert args.action == "create"
        assert args.notebook_id == "nb-123"
        assert args.title == "My Podcast"

    def test_podcast_get_action(self):
        """'podcast get' should parse correctly with positional args."""
        parser = create_parser()
        # For get/retry, the first arg is used as notebook_id and episode_id
        # (handler uses `args.episode_id or args.notebook_id`)
        args = parser.parse_args(["podcast", "get", "ep-456"])
        assert args.action == "get"
        # Handler will use notebook_id as fallback for episode_id

    def test_podcast_retry_action(self):
        """'podcast retry' should parse correctly with positional args."""
        parser = create_parser()
        args = parser.parse_args(["podcast", "retry", "ep-456"])
        assert args.action == "retry"


class TestSearchCommand:
    """Test search subcommand parsing."""

    def test_search_with_query(self):
        """'search hello' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["search", "hello world"])
        assert args.query == "hello world"

    def test_search_with_type_flag(self):
        """'search hello --type vector' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["search", "hello", "--type", "vector"])
        assert args.query == "hello"
        assert args.type == "vector"

    def test_search_with_limit_flag(self):
        """'search hello --limit 5' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["search", "hello", "--limit", "5"])
        assert args.query == "hello"
        assert args.limit == 5

    def test_search_with_sources_flag_only(self):
        """'search hello --sources' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["search", "hello", "--sources"])
        assert args.query == "hello"
        assert args.sources is True

    def test_search_with_notes_flag_only(self):
        """'search hello --notes' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["search", "hello", "--notes"])
        assert args.query == "hello"
        assert args.notes is True


class TestCredentialCommand:
    """Test credential subcommand parsing."""

    def test_credential_list_action(self):
        """'credential list' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["credential", "list"])
        assert args.action == "list"

    def test_credential_create_action(self):
        """'credential create' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["credential", "create", "--name", "my-key", "--provider", "openai"])
        assert args.action == "create"
        assert args.name == "my-key"
        assert args.provider == "openai"

    def test_credential_create_with_api_key(self):
        """'credential create' with --api-key should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["credential", "create", "--name", "my-key", "--provider", "openai", "--api-key", "sk-123"])
        assert args.action == "create"
        assert args.api_key == "sk-123"

    def test_credential_test_action(self):
        """'credential test' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["credential", "test", "cred-456"])
        assert args.action == "test"
        assert args.id == "cred-456"

    def test_credential_delete_action(self):
        """'credential delete' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["credential", "delete", "cred-456"])
        assert args.action == "delete"
        assert args.id == "cred-456"


class TestModelCommand:
    """Test model subcommand parsing."""

    def test_model_list_action(self):
        """'model list' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["model", "list"])
        assert args.action == "list"

    def test_model_list_with_provider(self):
        """'model list --provider openai' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["model", "list", "--provider", "openai"])
        assert args.action == "list"
        assert args.provider == "openai"

    def test_model_discover_action(self):
        """'model discover --provider openai' should parse correctly."""
        parser = create_parser()
        args = parser.parse_args(["model", "discover", "--provider", "openai"])
        assert args.action == "discover"
        assert args.provider == "openai"


class TestGlobalFlags:
    """Test global flags."""

    def test_server_flag(self):
        """--server flag should be parsed."""
        parser = create_parser()
        args = parser.parse_args(["--server", "http://custom:8080", "notebook", "list"])
        assert args.server == "http://custom:8080"

    def test_password_flag(self):
        """--password flag should be parsed."""
        parser = create_parser()
        args = parser.parse_args(["--password", "secret", "notebook", "list"])
        assert args.password == "secret"

    def test_version_flag(self):
        """--version flag should cause exit."""
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            args = parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_help_flag(self):
        """--help flag should cause exit."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            args = parser.parse_args(["--help"])


class TestOpenNotebookClient:
    """Test OpenNotebookClient class."""

    def test_client_default_server(self):
        """Client should use default server URL."""
        client = OpenNotebookClient()
        assert client.server == "http://localhost:5055"

    def test_client_default_password(self):
        """Client should use default password."""
        client = OpenNotebookClient()
        assert client.password == "open-notebook-change-me"

    def test_client_custom_server(self):
        """Client should use custom server URL."""
        client = OpenNotebookClient(server="http://custom:8080")
        assert client.server == "http://custom:8080"

    def test_client_custom_password(self):
        """Client should use custom password."""
        client = OpenNotebookClient(password="secret")
        assert client.password == "secret"

    def test_client_server_without_http_prefix(self):
        """Client should add http:// prefix if missing."""
        client = OpenNotebookClient(server="localhost:8080")
        assert client.server == "http://localhost:8080"

    def test_client_context_manager(self):
        """Client should work as context manager."""
        with OpenNotebookClient() as client:
            assert client is not None


class TestHandlerBehavior:
    """Test handler behavior when called."""

    def test_notebook_handler_with_no_action_calls_help(self):
        """Notebook handler should print help when action is None."""
        from opennotebook import notebook

        mock_client = MagicMock()
        args = MagicMock()
        args.action = None
        args.id_or_name = None
        args.description = None
        args.archived = None

        with patch("sys.stdout", new=StringIO()) as f:
            notebook._handle(args, mock_client)

        output = f.getvalue()
        assert "notebook" in output.lower()
        mock_client.get.assert_not_called()
        mock_client.post.assert_not_called()

    def test_source_handler_with_no_action_calls_help(self):
        """Source handler should print help when action is None."""
        from opennotebook import source

        mock_client = MagicMock()
        args = MagicMock()
        args.action = None
        args.notebook_id = None
        args.path = None

        with patch("sys.stdout", new=StringIO()) as f:
            source._handle(args, mock_client)

        output = f.getvalue()
        assert "source" in output.lower()
        mock_client.get.assert_not_called()

    def test_chat_handler_with_missing_args_calls_help(self):
        """Chat handler should print help when notebook_id or message is None."""
        from opennotebook import chat

        mock_client = MagicMock()
        args = MagicMock()
        args.notebook_id = None
        args.message = None
        args.model = None

        with patch("sys.stdout", new=StringIO()) as f:
            chat._handle(args, mock_client)

        output = f.getvalue()
        assert "chat" in output.lower()
        mock_client.post.assert_not_called()

    def test_search_handler_with_no_query_calls_help(self):
        """Search handler should print help when query is None."""
        from opennotebook import search

        mock_client = MagicMock()
        args = MagicMock()
        args.query = None
        args.type = "text"
        args.limit = 10
        args.sources = True
        args.notes = True

        with patch("sys.stdout", new=StringIO()) as f:
            search._handle(args, mock_client)

        output = f.getvalue()
        assert "search" in output.lower()
        mock_client.post.assert_not_called()

    def test_podcast_handler_with_no_action_calls_help(self):
        """Podcast handler should print help when action is None."""
        from opennotebook import podcast

        mock_client = MagicMock()
        args = MagicMock()
        args.action = None
        args.notebook_id = None
        args.episode_id = None
        args.title = None

        with patch("sys.stdout", new=StringIO()) as f:
            podcast._handle(args, mock_client)

        output = f.getvalue()
        assert "podcast" in output.lower()
        mock_client.get.assert_not_called()
        mock_client.post.assert_not_called()

    def test_credential_handler_with_no_action_calls_help(self):
        """Credential handler should print help when action is None."""
        from opennotebook import credential

        mock_client = MagicMock()
        args = MagicMock()
        args.action = None
        args.id = None
        args.name = None
        args.provider = None
        args.api_key = None

        with patch("sys.stdout", new=StringIO()) as f:
            credential._handle(args, mock_client)

        output = f.getvalue()
        assert "credential" in output.lower()
        mock_client.get.assert_not_called()
        mock_client.post.assert_not_called()

    def test_model_handler_with_no_action_calls_help(self):
        """Model handler should print help when action is None."""
        from opennotebook import model

        mock_client = MagicMock()
        args = MagicMock()
        args.action = None
        args.provider = None

        with patch("sys.stdout", new=StringIO()) as f:
            model._handle(args, mock_client)

        output = f.getvalue()
        assert "model" in output.lower()
        mock_client.get.assert_not_called()
        mock_client.post.assert_not_called()

    def test_note_handler_with_no_action_calls_help(self):
        """Note handler should print help when action is None."""
        from opennotebook import note

        mock_client = MagicMock()
        args = MagicMock()
        args.action = None
        args.source_id = None
        args.id_or_title = None
        args.content = None

        with patch("sys.stdout", new=StringIO()) as f:
            note._handle(args, mock_client)

        output = f.getvalue()
        assert "note" in output.lower()
        mock_client.get.assert_not_called()
        mock_client.post.assert_not_called()
