import { useEffect, useState } from "react";
import Board from "../components/Board/Board";
import PlayerInfo from "../components/PlayerInfo/PlayerInfo";
import { createGame, createRematch } from "../api/gameApi";

function GamePage() {
  const [game, setGame] = useState(null);
  const [error, setError] = useState("");
  const [gameResult, setGameResult] = useState("");
  const [rematchLoading, setRematchLoading] = useState(false);
  const [scores, setScores] = useState({
    player1: 0,
    player2: 0
  });

  useEffect(() => {
    let isMounted = true;

    createGame(1, 2)
      .then((newGame) => {
        if (!isMounted) return;
        setGame(newGame);
        setScores({
          player1: newGame.scores?.["1"] ?? 0,
          player2: newGame.scores?.["2"] ?? 0
        });
      })
      .catch((gameError) => {
        if (isMounted) setError(gameError.message);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleRematch = async () => {
    try {
      setRematchLoading(true);
      const nextGame = await createRematch(game.id);
      setGame(nextGame);
      setGameResult("");
      setScores({
        player1: nextGame.scores?.["1"] ?? 0,
        player2: nextGame.scores?.["2"] ?? 0
      });
    } catch (rematchError) {
      setError(rematchError.message);
    } finally {
      setRematchLoading(false);
    }
  };

  return (
    <div>
      <h1>Pallankuzhi</h1>

      {error && <p role="alert">{error}</p>}

      {game ? (
        <>
          <PlayerInfo player={game.current_turn} scores={scores} />

          {gameResult && <p className="gameResult" role="status">{gameResult}</p>}

          {gameResult && game.scores?.["1"] >= 5 && game.scores?.["2"] >= 5 && (
            <button className="rematchButton" type="button" onClick={handleRematch} disabled={rematchLoading}>
              {rematchLoading ? "Starting next level..." : "Rematch / Next level"}
            </button>
          )}

          <Board
            key={game.id}
            gameId={game.id}
            initialBoard={game.board_state.pits}
            currentPlayer={game.current_turn}
            setCurrentPlayer={(player) => setGame((previous) => ({ ...previous, current_turn: player }))}
            setScores={setScores}
            playerIds={{ 1: game.player1_id, 2: game.player2_id }}
            onGameOver={(winner, finalScores) => {
              setGame((previous) => ({ ...previous, scores: finalScores }));
              setGameResult(
                finalScores["1"] < 5 || finalScores["2"] < 5
                  ? winner === null ? "Game finished. It is a draw! Series complete." : `Congratulations! Player ${winner} won! Series complete.`
                  : winner === null ? "Game finished. It is a draw!" : `Congratulations! Player ${winner} won!`
              );
            }}
          />
        </>
      ) : (
        !error && <p>Creating match...</p>
      )}
    </div>
  );
}

export default GamePage;