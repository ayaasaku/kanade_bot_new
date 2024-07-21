import aiosqlite
import asyncio

async def main():
    db = await aiosqlite.connect("kanade_data.sqlite")
    cursor = await db.cursor()
    await cursor.execute("CREATE TABLE user_accounts (discord_id TEXT, player_id_tw TEXT, player_id_jp TEXT, player_id_en TEXT, player_id_kr TEXT)")
    await cursor.close()
    await db.commit()
    print('done')
    
asyncio.run(main())
