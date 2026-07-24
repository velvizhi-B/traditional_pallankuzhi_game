function PlayerInfo({ player, scores }) {

  return (
    <div>
      <h2>Player {player} Turn</h2>

      <p>Player 1 Score: {scores.player1}</p>
      <p>Player 2 Score: {scores.player2}</p>
    </div>
  );
}

export default PlayerInfo;