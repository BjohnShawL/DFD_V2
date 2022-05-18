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
from Classes.roll import DiceRoll, Roll
from Classes.modifier import Modifier
from Classes.actions import single_roll, multi_roll

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

@client.event
async def on_voice_state_update(member, before, after):
  debugger = "debug"
  # = client.get_role('conference_speaker')
  await print("role")
  # if role in member.roles :
  #   if before.voice.self_mute == True and after.voice.self_mute == False:
  #     print("conference_user talking")
  #   elif before.voice.self_mute == False and after.voice.self_mute == True:
  #     print("conference_user no longer talking")


@client.command()
async def sum_up(ctx, *args):
  await ctx.send(f"{sum(list(map(int,args)))}")

@client.command()
async def batch(ctx,*args):
  await multi_roll(base_url,ctx,*args)


@client.command()
async def roll(ctx,*args):
  dice = [] # this becomes a list of tuples with the batch pairings
  bonuses = []
  arguments = [*args]
  is_sum = determine_if_sum(arguments) # this can stay - we still want the sum functionality in, but we're going to simply return the Sum attr of the response from the api
  # if is_sum: 
  #   for i,a in enumerate(arguments):
  #     res = a.translate({ord(x): None for x in '()'})
  #     arguments[i] = res
  
  def handle_args(args):
    for i, v in enumerate(args):
        if str(v[0]) not in ['+', '-']:
            print(v[0])
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
    quantity, sides =[int(x) for x in str.upper(batch[0]).split('D')]
    _, sign, mod = re.split(pattern, batch[1])
    neg = True if sign == '-' else False 
    roll = Roll(
    quantity,sides,int(mod),neg
    )
    b = asdict(roll)
    message_body['dice'].append(b)

  for roll in dice:
    build_dice_list(roll)

  response = requests.post(url=base_url,json=message_body).json()

  

  username = ctx.author.display_name
  val=[]
  for v in msg['dice'] :
      val.append(v['value'])
  results_embed = discord.Embed()
  results_embed.set_author(name=f"-- {username} has rolled the dice! --")
  batches = []
  for i,v in enumerate(dice):
    results= []
    endSlice = i+int(v[0:v.lower().index('d')]) if int(v[0]) <= len(msg['dice']) -1 else int(v[0]) + 1 #this allows us to get all the results from the dice pool
    results.append(val[i:endSlice])
    d_roll = DiceRoll(v[0],results)
    batches.append(d_roll)
  if len(batches)>1 and is_sum:
    await ctx.send('You can only sum one batch of dice at a time')
    return

  for i,v in enumerate(batches):
    if i >= len(bonuses):
      results_embed.add_field(name=f"roll #{str(i+1)}", value=f"{v.val_string}", inline=False)
    else:
      originals = run_modifications(bonuses[i].sign,bonuses[i].value,v) if not is_sum else run_modifications_for_sum(bonuses[i].sign,bonuses[i].value,v)
      results_embed.add_field(name=f"roll #{str(i+1)}", value=f"{v.val_string} : {build_modified_string(originals, bonuses[i].sign,bonuses[i].value,is_sum)}", inline=False)
  await ctx.send(embed=results_embed)

def run_modifications(mod_sign,mod_val,val_array):
    originals = []
    for o in val_array.val_string.split(','):
      originals.append(int(o))
    for i,f in enumerate(val_array.values[0]):
        modified = modify(mod_sign,mod_val,f)
        val_array.values[0][i] = modified
    val_array.update_val_string()
    return originals 

def run_modifications_for_sum(mod_sign,mod_val,val_array):
    originals = []
    for o in val_array.val_string.split(','):
      originals.append(int(o))
    modified = modify(mod_sign,mod_val,sum(originals))
    val_array.values[0] = [modified]
    
    val_array.update_val_string()
    return originals  


def create_url(arg_array):
  arr_len = len(arg_array)
  if arr_len == 1:
    result = roll_dice(base_url + str(arg_array[0]))
    return result
  else:
    url_path = "" 
    for a in arg_array:
      if str(a[0]) == ('+' or '-'):
        continue
      url_path+= f"{a}/"
    result = roll_dice(base_url + url_path)
    return result

def roll_dice_update(url):
  # change this to use the requests library
  pass

def roll_dice(url):
   with urllib.request.urlopen(url) as r:
      response = r.read()
      result = json.loads(r.read().decode(r.headers.get_content_charset('utf-8')))
      return result

def modify(sign,modifier,value) -> int:
  return modifier + value if sign == '+' else value - modifier
    
def build_modified_string(originals,sign,value,is_sum):
  explanation = ""
  if is_sum:
    explanation +="({"
    terminator = "}"
    for index,val in enumerate(originals):
      explanation += f"{str(val)} + " if index <len(originals)-1 else f"{str(val)}{terminator}"
    explanation += f" {sign} {str(value)})"
  else:
    explanation +="("
    for i in originals:
      explanation += f"{str(i)} {sign} {str(value)}, " 
    explanation = explanation[:-2]
    explanation +=")"
  return explanation

def determine_if_sum(arg_list):
  p = re.compile(r'[()]')
  for i in arg_list:
    if p.match(i):
      return True
    else:
      return False

client.run(my_secret)