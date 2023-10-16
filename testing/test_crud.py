import sys
import os
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

import src.crud_functions as crud_functions

def crud_challenges_success():
    ch1 = {
        "_id": "6524bec1adb7238a3c812a8b",
        "email": "yl1@yl.com",
        "image_name": "blabla",
        "image_ver": "2.0"
    }
    
    ch2 = {
        "_id": "6524c308d74b9e961ddcdb1a", 
        "email": "yl1@yl.com",
        "image_name": "blabla",
        "image_ver": "1.0"
    }

    update_ch2 = {
        "_id": "6524c308d74b9e961ddcdb1a", 
        "email": "yl1@yl.com",
        "image_name": "hellobyebye",
        "image_ver": "2.0"
    }
    
    challenges = [ch1, ch2]

    for data in challenges:
        print(f'Add Challenge: {crud_functions.add_challenge(data)}\n\n')
    print(f'Get All Challenges: {crud_functions.get_all_challenges()}\n')
    print(f'Get Challenge By Id: {crud_functions.get_challenge_by_ids({"_id": [ "6524bec1adb7238a3c812a8b" ]})}\n\n')
    print(f'Update Challenge by Id: {crud_functions.update_challenge_by_id(update_ch2)}\n\n')
    print(f'Delete challenge by Id: {crud_functions.delete_challenges_by_ids({"_id": ["6524bec1adb7238a3c812a8b", "6524c308d74b9e961ddcdb1a"]})}\n\n')


def test_delete_all():
    print(f'{crud_functions.delete_all_challenges()}\n\n')
    print(f'{crud_functions.get_all_challenges()}\n\n')

if __name__ == '__main__':
    crud_challenges_success()
    # test_delete_all()
