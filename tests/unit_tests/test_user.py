import pytest
from unittest.mock import Mock, patch, ANY
from sqlalchemy.orm import Session

from controllers.user_controller import UserController
from models.users import User
from models.roles import Role
from models.clients import Client
from models.contracts import Contract
from models.events import Event
from views.user_view import UserView
from auth import generate_token, delete_token, verify_token

@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)

@pytest.fixture
def user_controller(mock_db_session):
    controller = UserController()
    controller.session = mock_db_session
    return controller

@pytest.fixture
def sample_role():
    role = Role(name="gestion")
    role.id = 1
    return role

@pytest.fixture
def sample_user(sample_role):
    user = User(
        id=1,
        name="Admin",
        email="admin@test.com",
        password="hashed_password",
        role_id=sample_role.id
    )
    user.role = sample_role
    return user

@pytest.fixture
def user_view(user_controller):
    view = UserView()
    view.controller = user_controller
    view.current_user = Mock(id=1, role=Mock(name="gestion"))
    return view

def test_successful_login(user_controller, sample_user, mock_db_session):
    mock_db_session.query().filter().first.return_value = sample_user
    user_controller.verify_password = Mock(return_value=True)
    result = user_controller.authenticate("admin@test.com", "password")

    assert result == sample_user

def test_failed_login_wrong_password(user_controller, sample_user, mock_db_session):
    mock_db_session.query().filter().first.return_value = sample_user
    user_controller.verify_password = Mock(return_value=False)
    result = user_controller.authenticate("admin@test.com", "wrongpass")

    assert result is None

def test_user_creation(user_controller, sample_role, mock_db_session):
    user_controller.check_permission = Mock(return_value=True)
    new_user = user_controller.create_user(
        "New User", "new@test.com", "password", sample_role.id, 1
    )

    assert new_user.name == "New User"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_user_update(user_controller, sample_user, mock_db_session):
    mock_db_session.query().filter().first.return_value = sample_user
    user_controller.check_permission = Mock(return_value=True)
    updated_user = user_controller.update_user(
        user_id=1,
        current_user_id=1,
        name="Updated Name"
    )

    assert updated_user.name == "Updated Name"
    mock_db_session.commit.assert_called_once()

def test_user_deletion(user_controller, sample_user, mock_db_session):
    mock_db_session.query().filter().first.return_value = sample_user
    user_controller.check_permission = Mock(return_value=True)
    result = user_controller.delete_user(1, 1)

    assert result is True
    mock_db_session.delete.assert_called_once_with(sample_user)
    mock_db_session.commit.assert_called_once()

def test_token_operations():
    test_user = Mock()
    test_user.id = 1
    test_user.role.name = "gestion"

    token = generate_token(test_user)

    with patch('jwt.decode') as mock_decode:
        mock_decode.return_value = {'user_id': 1, 'role': 'gestion'}
        payload = verify_token(token)

        assert payload['user_id'] == 1
        assert payload['role'] == 'gestion'

def test_logout():
    with open(".jwt_token", "w") as f:
        f.write("test_token")

    delete_token()

    with pytest.raises(FileNotFoundError):
        open(".jwt_token", "r")


def test_view_login_flow(user_view, user_controller, monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "cle_secrete_jwt")
    mock_role = Mock(spec=Role)
    mock_role.name = "gestion"

    mock_user = Mock(
        id=1,
        name="Admin",
        role=mock_role
    )

    with patch('views.user_view.inquirer.text') as mock_text, \
            patch('views.user_view.inquirer.secret') as mock_secret, \
            patch.object(user_controller, 'authenticate', return_value=mock_user), \
            patch('auth.jwt.encode') as mock_jwt_encode:
        mock_text.return_value.execute.return_value = "admin@test.com"
        mock_secret.return_value.execute.return_value = "password"
        mock_jwt_encode.return_value = "fake_token"
        result = user_view.login_prompt()

        assert result is True
        mock_jwt_encode.assert_called_once_with(
            {
                'user_id': 1,
                'role': 'gestion',
                'exp': ANY
            },
            "cle_secrete_jwt",
            algorithm='HS256'
        )

def test_view_create_user_validation(user_view):
    # Test validation email
    assert user_view.validate_email("invalid") == "Veuillez entrer un email valide"
    assert user_view.validate_email("valid@test.com") is True
