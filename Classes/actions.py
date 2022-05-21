from itertools import repeat
import discord
import urllib.request
import json
import re

from Classes.roll import DiceRoll
from Classes.modifier import Modifier


async def single_roll(base,context, *arg_list):
    dice = []
    bonuses = []
    arguments = [*arg_list]
    is_sum = determine_if_sum(arguments)
    if is_sum: 
      for i,a in enumerate(arguments):
        res = a.translate({ord(x): None for x in '()'})
        arguments[i] = res
    for v in arguments:
      if str(v[0]) == '+' or str(v[0]) =='-':
        bonuses.append(Modifier(str(v[0]),int(v[1:])))
      else:
        dice.append(v)
    msg = create_url(base,dice)
    username = context.author.display_name
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
      await context.send('You can only sum one batch of dice at a time')
      return

    for i,v in enumerate(batches):
      if i >= len(bonuses):
        results_embed.add_field(name=f"roll #{str(i+1)}", value=f"{v.val_string}", inline=False)
      else:
        originals = run_modifications(bonuses[i].sign,bonuses[i].value,v) if not is_sum else run_modifications_for_sum(bonuses[i].sign,bonuses[i].value,v)
        results_embed.add_field(name=f"roll #{str(i+1)}", value=f"{v.val_string} : {build_modified_string(originals, bonuses[i].sign,bonuses[i].value,is_sum)}", inline=False)
    await context.send(embed=results_embed)    

async def multi_roll(base,context, *arg_list):
    dice = []
    bonuses = []
    arguments = [*arg_list]
    batch_repeat = 0
    is_sum = determine_if_sum(arguments)
    if is_sum: 
      for i,a in enumerate(arguments):
        res = a.translate({ord(x): None for x in '()'})
        arguments[i] = res
    for v in arguments:
        if str(v[0]) == '+' or str(v[0]) =='-':
            bonuses.append(Modifier(str(v[0]),int(v[1:])))
        elif str(v[0]) == '#':
            batch_repeat = int(v[1:])
        else:
            dice.append(v)
    msg = create_url(base,dice)
    username = context.author.display_name
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
      await context.send('You can only sum one batch of dice at a time')
      return

    for i,v in enumerate(batches):
      if i >= len(bonuses):
        results_embed.add_field(name=f"roll #{str(i+1)}", value=f"{v.val_string}", inline=False)
      else:
        originals = run_modifications(bonuses[i].sign,bonuses[i].value,v) if not is_sum else run_modifications_for_sum(bonuses[i].sign,bonuses[i].value,v)
        results_embed.add_field(name=f"roll #{str(i+1)}", value=f"{v.val_string} : {build_modified_string(originals, bonuses[i].sign,bonuses[i].value,is_sum)}", inline=False)
    await context.send(embed=results_embed)    

def create_url(base_url,arg_array):
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

def roll_dice(url):
   with urllib.request.urlopen(url) as r:
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