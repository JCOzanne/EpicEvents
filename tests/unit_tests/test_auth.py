import pytest
import pendulum
import os
from unittest.mock import Mock, patch, mock_open
import jwt
from auth import generate_token, verify_token, save_token, load_token, delete_token


@pytest.fixture
def sample_user():
    user = Mock()
    user.id = 1
    user.role.name = "gestion"
    return user


@pytest.fixture
def valid_token(sample_user):
    exp_time = pendulum.now().add(hours=1).int_timestamp
    return jwt.encode(
        {
            "user_id": sample_user.id,
            "role": sample_user.role.name,
            "exp": exp_time
        },
        "cle_secrete_jwt",
        algorithm="HS256"
    )


def test_generate_token_valid(sample_user):
    with patch('os.getenv', return_value='cle_secrete_jwt'), \
         patch('auth.pendulum.now') as mock_now, \
         patch('jwt.encode') as mock_encode:

        mock_now.return_value.add.return_value.int_timestamp = 1704110400
        mock_encode.return_value = "test_token"
        token = generate_token(sample_user)
        mock_encode.assert_called_with({
            'user_id': 1,
            'role': 'gestion',
            'exp': 1704110400
        }, "cle_secrete_jwt", algorithm='HS256')

        assert token == "test_token"


def test_verify_token_valid(valid_token):
    with patch('jwt.decode') as mock_decode:
        mock_decode.return_value = {'user_id': 1, 'role': 'gestion'}
        payload = verify_token(valid_token)

        assert payload['user_id'] == 1
        assert payload['role'] == "gestion"


def test_verify_token_expired():
    with patch('jwt.decode') as mock_decode, \
            patch('builtins.print') as mock_print:
        mock_decode.side_effect = jwt.ExpiredSignatureError("Token expiré")
        result = verify_token("expired_token")
        mock_print.assert_called_with("Le Token a expiré, veuillez vous reconnecter")

        assert result is None


def test_verify_token_invalid():
    with patch('jwt.decode') as mock_decode, \
            patch('builtins.print') as mock_print:
        mock_decode.side_effect = jwt.InvalidTokenError("Token invalide")
        result = verify_token("invalid_token")
        mock_print.assert_called_with("Token invalide")

        assert result is None


def test_save_and_load_token():
    m = mock_open()
    with patch("builtins.open", m) as mock_file:
        save_token("test_token")
        mock_file.assert_called_once_with('.jwt_token', 'w')
        handle = mock_file()
        handle.write.assert_called_once_with("test_token")
        m.reset_mock()
        handle.read.return_value = "test_token"
        token = load_token()
        mock_file.assert_called_once_with('.jwt_token', 'r')

        assert token == "test_token"


def test_delete_token():
    with patch("os.path.exists") as mock_exists, \
            patch("os.remove") as mock_remove, \
            patch("builtins.print") as mock_print:
        mock_exists.return_value = True
        delete_token()
        mock_remove.assert_called_once_with('.jwt_token')
        mock_print.assert_called_with("Deconnexion réussie")
        mock_exists.return_value = False
        mock_remove.reset_mock()
        delete_token()
        mock_remove.assert_not_called()
        mock_print.assert_called_with("Aucun token à supprimer")


def test_full_token_cycle(sample_user, tmp_path):
    TOKEN_FILE = tmp_path / ".jwt_token"

    with patch('auth.TOKEN_FILE', str(TOKEN_FILE)):
        token = generate_token(sample_user)
        save_token(token)

        loaded_token = load_token()
        payload = verify_token(loaded_token)

        assert payload['user_id'] == sample_user.id
        assert payload['role'] == sample_user.role.name


def teardown_module(module):
    if os.path.exists(".jwt_token"):
        os.remove(".jwt_token")
