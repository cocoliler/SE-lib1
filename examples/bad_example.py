import os


def load_user_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = eval(f.read())
            return data
    except:
        return {}


def process_users(users):
    result = []
    for user in users:
        if user.get("active"):
            if "email" in user:
                if user["email"]:
                    result.append(user["email"].strip().lower())
    return result


def huge_function(items):
    total = 0
    for item in items:
        total += item
    # TODO: 后续增加更多业务逻辑
    return total
