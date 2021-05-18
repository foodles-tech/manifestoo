from typer.testing import CliRunner

from manifestoo.__main__ import app
from manifestoo.commands.list_depends import list_depends_command

from .common import mock_addons_selection, mock_addons_set, populate_addons_dir


def test_basic():
    addons_set = mock_addons_set(
        {
            "a": {"depends": ["b"]},
            "b": {},
        }
    )
    addons_selection = mock_addons_selection("a")
    assert list_depends_command(addons_selection, addons_set, recursive=False) == (
        ["b"],
        set(),
    )


def test_recursive():
    addons_set = mock_addons_set(
        {
            "a": {"depends": ["b"]},
            "b": {"depends": ["c"]},
            "c": {},
        }
    )
    addons_selection = mock_addons_selection("a")
    assert list_depends_command(addons_selection, addons_set, recursive=False) == (
        ["b"],
        set(),
    )
    assert list_depends_command(addons_selection, addons_set, recursive=True) == (
        [
            "b",
            "c",
        ],
        set(),
    )


def test_loop():
    addons_set = mock_addons_set(
        {
            "a": {"depends": ["b"]},
            "b": {"depends": ["c"]},
            "c": {"depends": ["a"]},
        }
    )
    addons_selection = mock_addons_selection("a")
    assert list_depends_command(addons_selection, addons_set, recursive=True) == (
        [
            "a",
            "b",
            "c",
        ],
        set(),
    )


def test_missing():
    addons_set = mock_addons_set(
        {
            "a": {"depends": ["b"]},
        }
    )
    assert list_depends_command(
        mock_addons_selection("a"), addons_set, recursive=False
    ) == (
        [
            "b",
        ],
        set(),
    )
    assert list_depends_command(
        mock_addons_selection("a"), addons_set, recursive=True
    ) == (
        [
            "b",
        ],
        {"b"},
    )
    assert list_depends_command(
        mock_addons_selection("a,c"), addons_set, recursive=True
    ) == (
        [
            "b",
        ],
        {"b", "c"},
    )


def test_include_selected():
    addons_set = mock_addons_set(
        {
            "a": {"depends": ["b"]},
            "b": {},
        }
    )
    addons_selection = mock_addons_selection("a")
    assert list_depends_command(
        addons_selection, addons_set, include_selected=True
    ) == (
        [
            "a",
            "b",
        ],
        set(),
    )


def test_integration(tmp_path):
    addons = {
        "a": {"depends": ["b"]},
        "b": {},
    }
    populate_addons_dir(tmp_path, addons)
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        app,
        [f"--addons-path={tmp_path}", "--select-include", "a", "list-depends"],
        catch_exceptions=False,
    )
    assert not result.exception
    assert result.exit_code == 0, result.stderr
    assert result.stdout == "b\n"
