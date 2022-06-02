import sys
sys.path.append("..")
from src.functions.roll_functions import (build_dice_list, handle_args,
                                            respond_to_roll)


def test_handle_arguments():
    arguments = ['1d100', '+10', '1d100', '+23']
    expected_dice = [['1d100', '+10'], ['1d100', '+23']]

    dice = handle_args(arguments)

    assert dice == expected_dice

def test_build_dice_list_not_sum():
    batch = ['1d100', '+10']
    expected = {"number":1, "sides":100, "mod":10, "neg":False}
    dice_list = build_dice_list(batch=batch, is_sum=False)
    assert expected == dice_list

def test_respond_to_roll_not_sum():
    resp={"sum": 19, "results": [4, 5, 5, 5], "detail": ["3 + 1", "4 + 1", "4 + 1", "4 + 1"]}
    expected = "4 , 5 , 5 , 5 : (3 + 1, 4 + 1, 4 + 1, 4 + 1)"
    val = respond_to_roll(resp, False)
    assert expected == val