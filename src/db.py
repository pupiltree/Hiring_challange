import sqlite3
import uuid
import json

class BookingDB:
    def __init__(self, db_path="reservations.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
              id TEXT PRIMARY KEY,
              user_id TEXT,
              check_in TEXT,
              check_out TEXT,
              room_type TEXT,
              guests INTEGER
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS convo_state (
              user_id    TEXT PRIMARY KEY,
              state      TEXT,
              slots_json TEXT
            )
        """)
        self.conn.commit()

    def create_booking(self, user_id, slots):
        res_id = str(uuid.uuid4())[:8]
        self.conn.execute(
            "INSERT INTO bookings VALUES (?,?,?,?,?,?)",
            (res_id, user_id,
             slots["check_in"], slots["check_out"],
             slots["room_type"], slots["guests"])
        )
        self.conn.commit()
        return res_id

    def update_booking(self, res_id, slots):
        cur = self.conn.execute(
            "UPDATE bookings SET check_in=?, check_out=? WHERE id=?",
            (slots["new_check_in"], slots["new_check_out"], res_id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def load_state(self, user_id):
        cur = self.conn.execute(
            "SELECT state, slots_json FROM convo_state WHERE user_id=?", (user_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        state, sj = row
        return state, json.loads(sj)

    def save_state(self, user_id, state, slots):
        self.conn.execute("""
            INSERT INTO convo_state(user_id, state, slots_json)
              VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              state = excluded.state,
              slots_json = excluded.slots_json
        """, (user_id, state, json.dumps(slots)))
        self.conn.commit()

    def clear_state(self, user_id):
        self.conn.execute("DELETE FROM convo_state WHERE user_id=?", (user_id,))
        self.conn.commit()
