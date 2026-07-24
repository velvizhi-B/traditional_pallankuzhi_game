import styles from "./Pit.module.scss";
import Seed from "../Seed/Seed";

function Pit({ index, seeds, onClick, disabled }) {
  const seedCount = Math.max(0, Number(seeds) || 0);

  return (
    <div
      className={styles.pit}
      data-testid="pit"
      data-pit-index={index}
      aria-label={`Pit ${index + 1}, ${seedCount} seeds`}
      onClick={!disabled ? onClick : undefined}
    >
      <div className={styles.seedLayout} aria-hidden="true">
        {Array.from({ length: seedCount }, (_, seedIndex) => (
          <Seed key={`${index}-${seedIndex}`} />
        ))}
      </div>
      <span className={styles.seedCount}>{seedCount}</span>
    </div>
  );
}

export default Pit;