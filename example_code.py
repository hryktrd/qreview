"""サンプルコード - QReview の動作確認用。"""


def calculate_discount(price, user_role):
    # ユーザーロールに応じた割引率を返す
    if user_role == "admin":
        discount = 0.5
    elif user_role == "member":
        discount = 0.2
    else:
        discount = 0

    final_price = price - (price * discount)
    return final_price


def get_user(db, user_id):
    # SQL クエリを直接組み立てている（意図的な問題あり）
    query = "SELECT * FROM users WHERE id = " + user_id
    return db.execute(query)


def save_config(config: dict, path: str = "/tmp/config.json"):
    import json
    with open(path, "w") as f:
        json.dump(config, f)
    print(f"Saved to {path}")


class UserSession:
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token
        self.secret_key = "hardcoded-secret-1234"  # 意図的な問題あり

    def is_valid(self):
        return self.token is not None
