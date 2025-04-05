import pytest
from unittest.mock import patch, Mock
from views.menu_view import MenuView


@pytest.fixture
def fake_user_view():
    return Mock()


@patch("InquirerPy.inquirer.select")
def test_display_main_menu_no_user_quit(mock_select, fake_user_view):
    mock_select.return_value.execute.return_value = "0"
    menu = MenuView(user_view=fake_user_view)
    menu.current_user = None

    menu.display_main_menu()


@patch("InquirerPy.inquirer.secret")
@patch("InquirerPy.inquirer.text")
def test_login_prompt_success(mock_text, mock_secret, fake_user_view):
    mock_text.return_value.execute.return_value = "test@example.com"
    mock_secret.return_value.execute.return_value = "password123"

    fake_user = Mock()
    fake_user.name = "Jean"
    fake_user_view.controller.authenticate.return_value = fake_user
    fake_user_view.controller.generate_token.return_value = "fake_token"

    menu = MenuView(user_view=fake_user_view)
    menu.login_prompt()

    assert menu.current_user == fake_user


@patch("InquirerPy.inquirer.select")
def test_display_user_menu_return(mock_select, fake_user_view):
    mock_select.return_value.execute.return_value = "0"

    menu = MenuView(user_view=fake_user_view)
    menu.current_user = Mock()

    menu.display_user_menu()
