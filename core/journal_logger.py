import yaml, logging
import psycopg2
from datetime import date

# — load DB creds —
with open("config/secrets.yaml", "r") as f:
    cfg = yaml.safe_load(f)

DB_PARAMS = {
    "host":     cfg["pg_host"],
    "port":     cfg["pg_port"],
    "dbname":   cfg["pg_name"],
    "user":     cfg["pg_user"],
    "password": cfg["pg_password"],
}

# — logging setup —
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def log_trade(trade_data):
    """
    trade_data should include:
      - symbol          (str)
      - qty             (int)
      - entry_price     (float)
      - stop_loss       (float)
      - risk_amount     (float)
      - confidence_score(float), optional
      - setup_tag       (str),    optional
      - review_notes    (str),    optional
      - r_multiple      (float),  optional
    """
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur  = conn.cursor()

        insert_sql = """
        INSERT INTO trades (
          date,
          symbol,
          num_shares,
          buy_price,
          position_size,
          sell_date,
          sell_price,
          net_pnl,
          net_roi,
          notes,
          risk_amount,
          r_multiple,
          setup_tag,
          confidence_score,
          review_notes,
          failure_reasons,
          success_reasons
        )
        VALUES (
          %s, %s, %s, %s, %s,
          %s, %s, %s, %s, %s,
          %s, %s, %s, %s, %s,
          %s, %s
        )
        """

        # map our data into your schema
        values = (
            date.today(),                           # date
            trade_data["symbol"],
            trade_data["qty"],                      # num_shares
            trade_data["entry_price"],              # buy_price
            trade_data["qty"] * trade_data["entry_price"],  # position_size
            None,                                    # sell_date
            0.0,                                     # sell_price
            0.0,                                     # net_pnl
            0.0,                                     # net_roi
            "",                                      # notes
            trade_data["risk_amount"],
            trade_data.get("r_multiple"),
            trade_data.get("setup_tag"),
            trade_data.get("confidence_score"),
            trade_data.get("review_notes", ""),
            "",  # failure_reasons
            ""   # success_reasons
        )

        cur.execute(insert_sql, values)
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"✅ Trade logged: {trade_data['symbol']} x{trade_data['qty']}")

    except Exception as e:
        logger.error(f"❌ Couldn’t log trade to DB: {e}")


def get_open_trades():
    """Fetch all trades from the DB that are still open."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        cur.execute("""
            SELECT ref, symbol, num_shares, buy_price
            FROM trades
            WHERE sell_price = 0.0 AND sell_date IS NULL
        """)
        trades = cur.fetchall()
        cur.close()
        conn.close()

        # Format as list of dicts for easier use
        return [
            {
                "ref": row[0],
                "symbol": row[1],
                "qty": row[2],
                "buy_price": row[3]
            }
            for row in trades
        ]

    except Exception as e:
        logger.error(f"❌ Couldn’t fetch open trades: {e}")
        return []
    

def update_closed_trade(update_data):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        update_sql = """
        UPDATE trades
        SET sell_date = %s,
            sell_price = %s,
            net_pnl = %s,
            net_roi = %s
        WHERE ref = %s
        """

        values = (
            update_data["sell_date"],
            update_data["sell_price"],
            update_data["net_pnl"],
            update_data["net_roi"],
            update_data["ref"]
        )

        cur.execute(update_sql, values)
        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"✅ Trade ref {update_data['ref']} marked as closed.")
    except Exception as e:
        logger.error(f"❌ Failed to update closed trade: {e}")