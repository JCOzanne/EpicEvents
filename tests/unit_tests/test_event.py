import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, timedelta
from controllers.event_controller import EventController
from models.events import Event
from models.contracts import Contract
from models.clients import Client
from models.users import User
from models.roles import Role
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)

@pytest.fixture
def event_controller(mock_db_session):
    controller = EventController()
    controller.session = mock_db_session
    return controller

@pytest.fixture
def sample_roles():
    return [
        Role(name="commercial"),
        Role(name="support"),
        Role(name="gestion")
    ]

@pytest.fixture
def sample_commercial(sample_roles):
    user = User(
        id=1,
        name="Commercial Test",
        role=sample_roles[0]
    )
    return user

@pytest.fixture
def sample_support(sample_roles):
    user = User(
        id=2,
        name="Support Test",
        role=sample_roles[1]
    )
    return user

@pytest.fixture
def sample_gestion(sample_roles):
    user = User(
        id=3,
        name="Gestion Test",
        role=sample_roles[2]
    )
    return user

@pytest.fixture
def sample_client(sample_commercial):
    client = Client(
        id=1,
        name="Client Test",
        email="client@test.com",
        phone="0123456789",
        company="Test Company",
        commercial_id=sample_commercial.id,
        commercial=sample_commercial
    )
    return client

@pytest.fixture
def sample_contract(sample_client):
    contract = Contract(
        id=1,
        client=sample_client,
        status=True
    )
    return contract

@pytest.fixture
def sample_event(sample_contract, sample_support):
    return Event(
        id=1,
        name="Test Event",
        contract=sample_contract,
        support_id=sample_support.id,
        support=sample_support,
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=6)
    )

def test_create_event_success(event_controller, sample_commercial, sample_contract, sample_client):
    sample_contract.client = sample_client
    event_controller.session.query().filter().first.return_value = sample_contract
    result = event_controller.create_event(
        name="New Event",
        location="Paris",
        attendees=100,
        notes="Test notes",
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=6),
        contract_id=1,
        current_user=sample_commercial
    )

    assert result is not None

def test_create_event_without_permission(event_controller, sample_support):
    result = event_controller.create_event(
        name="New Event",
        location="Paris",
        attendees=100,
        notes="Test notes",
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=6),
        contract_id=1,
        current_user=sample_support
    )

    assert result is None

def test_create_event_unsigned_contract(event_controller, sample_commercial):
    unsigned_contract = Mock(spec=Contract, status=False)
    event_controller.session.query().filter().first.return_value = unsigned_contract
    result = event_controller.create_event(
        name="New Event",
        location="Paris",
        attendees=100,
        notes="Test notes",
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=6),
        contract_id=1,
        current_user=sample_commercial
    )

    assert result is None

def test_update_event_by_support(event_controller, sample_event, sample_support):
    event_controller.session.query().filter().first.return_value = sample_event
    result = event_controller.update_events(
        event_id=1,
        name="Updated Name",
        current_user=sample_support
    )

    assert result.name == "Updated Name"

def test_update_event_by_gestion(event_controller, sample_event, sample_gestion):
    event_controller.session.query().filter().first.return_value = sample_event
    result = event_controller.update_events(
        event_id=1,
        location="New Location",
        current_user=sample_gestion
    )

    assert result.location == "New Location"

def test_update_event_without_permission(event_controller, sample_event, sample_commercial):
    event_controller.session.query().filter().first.return_value = sample_event
    result = event_controller.update_events(
        event_id=1,
        name="Updated Name",
        current_user=sample_commercial
    )

    assert result is None

def test_delete_event_by_gestion(event_controller, sample_event, sample_gestion):
    event_controller.session.query().filter().first.return_value = sample_event
    result = event_controller.delete_event(1, sample_gestion)

    assert result is True
    event_controller.session.delete.assert_called_once_with(sample_event)

def test_delete_event_without_permission(event_controller, sample_event, sample_support):
    result = event_controller.delete_event(1, sample_support)

    assert result is False

def test_display_events(event_controller, sample_event):
    event_controller.get_all_events = Mock(return_value=[sample_event])
    events = event_controller.get_all_events()

    assert len(events) == 1
    assert events[0].name == "Test Event"

def test_display_events_by_support(event_controller, sample_event, sample_support):
    event_controller.get_events_by_support = Mock(return_value=[sample_event])
    events = event_controller.get_events_by_support(sample_support.id)

    assert len(events) == 1
    assert events[0].support.id == sample_support.id
