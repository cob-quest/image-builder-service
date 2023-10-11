import crud_functions

def create_users():
    user1 = {
        "_id": "6524bec1adb7238a3c812a8b",
        "email": "yl1@yl.com",
        "image_name": "blabla",
        "image_url": "https://gitlab.container.registry/xyz1",
        "image_ver": 2.0
    }
    
    user2 = {
        "_id": "6524c308d74b9e961ddcdb1a", 
        "email": "yl1@yl.com",
        "image_name": "blabla",
        "image_url": "https://gitlab.container.registry/abc",
        "image_ver": 2.0
    }

    return [user1, user2]


if __name__ == '__main__':
    for data in create_users():
        print(f'{crud_functions.add_challenge(data)}\n')
    print(f'{crud_functions.get_all_challenges()}\n')
    print(f'{crud_functions.get_challenge_by_ids({"_id": [ "6524bec1adb7238a3c812a8b" ]})}\n')