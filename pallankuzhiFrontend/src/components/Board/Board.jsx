import { useState } from "react";
import Pit from "../Pit/Pit";
import styles from "./Board.module.scss";
import { makeMove } from "../../api/gameApi";


function Board({ gameId, initialBoard, currentPlayer, setCurrentPlayer, setScores, playerIds, onGameOver }) {
  const [pits, setPits] = useState(initialBoard);
  const [loading, setLoading] = useState(false);
  const [gameOver, setGameOver] = useState(false);
  const [moveStatus, setMoveStatus] = useState("");

  const isPlayerPit = (index) => {
    if (gameOver) return false;
    const pitsPerSide = pits.length / 2;
    if (currentPlayer === 1) return index >= 0 && index < pitsPerSide;
    if (currentPlayer === 2) return index >= pitsPerSide && index < pits.length;
    return false;
  };

  const handlePitClick = async (index) => {
    if (!isPlayerPit(index)) {
      console.log('handlePitClick: not player pit', { index, currentPlayer });
      return;
    }

    const previousPits = pits.slice();
    const seedsToSow = previousPits[index];

    try {
      setLoading(true);
      setMoveStatus("Drawing seeds...");
      setPits((currentPits) => currentPits.map((seeds, pitIndex) => (
        pitIndex === index ? seeds - seedsToSow : seeds
      )));

      for (let seedNumber = 0; seedNumber < seedsToSow; seedNumber += 1) {
        await new Promise((resolve) => setTimeout(resolve, 140));
        const destination = (index + seedNumber + 1) % previousPits.length;
        setMoveStatus(`Sowing seed ${seedNumber + 1} of ${seedsToSow}`);
        setPits((currentPits) => currentPits.map((seeds, pitIndex) => (
          pitIndex === destination ? seeds + 1 : seeds
        )));
      }

      setMoveStatus("Finishing move...");
      console.log('handlePitClick: making move', { index, currentPlayer, gameId, payload: { player_id: playerIds[currentPlayer], pit_choosen: index } });

      const data = await makeMove(gameId, {
        player_id: playerIds[currentPlayer],
        pit_choosen: index,
      });
      setPits(data.board || (data.board_state && data.board_state.pits) || Array(14).fill(5));

      setScores({
        player1: data.scores?.["1"] ?? 0,
        player2: data.scores?.["2"] ?? 0,
      });

      if (data.status === "completed" || data.status === "finished" || data.game_over) {
        setGameOver(true);
        const winner = data.winner === null
          ? null
          : data.winner === playerIds[1] ? 1 : 2;
        onGameOver(winner, data.scores ?? { "1": 0, "2": 0 });
      } else {
        setCurrentPlayer(data.current_turn);
      }
    } catch (err) {
      setPits(previousPits);
      alert(err.message);
    } finally {
      setLoading(false);
      setMoveStatus("");
    }
  };

  return (
    <div className={styles.board}>
      <div className={styles.moveStatus} aria-live="polite">{moveStatus}</div>
      <div className={styles.sideLabel}>Player 2 side</div>
      <div className={styles.row} aria-label={`Player 2 side, ${pits.length / 2} pits`}>
        {pits
          .slice(pits.length / 2)
          .reverse()
          .map((seeds, idx) => {
            const realIndex = pits.length - 1 - idx;

            return (
              <Pit
                key={realIndex}
                index={realIndex}
                seeds={seeds}
                disabled={loading}
                onClick={() => handlePitClick(realIndex)}
              />
            );
          })}
      </div>

      <div className={styles.sideLabel}>Player 1 side</div>
      <div className={styles.row} aria-label={`Player 1 side, ${pits.length / 2} pits`}>
        {pits.slice(0, pits.length / 2).map((seeds, index) => (
          <Pit
            index={index}
            key={index}
            seeds={seeds}
            disabled={loading}
            onClick={() => handlePitClick(index)}
          />
        ))}
      </div>
    </div>
  );
}

export default Board;
