async def m001_add_numbers(db):
    """
    Creates a hash check table.
    """
    await db.execute(
        f"""
        CREATE TABLE numbers.games (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            wallet TEXT NOT NULL,
            user TEXT NOT NULL,
            haircut INTEGER NOT NULL DEFAULT 5 CHECK(haircut <= 50),
            closing_date TIMESTAMP NOT NULL,
            buy_in_max INTEGER NOT NULL,
            height_number INTEGER NOT NULL,
            block_height TEXT NOT NULL,
            odds INTEGER NOT NULL,
            completed BOOLEAN,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
        """
    )


async def m001_add_players(db):
    """
    Creates a hash check table.
    """
    await db.execute(
        f"""
        CREATE TABLE numbers.players (
            id TEXT PRIMARY KEY,
            game_id TEXT NOT NULL,
            height_number TEXT NOT NULL,
            buy_in INTEGER NOT NULL,
            ln_address TEXT NOT NULL,
            paid BOOLEAN,
            owed INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
        """
    )
