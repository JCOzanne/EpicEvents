import pytest
from unittest.mock import Mock, patch
import sys
from main import main, initialize_roles, create_admin_user
from models.roles import Role
from models.users import User
from sqlalchemy.orm import Session

@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)

def test_initialize_roles(mock_db_session):
    with patch('main.SessionLocal', return_value=mock_db_session):
        mock_db_session.query().count.return_value = 0

        initialize_roles()

        assert mock_db_session.add_all.call_count == 1
        mock_db_session.commit.assert_called_once()

def test_create_admin_user(mock_db_session):
    mock_role = Mock()
    mock_role.id = 1

    with patch('main.SessionLocal', return_value=mock_db_session), \
            patch('bcrypt.hashpw', return_value=b'hashed_password'), \
            patch('bcrypt.gensalt', return_value=b'salt'):
        mock_db_session.query().filter().first.return_value = mock_role
        mock_db_session.query().filter().count.return_value = 0
        create_admin_user()

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

def test_main_with_login_arg(mock_db_session):
    testargs = ["main.py", "login"]
    with patch.object(sys, 'argv', testargs), \
            patch('main.UserView') as mock_user_view, \
            patch('main.MenuView'), \
            patch.object(mock_user_view.return_value, 'login_prompt', return_value=True):
        main()

        mock_user_view.return_value.login_prompt.assert_called_once()

def test_main_without_login_arg_authenticated(mock_db_session):
    with patch('main.UserView') as mock_user_view, \
            patch('main.MenuView'), \
            patch.object(mock_user_view.return_value, 'check_authentication', return_value=True):
        main()

        mock_user_view.return_value.check_authentication.assert_called_once()

def test_main_without_login_arg_not_authenticated(mock_db_session, capsys):
    with patch('main.UserView') as mock_user_view, \
            patch.object(mock_user_view.return_value, 'check_authentication', return_value=False):
        main()
        output = capsys.readouterr().out

        assert "Veuillez vous connecter" in output
