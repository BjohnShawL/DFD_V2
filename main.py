import discord
import os
import json
import sys
import re

from discord.flags import Intents
from dataclasses import asdict
import requests

sys.path.append('Classes')
from discord.ext import commands
from dotenv import load_dotenv
from src.functions.roll_functions import determine_if_sum, build_dice_list, handle_args, respond_to_roll


load_dotenv()

#my_secret = os.environ.get("TOKEN")
INTENTS = discord.Intents.default()
my_secret = os.getenv("TOKEN")

client = commands.Bot(command_prefix='!',description='Now with more moreness!', case_insensitive=True, intents=INTENTS)
base_url = 'http://localhost:7071/api/roll'
#base_url = os.getenv("BASE_URL")

@client.event
async def on_ready():
  channelName = client.guilds
  print(f"Hello world! Looks like I've woken up in {channelName[0]}")

@client.command()
async def roll(ctx,*args):
  username = ctx.author.display_name
  results_embed = discord.Embed()
  results_embed.set_author(name=f"-- {username} has rolled the dice! --")
  message_body={"dice":[]}
  arguments = [*args]
  is_valid_roll = False
  
  is_sum = determine_if_sum(arguments) # this can stay - we still want the sum functionality in, but we're going to simply return the Sum attr of the response from the api
  dice = handle_args(arguments)
    
  try:
    for roll in dice:
      b = build_dice_list(roll, is_sum)
      message_body['dice'].append(b)
  except (ValueError, TypeError):
    results_embed.add_field(name="Buuuuuut...", value="something went wrong - please check what you're rolling")
  else:
    is_valid_roll = True
  
  if is_valid_roll:
    response = requests.post(url=base_url,json=message_body).json()
    for i,v in enumerate(response):
      val =  respond_to_roll(v, is_sum)
      results_embed.add_field(name=f"Roll #{i+1}",value=val, inline=False)
  
  await ctx.send(embed=results_embed)


client.run(my_secret)