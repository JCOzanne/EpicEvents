import pytest
from unittest.mock import Mock, patch, MagicMock
from controllers.client_controller import ClientController
from models.contracts import Contract
from models.events import Event
from models.clients import Client
from models.users import User
from models.roles import Role
from sqlalchemy.orm import Session

from views.client_view import ClientView


@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)

@pytest.fixture
def client_controller(mock_db_session):
    controller = ClientController()
    controller.session = mock_db_session
    return controller

@pytest.fixture
def sample_role():
    role = Role(name="commercial")
    role.id = 2
    return role

@pytest.fixture
def sample_commercial(sample_role):
    user = User(
        id=1,
        name="Commercial Test",
        email="commercial@test.com",
        password="password",
        role_id=sample_role.id
    )
    user.role = sample_role
    return user

@pytest.fixture
def sample_client(sample_commercial):
    client = Client(
        id=1,
        name="Client Test",
        email="client@test.com",
        phone="0123456789",
        company="Test Company",
        date_created="2023-01-01",
        date_updated="2023-01-01",
        commercial_id=sample_commercial.id
    )
    client.commercial = sample_commercial

    contract_mock = Mock(
        spec=Contract,
        client_id=1,
        events=[],
        _sa_instance_state=MagicMock(
            parents={},
            manager=MagicMock(
                __getitem__=lambda self, key: MagicMock(impl=Mock())
        )
    )
    )
    client.contracts = [contract_mock]
    return client


@pytest.fixture
def client_view():
    mock_role = Mock()
    mock_role.name = "commercial"

    user = Mock()
    user.id = 1
    user.role = mock_role

    view = ClientView(current_user=user)
    view.controller = Mock(spec=ClientController)
    return view

def test_create_client_success(client_controller, sample_commercial):
    new_client = client_controller.create_client(
        "Nouveau Client",
        "nouveau@client.com",
        "0612345678",
        "Entreprise",
        sample_commercial
    )

    assert new_client is not None
    client_controller.session.add.assert_called_once()
    client_controller.session.commit.assert_called_once()

def test_create_client_without_permission(client_controller):
    non_commercial_user = Mock()
    non_commercial_user.role.name = "support"
    result = client_controller.create_client(
        "Client", "client@test.com", "0612345678", "Entreprise", non_commercial_user
    )

    assert result is None

def test_update_client(client_controller, sample_commercial, sample_client):
    client_controller.session.query().filter().first.return_value = sample_client
    updated_client = client_controller.update_client(
        1, "Nouveau Nom", None, None, None, sample_commercial
    )

    assert updated_client.name == "Nouveau Nom"
    client_controller.session.commit.assert_called_once()

def test_delete_client(client_controller, sample_commercial, sample_client):
    client_controller.session.query().filter().first.return_value = sample_client
    result = client_controller.delete_client(1, sample_commercial)

    assert result is True
    client_controller.session.delete.assert_called_once_with(sample_client)
    client_controller.session.commit.assert_called_once()


def test_display_clients_by_commercial(client_controller, sample_commercial):
    mock_client = Mock()
    mock_client.id = 1
    mock_client.name = "Client Test"
    client_controller.get_client_by_commercial = Mock(return_value=[mock_client])
    clients = client_controller.get_client_by_commercial(sample_commercial.id)

    assert len(clients) == 1
    assert clients[0].name == "Client Test"


def test_view_client_creation(client_view, capsys):
    client_view.current_user.role.name = "commercial"
    mock_client = Mock()
    mock_client.name = "Client Test"
    client_view.controller.create_client.return_value = mock_client

    with patch('views.client_view.inquirer.text') as mock_text:
        mock_text.side_effect = [
            Mock(execute=lambda: "Client Test"),
            Mock(execute=lambda: "client@test.com"),
            Mock(execute=lambda: "0123456789"),
            Mock(execute=lambda: "Entreprise Test")
        ]

        client_view.create_client_prompt()
        client_view.controller.create_client.assert_called_once_with(
            "Client Test",
            "client@test.com",
            "0123456789",
            "Entreprise Test",
            client_view.current_user
        )
        output = capsys.readouterr().out

        assert "Le client Client Test a été créé avec succès." in output
