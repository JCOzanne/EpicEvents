import pytest
from unittest.mock import patch, Mock
from views.menu_view import MenuView  # adapte le chemin

@pytest.fixture
def fake_user_view():
    return Mock()  # ou un vrai objet mocké si nécessaire

@patch("InquirerPy.inquirer.select")
def test_display_main_menu_no_user_quit(mock_select, fake_user_view):
    # Simule le choix "0" pour quitter le menu
    mock_select.return_value.execute.return_value = "0"

    menu = MenuView(user_view=fake_user_view)
    menu.current_user = None

    menu.display_main_menu()  # ne plante pas = test OK

@patch("InquirerPy.inquirer.secret")
@patch("InquirerPy.inquirer.text")
def test_login_prompt_success(mock_text, mock_secret, fake_user_view):
    # Simule l'entrée utilisateur
    mock_text.return_value.execute.return_value = "test@example.com"
    mock_secret.return_value.execute.return_value = "password123"

    fake_user = Mock()
    fake_user.name = "Jean"
    fake_user_view.controller.authenticate.return_value = fake_user
    fake_user_view.controller.generate_token.return_value = "fake_token"

    menu = MenuView(user_view=fake_user_view)
    menu.login_prompt()

    # Vérifie que l'utilisateur est bien connecté
    assert menu.current_user == fake_user

@patch("InquirerPy.inquirer.select")
def test_display_user_menu_return(mock_select, fake_user_view):
    mock_select.return_value.execute.return_value = "0"

    menu = MenuView(user_view=fake_user_view)
    menu.current_user = Mock()  # Simule qu'un utilisateur est connecté

    menu.display_user_menu()  # ne plante pas = test OK
