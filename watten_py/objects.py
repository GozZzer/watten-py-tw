import datetime
import json
import uuid


class Client:
    def __init__(self, user_id: uuid.UUID, username: str, email: str = None):
        self.user_id: uuid.UUID = user_id
        self.username = username
        self.email = email

    def __str__(self):
        return f"<Client {self.username}>"

    @classmethod
    def get_user(cls, username: str, password: str):
        dta = None
        with open("watten_py/user_data.json", "r") as f:
            data = json.load(f)
            user_id = [user_id for user_id in data if data[user_id]["username"] == username]
            try:
                dta = data[user_id[0]]
            except IndexError:
                return "Invalid Username"

        if dta["password"] == password:
            return cls(
                user_id[0],
                dta["username"],
                dta["email"]
            )
        else:
            return "Invalid Password"

    @classmethod
    def get_user_by_node(cls, node):
        with open("watten_py/user_data.json", "r") as f:
            data = json.load(f)
            try:
                user_lst = [uuid.UUID(uid) for uid in data if uuid.UUID(uid).fields[5] == node]
                times = [datetime.datetime.fromtimestamp((u.time - 0x01b21dd213814000) * 100 / 1e9) for u in user_lst]
                try:
                    user = user_lst[times.index(max(times))]
                except ValueError:
                    return None
                try:
                    return cls(
                        user,
                        data[str(user)]["username"],
                        data[str(user)]["email"]
                    )
                except KeyError:
                    return cls(
                        user,
                        data[str(user)]["username"],
                    )
            except IndexError:
                return None

    @classmethod
    def new_user(cls, username: str, uuid: uuid.UUID, email: str = None, password: str = None):
        with open("watten_py/user_data.json", "r") as f:
            data = json.load(f)
            try:
                _ = [user_id for user_id in data if data[user_id]["username"] == username][0]
                return f"{username} is already used"
            except IndexError:
                pass
        with open("user_data.json", "w") as f:
            if email is None:
                data[str(uuid)] = {"username": username}
            data[str(uuid)] = {"username": username, "email": email, "password": password}
            json.dump(data, f, indent=4)
        return cls(
            uuid,
            username,
            email
        )


class Packet:
    def __init__(self, task_type: str, **kwargs):
        self.task_type = task_type
        self.data = kwargs

    def __str__(self):
        return f'<Packet task_type: "{self.task_type}">'
