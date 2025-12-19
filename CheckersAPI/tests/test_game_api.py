from unittest.mock import AsyncMock, MagicMock
from web.dependencies import get_game_repository, get_matching_repository, get_create_player_handler
from infrastructure.repositories.matching_repository import MatchingRepository
from application.handlers.create_player_handler import CreatePlayerHandler

def test_get_game(client):
    mock_repository = AsyncMock()
    mock_repository.fetch.return_value = {"game_id": "123", "status": "active"}

    app = client.app
    app.dependency_overrides[get_game_repository] = lambda: mock_repository

    response = client.get("/api/games/123")

    assert response.status_code == 200
    assert response.json() == {"game_id": "123", "status": "active"}

    app.dependency_overrides = {}

def test_request_game_guest(client):
    mock_matching_repo = MagicMock(spec=MatchingRepository)
    mock_matching_repo.add_to_queue.return_value = "queue_id"
    
    mock_player_handler = MagicMock(spec=CreatePlayerHandler)
    mock_player_handler.handle.return_value = "guest_player_123"
    
    app = client.app
    app.dependency_overrides[get_matching_repository] = lambda: mock_matching_repo
    app.dependency_overrides[get_create_player_handler] = lambda: mock_player_handler
    
    response = client.post("/api/games/request_game")
    
    assert response.status_code == 200
    assert response.json() == {"player_id": "guest_player_123", "status": "waiting"}
    
    mock_player_handler.handle.assert_called_once()
    mock_matching_repo.add_to_queue.assert_called_once_with(player_id="guest_player_123", region="EU", rating=1000)
    
    app.dependency_overrides = {}

def test_request_game_auth(client):
    # Mock decode_access_token to return a payload with player_id
    # We need to mock web.routers.game_api.decode_access_token
    # Since we can't easily mock the import inside the function without patching,
    # we will use unittest.mock.patch
    
    from unittest.mock import patch
    from web.models import AccessTokenData
    from datetime import datetime, timezone, timedelta
    
    mock_matching_repo = MagicMock(spec=MatchingRepository)
    mock_matching_repo.add_to_queue.return_value = "queue_id"
    
    mock_player_handler = MagicMock(spec=CreatePlayerHandler)
    
    app = client.app
    app.dependency_overrides[get_matching_repository] = lambda: mock_matching_repo
    app.dependency_overrides[get_create_player_handler] = lambda: mock_player_handler
    
    with patch("web.routers.game_api.decode_access_token") as mock_decode:
        mock_decode.return_value = AccessTokenData(
            sub="auth_player_456",
            name="Test User",
            preferred_username="test@example.com",
            type="user",
            exp=datetime.now(timezone.utc) + timedelta(hours=1),
            iss="test_issuer",
            aud="test_audience"
        )
        
        response = client.post(
            "/api/games/request_game",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"player_id": "auth_player_456", "status": "waiting"}
        
        mock_player_handler.handle.assert_not_called()
        mock_matching_repo.add_to_queue.assert_called_once_with(player_id="auth_player_456", region="EU", rating=1000)
    
    app.dependency_overrides = {}
