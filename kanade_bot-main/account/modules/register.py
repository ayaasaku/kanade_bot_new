import aiosqlite

async def check_user_account(discord_id: str, server: str):
    db = await aiosqlite.connect("kanade_data.db")
    cursor = await db.cursor()
    print(server)
    await cursor.execute(f'SELECT player_id_{server} from user_accounts WHERE discord_id = ?', (discord_id,))
    result = await cursor.fetchone()
    await db.commit()
    if result is None or result == None:
        return False
    else:
        return True
