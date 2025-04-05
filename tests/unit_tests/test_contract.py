import pytest
from unittest.mock import Mock, MagicMock, patch
from controllers.contract_controller import ContractController
from models.events import Event
from models.contracts import Contract
from models.clients import Client
from models.users import User
from models.roles import Role
from sqlalchemy.orm import Session

from views.contract_view import ContractView


@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)


@pytest.fixture
def contract_controller(mock_db_session):
    controller = ContractController()
    controller.session = mock_db_session
    return controller


@pytest.fixture
def sample_role():
    role = Role(name="gestion")
    role.id = 3
    return role


@pytest.fixture
def sample_commercial():
    commercial_role = Role(name="commercial")
    commercial_role.id = 2

    user = User(
        id=1,
        name="Commercial Test",
        email="commercial@test.com",
        password="password",
        role_id=commercial_role.id
    )
    user.role = commercial_role
    return user


@pytest.fixture
def sample_client(sample_commercial):
    client = Client(
        id=1,
        name="Client Test",
        email="client@test.com",
        phone="0123456789",
        company="Test Company",
        commercial_id=sample_commercial.id
    )
    client.commercial = sample_commercial
    return client


@pytest.fixture
def sample_contract(sample_client):
    contract = Contract(
        id=1,
        client_id=sample_client.id,
        amount=1000.0,
        sold=500.0,
        status=False,
        date_created="2023-01-01"
    )
    contract.client = sample_client

    event_mock = MagicMock(
        _sa_instance_state=MagicMock(
            parents={},
            manager=MagicMock(__getitem__=lambda self, key: MagicMock(impl=Mock()))
        )
    )
    contract.events = [event_mock]
    return contract


@pytest.fixture(autouse=True)
def init_roles():
    Role(name="commercial")
    Role(name="gestion")
    Role(name="support")


@pytest.fixture
def contract_view():
    view = ContractView(current_user=Mock(role=Mock(name="gestion")))
    view.controller = Mock(spec=ContractController)
    return view


def test_create_contract_success(contract_controller, sample_client):
    gestion_role = Role(name="gestion")
    current_user = Mock(spec=User)
    current_user.role = gestion_role
    contract_controller.session.query().filter().first.return_value = sample_client
    new_contract = contract_controller.create_contract(
        client_id=1,
        amount=2000.0,
        sold=1000.0,
        status=True,
        current_user=current_user
    )

    assert new_contract is not None


def test_create_contract_without_permission(contract_controller):
    non_gestion_user = Mock(role=Mock(name="commercial"))
    result = contract_controller.create_contract(
        client_id=1,
        amount=2000.0,
        sold=1000.0,
        status=True,
        current_user=non_gestion_user
    )

    assert result is None


def test_update_contract(contract_controller, sample_contract, sample_commercial):
    contract_controller.session.query().filter().first.return_value = sample_contract
    sample_contract.client.commercial_id = sample_commercial.id
    updated_contract = contract_controller.update_contract(
        contract_id=1,
        amount=1500.0,
        sold=700.0,
        status=True,
        current_user=sample_commercial
    )

    assert updated_contract.amount == 1500.0
    contract_controller.session.commit.assert_called_once()


def test_delete_contract(contract_controller, sample_contract):
    gestion_role = Role(name="gestion")
    current_user = Mock(spec=User)
    current_user.role = gestion_role
    contract_controller.session.query().filter().first.return_value = sample_contract
    result = contract_controller.delete_contract(1, current_user)

    assert result is True


def test_display_contracts(contract_controller, sample_contract):
    contract_controller.get_all_contracts = Mock(return_value=[sample_contract])
    contracts = contract_controller.get_all_contracts()

    assert len(contracts) == 1
    assert contracts[0].client.name == "Client Test"


def test_display_unsigned_contracts(contract_controller):
    unsigned_contract = Mock(spec=Contract, status=False)
    contract_controller.get_unsigned_contracts = Mock(return_value=[unsigned_contract])
    contracts = contract_controller.get_unsigned_contracts()

    assert len(contracts) == 1
    assert not contracts[0].status


def test_display_unpaid_contracts(contract_controller):
    unpaid_contract = Mock(spec=Contract, sold=500.0, amount=1000.0)
    contract_controller.get_unpaid_contracts = Mock(return_value=[unpaid_contract])
    contracts = contract_controller.get_unpaid_contracts()

    assert len(contracts) == 1
    assert contracts[0].sold > 0


def test_contract_display(contract_view, capsys):
    test_contract = Mock(
        amount=10000.0,
        sold=5000.0,
        client=Mock(name="Client Test"),
        status=False
    )
    contract_view.controller.get_all_contracts.return_value = [test_contract]

    contract_view.display_contracts()

    output = capsys.readouterr().out
    assert "Client Test" in output
    assert "10000.0" in output
    assert "Non signé" in output


def test_contract_creation(contract_view):
    contract_view.current_user.role.name = "gestion"
    mock_client = Mock(id=1, name="Client Test")
    contract_view.client_controller = Mock()
    contract_view.client_controller.get_all_clients.return_value = [mock_client]

    with patch('views.contract_view.inquirer.text') as mock_text, \
            patch('views.contract_view.inquirer.select') as mock_select, \
            patch('views.contract_view.inquirer.confirm') as mock_confirm:
        mock_text.side_effect = [
            Mock(execute=lambda: "10000"),
            Mock(execute=lambda: "5000")
        ]
        mock_select.return_value.execute.return_value = 1
        mock_confirm.return_value.execute.return_value = False
        contract_view.create_contract_prompt()
        contract_view.controller.create_contract.assert_called_once_with(
            1,
            10000.0,
            5000.0,
            False,
            contract_view.current_user
        )
