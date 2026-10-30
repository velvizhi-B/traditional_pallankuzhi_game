const API = "http://127.0.0.1:8000";

export async function createRematch(gameId) {
  const response = await fetch(`${API}/games/${gameId}/rematch`, {
    method: "POST",
  });

  if (!response.ok) {
    let detail = "Could not create rematch";
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {
      // Keep the fallback message when the server does not return JSON.
    }
    throw new Error(detail);
  }

  return await response.json();
}

export async function createGame(player1Id, player2Id) {
  const response = await fetch(`${API}/games/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      player1_id: player1Id,
      player2_id: player2Id
    })
  });

  if (!response.ok) {
    let detail = "Could not create game";
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {
      // Keep the fallback message when the server does not return JSON.
    }
    throw new Error(detail);
  }

  return await response.json();
}

export async function makeMove(gameId, payload) {

  const response = await fetch(`${API}/moves/${gameId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    let detail = "Move failed";
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {
      // Keep the fallback message when the server does not return JSON.
    }
    throw new Error(detail);
  }

  return await response.json();
}