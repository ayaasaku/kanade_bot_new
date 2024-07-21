import aiosqlite

import discord
from discord import app_commands, ui, Interaction, SelectOption
from discord.ext import commands
from discord.app_commands import Choice
from discord.ui import (Select, View, select)   

from modules.main import defaultEmbed, errEmbed, successEmbed
from account.modules.register import check_user_account
from sekai.sekai_modules.main import get_data

from data.emoji_data import *

class SekaiAccountCog(commands.Cog, name='account'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        global none_embed
        none_embed = errEmbed(
            '玩家ID不存在',
            f'也許該名玩家還沒注冊？\n可以使用 `/register` 來註冊') 

            
    @app_commands.command(name='id', description='查看一個玩家的ID') 
    @app_commands.choices(option=[
        Choice(name='jp', value='jp'),
        Choice(name='tw', value='tw'),
        Choice(name='en', value='en'),
        Choice(name='kr', value='kr')])  
    @app_commands.rename(person='其他玩家')
    async def id(self, interaction: Interaction, option: str, person: discord.User = None):
        await interaction.response.defer()
        db = await aiosqlite.connect("kanade_data.db")
        cursor = await db.cursor()
        if person == None:
            discord_id = interaction.user.id
            name = interaction.user.display_name
            avatar = interaction.user.display_avatar
        else:
            discord_id = person.id
            name = person.display_name
            avatar = person.display_avatar
            
        await cursor.execute(f'SELECT player_id_{option} from user_accounts WHERE discord_id = ?', (str(discord_id),))
        player_id = await cursor.fetchone()
        
        if player_id[0] is None or player_id[0] == None:
            embed = none_embed
            await interaction.followup.send(embed=embed, ephemeral= True)
        else:
            player_id = player_id[0]
            embed = defaultEmbed(f'{player_id}')
            embed.set_author(name=f'{name}的玩家ID', icon_url=avatar)
            await interaction.followup.send(embed=embed)

    '''class RegisterModal(ui.Modal, title=f'註冊帳戶'):   
        player_id = ui.TextInput(label='玩家id', style=discord.TextStyle.short, required=True)
    
    async def on_submit(self, interaction: Interaction):
        db = await aiosqlite.connect("kanade_data.db")
        cursor = await db.cursor()
        discord_id = str(interaction.user.id)
        player_id = str(self.RegisterModal.player_id)
        name = interaction.user.display_name
        check = await check_user_account(discord_id = str(interaction.user.id), db=db, server=self.RegisterView.select_server.values[0])
        if check == True: 
            embed = errEmbed(
            '帳號已經存在',
            '你已經註冊過帳號了，不需要再註冊囉')
            await interaction.response.send_message(embed=embed)
        else:
            api = await get_data(server=self.RegisterView.select_server.values[0], type='api', path=f'/profile/{self.RegisterView.select_server.values[0]}/{self.RegisterModal.player_id}')
            none = {}
            if api != none:  
                await cursor.execute(f'INSERT INTO user_accounts(discord_id, player_id_{self.RegisterView.select_server.values[0]}) VALUES(?, ?)', (discord_id, player_id))
                await db.commit()
                if self.RegisterView.select_server.values[0] == 'tw':
                    title = '** 台服帳號註冊成功 **'
                elif self.RegisterView.select_server.values[0] == 'jp':
                    title = '** 日服帳號註冊成功 **'
                elif self.RegisterView.select_server.values[0] == 'en':
                    title = '** en 服帳號註冊成功 **'
                elif self.RegisterView.select_server.values[0] == 'kr':
                    title = '** kr 服帳號註冊成功 **'
                description = f'{name}，感謝使用奏寶，帳號已設置成功。'
                embed = successEmbed(title, description)
                embed.set_author(name=interaction.user.display_name, icon_url= interaction.user.display_avatar)
                embed.add_field(name=f'ID: ', value=self.RegisterModal.player_id, inline=False)
                await interaction.response.send_message(embed=embed, ephemeral= True)
            if api == none:
                embed = errEmbed(
                '玩家ID不存在',
                f'請確定一下是否輸入了正確的ID')
                await interaction.response.send_message(embed=embed, ephemeral= True)
    
   
                    
    class RegisterView():
        register_view = View()
        
        select_server = Select(placeholder=None, min_values=1, max_values=1, options=[
            SelectOption(label='tw', value = 'tw'), 
            SelectOption(label='jp', value = 'jp'), 
            SelectOption(label='en', value = 'en'), 
            SelectOption(label='kr', value = 'kr'), 
        ])
        
        register_view.add_item(select_server)
        
        async def select_server_callback(self):
            await self.interaction.followup.send(view=self.RegisterModal())
        
        select_server.callback(select_server_callback()) 

    @app_commands.command(name='register', description='註冊玩家ID')    
    async def register(self, interaction: discord.Interaction):
        self.interaction = interaction
        await interaction.response.defer()
        await interaction.followup.send(view=self.RegisterView.register_view, ephemeral= True)'''
        

    class RegisterModal(ui.Modal, title=f'註冊帳戶'):
        def __init__(self, select:Select):
            super().__init__(timeout=None)
            self.select_server = select
        player_id = ui.TextInput(label='玩家id', style=discord.TextStyle.short, required=True)

        async def on_submit(self, interaction: discord.Interaction):
            db = await aiosqlite.connect("kanade_data.db")
            cursor = await db.cursor()
            discord_id = str(interaction.user.id)
            player_id = str(self.player_id)
            name = interaction.user.display_name
            
            await cursor.execute(f'SELECT player_id_{self.select_server.values[0]} from user_accounts WHERE discord_id = ?', (discord_id,))
            result = await cursor.fetchone()
            await db.commit()
            if result[0] == None or result is None:
                none = {}
                api = await get_data(server=self.select_server.values[0], type='api', path=f'/profile/{self.select_server.values[0]}/{self.player_id}')
                if api != none:  
                    all_servers = ['tw', 'jp', 'kr', 'en']
                    for server in all_servers:
                        await cursor.execute(f'SELECT player_id_{server} from user_accounts WHERE discord_id = ?', (discord_id,))
                        result = await cursor.fetchone()
                        if result[0] != None or result is None:
                            await cursor.execute(f"UPDATE user_accounts SET player_id_{server} = ? WHERE discord_id = {discord_id}", (player_id,))
                            await db.commit()
                    else:
                        await cursor.execute(f'INSERT INTO user_accounts(discord_id, player_id_{self.select_server.values[0]}) VALUES(?, ?)', (discord_id, player_id))
                        await db.commit()
                    
                    if self.select_server.values[0] == 'tw':
                        title = '** 台服帳號註冊成功 **'
                    elif self.select_server.values[0] == 'jp':
                        title = '** 日服帳號註冊成功 **'
                    elif self.select_server.values[0] == 'en':
                        title = '** en 服帳號註冊成功 **'
                    elif self.select_server.values[0] == 'kr':
                        title = '** kr 服帳號註冊成功 **'
                        
                    description = f'{name}，感謝使用奏寶，帳號已設置成功。'
                    embed = successEmbed(title, description)
                    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
                    embed.add_field(name='ID: ', value=self.player_id, inline=False)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    
                elif api == none:
                    embed = errEmbed(
                        '玩家ID不存在',
                        f'請確定一下是否輸入了正確的ID'
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = errEmbed(
                    '帳號已經存在',
                    '你已經註冊過帳號了，不需要再註冊囉'
                )
                await interaction.response.send_message(embed=embed)

    class RegisterView(View):
        @select(placeholder=None,
            options=[
                SelectOption(label='tw', value='tw'),
                SelectOption(label='jp', value='jp'),
                SelectOption(label='en', value='en'),
                SelectOption(label='kr', value='kr'),
            ])
        async def select_server_callback(self, interaction: Interaction, select: Select):
            await interaction.response.send_modal(SekaiAccountCog.RegisterModal(select))  


    @app_commands.command(name='register', description='註冊玩家ID')
    async def register(self, interaction: discord.Interaction):
        self.interaction = interaction
        await interaction.response.defer()
        await interaction.followup.send(view=SekaiAccountCog.RegisterView(), ephemeral=True)
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SekaiAccountCog(bot))