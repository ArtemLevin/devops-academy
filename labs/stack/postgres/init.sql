-- Synthetic values only; evaluated on first initialization of an empty data volume.
CREATE TABLE IF NOT EXISTS demo_events (
    event_id INTEGER PRIMARY KEY,
    label TEXT NOT NULL
);
INSERT INTO demo_events (event_id, label) VALUES
    (1, 'Student A — synthetic event'),
    (2, 'Student B — synthetic event');
