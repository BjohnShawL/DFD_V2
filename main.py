import discord
import os
import urllib.request
import json
import sys


sys.path.append('Classes')
from itertools import chain
from discord.ext import commands
from dotenv import load_dotenv
from Classes.roll import DiceRoll
from Classes.modifier import Modifier

#load_dotenv()

my_secret = os.environ.get("TOKEN")
#my_secret = os.getenv("TOKEN")
client = commands.Bot(command_prefix='!',description='Now with more moreness!', case_insensitive=True)
base_url = 'http://roll.diceapi.com/json/'


@client.event
async def on_ready():
  channelName = client.guilds
  print(f"Hello world! Looks like I've woken up in {channelName[0]}")

@client.command()
async def sum_up(ctx, *args):
  await ctx.send(f"{sum(list(map(int,args)))}")

@client.command()
async def roll(ctx,*args):
  
  dice = []
  bonuses = []

  for v in args:
    if str(v[0]) == '+' or str(v[0]) =='-':
      bonuses.append(Modifier(str(v[0]),int(v[1:])))
    else:
      dice.append(v)
  msg = create_url(dice)
  username = ctx.author.display_name
  val=[]
  
  for v in msg['dice'] :
      val.append(v['value'])
  results_embed = discord.Embed()
  results_embed.set_author(name=f"-- {username} has rolled the dice! --")
  
  

  batches = []
  
  for i,v in enumerate(dice):
    results= []
    endSlice = i+int(v[0:v.index('d')]) if int(v[0]) <= len(msg['dice']) -1 else int(v[0]) + 1 #this allows us to get all the results from the dice pool
    results.append(val[i:endSlice])
    d_roll = DiceRoll(v[0],results)

    batches.append(d_roll)

 # print(batches)

  for i,v in enumerate(batches):
    if i >= len(bonuses):
      results_embed.add_field(name=f"roll #{str(i+1)}", value=f"{v.val_string}", inline=False)
    else:
      mod_sign = bonuses[i].sign
      mod_val = bonuses[i].value
      originals = []
      for o in v.val_string.split(','):
        originals.append(int(o))

      for f in v.values:
        modified = modify(mod_sign,mod_val,f[0])
        f[0] = modified
      v.update_val_string()
      results_embed.add_field(name=f"roll #{str(i+1)}", value=f"{v.val_string} ({build_modified_string(originals, mod_sign,mod_val)})", inline=False)
  await ctx.send(embed=results_embed)


def create_url(arg_array):
  arr_len = len(arg_array)
  if arr_len == 1:
    result = roll_dice(base_url + str(arg_array[0]))
    #result = base_url + str(arg_array[0])
    return result
  else:
    url_path = "" 
    for a in arg_array:
      if str(a[0]) == ('+' or '-'):
        continue
      url_path+= f"{a}/"
    result = roll_dice(base_url + url_path)
    return result


def roll_dice(url):
   with urllib.request.urlopen(url) as r:
      result = json.loads(r.read().decode(r.headers.get_content_charset('utf-8')))
      return result

def modify(sign,modifier,value) -> int:
  return modifier + value if sign == '+' else value - modifier
    
def build_modified_string(originals,sign,value):
  #print(originals)
  explanation = ""
  #flat_list = list(chain.from_iterable(originals))
  for i in originals:
    explanation += f"{str(i)} {sign} {str(value)}, "
  return explanation[:-2]



client.run(my_secret)