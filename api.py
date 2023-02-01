import time
import requests
from datetime import datetime

URL_API = "https://blaze.com"
URL_WEB_PROXY = "https://us13.proxysite.com"


def add_results(acc, results):
    """

    :param acc:
    :param results:
    :return:
    """
    color, amount = results["color"], results["amount"]
    acc[color] = acc.get(color) or {}
    acc[color]["amount"] = acc[color].get("amount") or 0
    acc[color]["amount"] += amount
    return acc


class Browser(object):

    def __init__(self):
        self.response = None
        self.headers = None
        self.session = requests.Session()

    def set_headers(self, headers=None):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36"
        }
        if headers:
            for key, value in headers.items():
                self.headers[key] = value

    def get_headers(self):
        return self.headers

    def send_request(self, method, url, **kwargs):
        return self.session.request(method, url, **kwargs)


class BlazeAPI(Browser):

    def __init__(self, username=None, password=None):
        super().__init__()
        self.proxies = None
        self.token = None
        self.wallet_id = None
        self.username = username
        self.password = password
        self.set_headers()
        self.headers = self.get_headers()

    def auth(self):
        data = {
            "username": self.username,
            "password": self.password
        }
        self.headers["referer"] = f"{URL_API}/pt/?modal=auth&tab=login"
        self.response = self.send_request("PUT",
                                          f"{URL_API}/api/auth/password",
                                          json=data,
                                          headers=self.headers)

        if not self.response.json().get("error"):
            self.token = self.response.json()["access_token"]

        return self.response.json()

    def get_profile(self):
        self.headers["authorization"] = f"Bearer {self.token}"
        self.response = self.send_request("GET",
                                          f"{URL_API}/api/users/me",
                                          headers=self.headers)
        return self.response.json()

    def get_balance(self):
        self.headers["authorization"] = f"Bearer {self.token}"
        self.response = self.send_request("GET",
                                          f"{URL_API}/api/wallets",
                                          headers=self.headers)
        if self.response:
            self.wallet_id = self.response.json()[0]["id"]
        return self.response.json()

    def get_status(self):
        self.response = self.get_roulettes()
        if self.response:
            return self.response.json()["status"]
        return {"status": "rolling"}

    def get_ranking(self, **params):
        list_best_users = []
        while True:
            self.response = self.get_roulettes()
            if self.response:
                if self.response.json()["status"] == 'waiting':
                    for user_rank in self.response.json()["bets"]:
                        if user_rank["user"]["rank"] in params["ranks"]:
                            list_best_users.append(user_rank)
                    return list_best_users
            time.sleep(2)

    def get_trends(self):
        while True:
            self.response = self.get_roulettes()
            if self.response:
                if self.response.json()["status"] == 'waiting':
                    return self.response.json()
            time.sleep(2)

    def bets(self, color, amount):
        result_dict = {
            "result": False,
        }
        data = {
            "amount": str(f"{float(amount):.2f}"),
            "currency_type": "BRL",
            "color": 1 if color == "vermelho" else 2 if color == "preto" else 0,
            "free_bet": False,
            "wallet_id": self.wallet_id
        }

        self.headers["authorization"] = f"Bearer {self.token}"
        self.response = self.send_request("POST",
                                          f"{URL_API}/api/roulette_bets",
                                          json=data,
                                          headers=self.headers)
        if self.response:
            result_dict = {
                "result": True,
                "object": self.response,
                "message": "Operação realizada com sucesso!!!"
            }
        return result_dict

    def awaiting_result(self):
        while True:
            try:
                try:
                    self.response = self.get_roulettes()

                    if self.response.json()["status"] == "complete":
                        return self.response.json()
                except:
                    try:
                        self.response = self.get_roulettes()

                        if self.response.json()["status"] == "complete":
                            return self.response.json()
                    except:
                        self.response = self.get_roulettes()

                        if self.response.json()["status"] == "complete":
                            return self.response.json()
            except:
                pass
            time.sleep(1)

    def get_with_webproxy(self, url):
        data = {
            "server-option": "us13",
            "d": url,
            "allowCookies": "on"
        }
        self.headers["Origin"] = f"{URL_WEB_PROXY}"
        self.headers["Referer"] = f"{URL_WEB_PROXY}/"
        return self.send_request("POST",
                                 f"{URL_WEB_PROXY}/includes/process.php?action=update",
                                 data=data,
                                 headers=self.headers)

    def get_last_doubles(self, web_proxy=False):
        if not web_proxy:
            self.response = self.send_request("GET",
                                              f"{URL_API}/api/roulette_games/recent",
                                              proxies=self.proxies,
                                              headers=self.headers)
        else:
            self.response = self.get_with_webproxy(f"{URL_API}/api/roulette_games/recent")

        if self.response:
            result = {
                "items": [
                    {"color": "branco" if i["color"] == 0 else "vermelho" if i["color"] == 1 else "preto",
                     "value": i["roll"], "created_date": datetime.strptime(
                        i["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
                     } for i in self.response.json()]}
            return result
        return False

    def get_last_crashs(self, web_proxy=False):
        if not web_proxy:
            self.response = self.send_request("GET",
                                              f"{URL_API}/api/crash_games/recent",
                                              proxies=self.proxies,
                                              headers=self.headers)
        else:
            self.response = self.get_with_webproxy(f"{URL_API}/api/crash_games/recent")

        if self.response:
            result = {
                "items": [{"color": "preto" if float(i["crash_point"]) < 2 else "verde", "value": i["crash_point"]}
                          for i in self.response.json()]}
                          
            return result
        return False

    def get_roulettes(self, web_proxy=False):
        if not web_proxy:
            self.response = self.send_request("GET",
                                              f"{URL_API}/api/roulette_games/current",
                                              proxies=self.proxies,
                                              headers=self.headers)
        else:
            self.response = self.get_with_webproxy(f"{URL_API}/api/roulette_games/current")

        return self.response

    def get_all_results(self):
        while True:
            self.get_roulettes()
            if self.response.json()["status"] == "complete":
                bets = self.response.json()["bets"]
                cont_bets_color_0 = 0
                cont_bets_color_1 = 0
                cont_bets_color_2 = 0
                amount_bets_color_0 = 0
                amount_bets_color_1 = 0
                amount_bets_color_2 = 0
                status_bets_color_0 = None
                status_bets_color_1 = None
                status_bets_color_2 = None
                for bet in bets:
                    if bet["color"] == 1:
                        cont_bets_color_1 += 1
                        amount_bets_color_1 += float(bet["amount"])
                        status_bets_color_1 = bet["status"]
                    elif bet["color"] == 2:
                        cont_bets_color_2 += 1
                        amount_bets_color_2 += float(bet["amount"])
                        status_bets_color_2 = bet["status"]
                    else:
                        cont_bets_color_0 += 1
                        amount_bets_color_0 += float(bet["amount"])
                        status_bets_color_0 = bet["status"]

                print("TOTAL DE APOSTAS: ", len(bets))
                print(f"{cont_bets_color_0} pessoas apostaram no BRANCO, {cont_bets_color_1} "
                      f"pessoas apostaram no VERMELHO, {cont_bets_color_2} pessoas apostaram no PRETO ")
                print(f"Valor total de apostas no BRANCO: {amount_bets_color_0:.2f} status: {status_bets_color_0}, \n"
                      f"Valor total de apostas no VERMELHO: {amount_bets_color_1:.2f} status: {status_bets_color_1}, \n"
                      f"Valor total de apostas no PRETO: {amount_bets_color_2:.2f} status: {status_bets_color_2}")

                bets_roll_color = ["BRANCO", "VERMELHO", "PRETO"]
                bets_amount_list = [amount_bets_color_0, amount_bets_color_1, amount_bets_color_2]
                bets_status_list = [status_bets_color_0, status_bets_color_1, status_bets_color_2]

                for index, value in enumerate(bets_status_list):
                    if value == "win":
                        if bets_amount_list.index(max(bets_amount_list)) == index:
                            result = "MAIOR"
                        else:
                            result = "MENOR"
                        print(f"Giro anterior {self.response.json()['roll']}, cor {bets_roll_color[index]} >> {result}")
                        # print(f'{crash_point}')
                break

            time.sleep(0.5)
