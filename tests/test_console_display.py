from hal.display.console_display import CLEAR_SEQUENCE, ConsoleDisplay

# --- helper function ---

TITLE = "Test Menu"
OPTIONS = ["Option 1", "Option 2", "Option 3"]

def marked_lines(output):
    """Lines of the output that carry the selection marker."""
    return [line for line in output.splitlines() if line.startswith("> ")]


# --- name ------------------------------------------------------------------

def test_name_is_console():
    assert ConsoleDisplay().name == "Console"


# --- show_menu -------------------------------------------------------------

def test_show_menu_prints_title_and_all_options(capsys):
    display = ConsoleDisplay()

    display.show_menu(TITLE, OPTIONS, 0)
    output = capsys.readouterr().out

    assert TITLE in output
    for option in OPTIONS:
        assert option in output


def test_show_menu_marks_only_the_selected_option(capsys):
    display = ConsoleDisplay()

    display.show_menu(TITLE, OPTIONS, 1)
    output = capsys.readouterr().out

    marked = marked_lines(output)
    assert len(marked) == 1
    assert "Option 2" in marked[0]


def test_show_menu_moves_marker_when_index_changes(capsys):
    display = ConsoleDisplay()
    display.show_menu(TITLE, OPTIONS, 0)
    capsys.readouterr()  # discard the first draw

    display.show_menu(TITLE, OPTIONS, 2)
    marked = marked_lines(capsys.readouterr().out)

    assert len(marked) == 1
    assert "Option 3" in marked[0]


def test_show_menu_clears_the_screen_first(capsys):
    display = ConsoleDisplay()

    display.show_menu(TITLE, OPTIONS, 0)
    output = capsys.readouterr().out

    assert output.startswith(CLEAR_SEQUENCE)


def test_show_menu_clears_before_every_draw(capsys):
    display = ConsoleDisplay()

    display.show_menu(TITLE, OPTIONS, 0)
    display.show_menu(TITLE, OPTIONS, 1)
    output = capsys.readouterr().out

    assert output.count(CLEAR_SEQUENCE) == 2


def test_show_menu_without_options_prints_only_the_title(capsys):
    display = ConsoleDisplay()

    display.show_menu(TITLE, [], 0)
    output = capsys.readouterr().out

    assert TITLE in output
    assert marked_lines(output) == []


# --- clear_screen ----------------------------------------------------------

def test_clear_screen_prints_the_clear_sequence(capsys):
    display = ConsoleDisplay()

    display.clear_screen()

    assert capsys.readouterr().out == CLEAR_SEQUENCE


# --- start / stop ----------------------------------------------------------

def test_stop_can_be_called_twice():
    display = ConsoleDisplay()
    display.start()

    display.stop()
    display.stop()
