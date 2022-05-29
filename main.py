import discord
import os
import json
import sys
import re

from discord.flags import Intents
from dataclasses import asdict
import requests

sys.path.append('Classes')
from itertools import chain
from discord.ext import commands
from dotenv import load_dotenv
from Classes.roll import Roll


load_dotenv()

#my_secret = os.environ.get("TOKEN")
INTENTS = discord.Intents.default()
my_secret = os.getenv("TOKEN")

client = commands.Bot(command_prefix='!',description='Now with more moreness!', case_insensitive=True, intents=INTENTS)
#base_url = 'http://localhost:7071/api/roll'
base_url = os.getenv("BASE_URL")

@client.event
async def on_ready():
  channelName = client.guilds
  print(f"Hello world! Looks like I've woken up in {channelName[0]}")

@client.command()
async def roll(ctx,*args):
  dice = [] # this becomes a list of tuples with the batch pairings
  bonuses = []
  arguments = [*args]
  is_sum = determine_if_sum(arguments) # this can stay - we still want the sum functionality in, but we're going to simply return the Sum attr of the response from the api

  
  def handle_args(args):
    for i, v in enumerate(args):
        if str(v[0]) not in ['+', '-']:
            dice.append([v])
        else:
            try:
                if len(dice[-1]) > 1:
                    raise
                dice[-1].append(v)
            except:
                print("You have a modifier without a roll")

  handle_args(arguments)

  message_body={"dice":[]}

  def build_dice_list(batch):
    pattern = re.compile('([-|+])')
    mod, neg = None, None
    quantity, sides =[int(x) for x in str.upper(batch[0]).split('D')]
    
    if len(batch)>1:
      _, sign, mod = re.split(pattern, batch[1])
      neg = True if sign == '-' else False 
    
    roll = Roll(
    quantity,sides,int(mod),neg
    ) if not neg is None else Roll(quantity,sides)
    b = asdict(roll)
    message_body['dice'].append(b)

  username = ctx.author.display_name
  results_embed = discord.Embed()
  results_embed.set_author(name=f"-- {username} has rolled the dice! --")

  try:
    for roll in dice:
      build_dice_list(roll)
  except (ValueError, TypeError):
    results_embed.add_field(name="Buuuuuut...", value="something went wrong - please check what you're rolling")
    await ctx.send(embed=results_embed)
  response = requests.post(url=base_url,json=message_body).json()

  

  val=[]



  for i,v in enumerate(response):
    val = ''
    is_modified = determine_if_modified(v)
    if is_sum:
      val = f"Total = {v['sum']} "
    else:
      totals = v["results"]
      val = f" Result = {v['sum']}" if len(v['detail']) == 1 else f"{' , '.join([str(t) for t in totals])}"
      if is_modified:
        val += f" : ({', '.join([d for d in v['detail']])})"

    results_embed.add_field(name=f"Roll #{i+1}",value=val, inline=False)
    
  await ctx.send(embed=results_embed)



def determine_if_sum(arg_list):
  p = re.compile(r'[()]')
  for i in arg_list:
    if p.match(i):
      return True
    else:
      return False
def determine_if_modified(res):
  pattern = re.compile('([-|+])')
  details = "".join([d for d in res['detail']])
  return bool(re.search(pattern=pattern, string=details))

client.run(my_secret)