from Classes.roll import Roll
from dataclasses import asdict
import re


def determine_if_sum(arg_list):
  p = re.compile(r'[()]')
  for i in arg_list:
    if p.search(i):
      return True
    else:
      return False

def determine_if_modified(res):
  pattern = re.compile('([-|+])')
  details = "".join([d for d in res['detail']])
  return bool(re.search(pattern=pattern, string=details))

def build_dice_list(batch, is_sum):
    if is_sum:
      brackets = re.compile('[()]')
      for i, b in enumerate(batch):
        b = re.sub(brackets, '', b)
        batch[i] = b
    pattern = re.compile('([-|+])')
    mod, neg = None, None
    quantity, sides =[int(x) for x in str.upper(batch[0]).split('D')]
    
    if len(batch)>1:
      _, sign, mod = re.split(pattern, batch[1])
      neg = True if sign == '-' else False 
    
    roll = Roll(
    quantity,sides,int(mod),neg
    ) if not neg is None else Roll(quantity,sides)
    return asdict(roll)

def handle_args(args):
    dice = []
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
    return dice

def respond_to_roll(v, is_sum):
  val = ''
  is_modified = determine_if_modified(v)
  if is_sum:
    val = f"Total = {v['sum']} : ({', '.join([d for d in v['detail']])})"
  else:
    totals = v["results"]
    val = f" Result = {v['sum']}" if len(v['detail']) == 1 else f"{' , '.join([str(t) for t in totals])}"
    if is_modified:
      val += f" : ({', '.join([d for d in v['detail']])})"
  return val