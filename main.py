import discord
from discord.ext import commands
import requests
import json
import aiohttp
import random

intents = discord.Intents.all()

client = commands.Bot(command_prefix='!',intents=discord.Intents.all())

pokemon_cache = {}

@client.event
async def on_ready():
    print("Bot is ready")
    print("------------")

@client.command()
async def commands(ctx):
    embed = discord.Embed(title="Command List", description="List of available commands:", color=0x00ff00)
    embed.add_field(name="!start <difficulty> <type>", value="Starts the Pokemon guessing game with specified difficulty and type", inline=False)
    embed.add_field(name="!help", value="Shows the list of available commands", inline=False)
    await ctx.send(embed=embed)

@client.command()
async def start(ctx, difficulty: str, *types: str):
    difficulty = difficulty.lower()
    types = [t.lower() for t in types]

    if difficulty not in ['easy', 'medium', 'hard']:
        await ctx.send("Invalid difficulty level. Please specify easy, medium, or hard.")
        return

    if not types:
        await ctx.send("Please specify at least one Pokemon type: water, fire, grass, electric, etc.")
        return

    pokemon_list = []

    if difficulty == 'easy':
        max_gen = 1
    elif difficulty == 'medium':
        max_gen = 3
    elif difficulty == 'hard':
        max_gen = 9

    async with aiohttp.ClientSession() as session:
        for i in range(1, max_gen * 151 + 1):
            if str(i) in pokemon_cache:
                pokemon_data = pokemon_cache[str(i)]
            else:
                async with session.get(f"https://pokeapi.co/api/v2/pokemon/{i}") as response:
                    if response.status == 200:
                        pokemon_data = await response.json()
                        pokemon_cache[str(i)] = pokemon_data

            pokemon_name = pokemon_data['name']
            pokemon_types = [t['type']['name'] for t in pokemon_data['types']]
            if any(p_type in types for p_type in pokemon_types):
                pokemon_image_url = pokemon_data['sprites']['front_default']
                pokemon_list.append((pokemon_name, pokemon_image_url))

    if pokemon_list:
        pokemon_name, pokemon_image_url = random.choice(pokemon_list)
        resized_image_url = f"{pokemon_image_url}?size=400"

        embed = discord.Embed(title="Guess that Pokemon!", color=0x04D9FF)
        embed.set_image(url=resized_image_url)

        await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel and m.content.lower() == pokemon_name

        while True:
            user_guess = await client.wait_for('message', check=check)
            if user_guess.author == ctx.author:
                congrats_embed = discord.Embed(title="Congratulations!",
                                               description=f"Correct! You guessed the Pokemon name correctly: **{pokemon_name}**",
                                               color=0xFFD700)
                congrats_embed.set_image(url="https://giffiles.alphacoders.com/130/130540.gif")
                await ctx.send(embed=congrats_embed)
                break
    else:
        await ctx.send("No Pokemon found matching the specified criteria.")

client.run("MTIxMTE0NzU3MjQxMzA3MTQ0MQ.Gu2Yp2.Ey9BDU2ElstfIlPEAQ-Uz0sxFENUtBk7qNABJc")

