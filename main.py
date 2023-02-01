import time
from threading import Thread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
import webbrowser
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from api import BlazeAPI

ba = BlazeAPI("blazedemo@gmail.com", "blazedemo")

contribuicao = "https://www.vakinha.com.br/vaquinha/contribuicao-software-blaze-demo?utm_source=site&utm_medium=product-thanks-page"

def get_velas():
    lista = []
    last_crashs = ba.get_last_crashs()
    itens = last_crashs['items']
    for i in range(15):
        lista.append(itens[i]["value"])
    return lista

def wait_crash():
    v1 = get_velas()
    while True:
        v2 = get_velas()
        if v1 != v2:
            break
        time.sleep(0.5)
    return v2

def get_num():
    lista = []
    last_doubles = ba.get_last_doubles()
    num = (last_doubles["items"])
    n = len(num) - 1
    for i in range(15):
        lista.append(num[i]["value"])
        if n <= 0:
            break
        n -= 1
    return lista

def wait_double():
    v1 = get_num()
    while True:
        v2 = get_num()
        if v1 != v2:
            break
        time.sleep(0.5)
    return v2

def cor_double(pedra):
    if int(pedra) > 7:
        return str(pedra), (38/255, 47/255, 60/255, 1), (187/255, 190/255, 198/255, 1)
    elif int(pedra) == 0:
        return str(pedra), (255/255, 255/255, 255/255, 1), (241/255, 44/255, 76/255, 1)
    else:
        return str(pedra), (241/255, 44/255, 76/255, 1), (140/255, 16/255, 37/255, 1)

def cor_crash(vela):
    if float(vela) >= 2:
        return f"{vela}X", (4/255, 212/255, 124/255, 1), (0/255, 135/255, 95/255, 1)
    elif float(vela) == 0:
        return "1.00X", (52 / 255, 61 / 255, 74 / 255, 1), (188 / 255, 186 / 255, 192 / 255, 1)
    else:
        return f"{vela}X", (52/255, 61/255, 74/255, 1 ), (188/255, 186/255, 192/255, 1)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.podeentrartela = True
        self.entrarinstagram = True
        self.entrarlinkedin = True
        self.podemudarbanca = False
        self.podeentrarinfo = True
        self.ajuda = True

    def dialog_mudar_banca(self):
        if self.podemudarbanca:
            txt = MDTextField(
                hint_text="Valor da banca...",
                size_hint=(.9, .9),
                pos_hint={"center_x": 0.7, "center_y": 0.6},
                line_color_focus=(241/255, 44/255, 76/255),
                text_color_focus=(241 / 255, 44 / 255, 76 / 255),
                hint_text_color_focus=(241 / 255, 44 / 255, 76 / 255),
)

            self.dialog = MDDialog(
                title="Qual o valor da sua banca?",
                type="custom",
                content_cls=txt,
                buttons=[
                    MDFlatButton(
                        text="Cancelar",
                        theme_text_color="Custom",
                        text_color=(241/255, 44/255, 76/255),
                        on_release=lambda x: self.dialog.dismiss(force=True),
                    ),
                    MDFlatButton(
                        text="Ok",
                        theme_text_color="Custom",
                        text_color=(241/255, 44/255, 76/255),
                        on_release=lambda x: self.mudar_valor_banca(txt),
                    ),
                ],
            )
            self.dialog.open()
    def contribuicao(self):
        if self.ajuda:
            webbrowser.open_new(contribuicao)

    def mudar_valor_banca(self, valor):
        self.dialog.dismiss(force=True)
        if valor.text != "":
            try:
                Valor = float(valor.text)
            except:
                Valor = 40.0
            if Valor > 10_000:
                Valor = 10_000.0
            if Valor < 1:
                Valor = 1
            zero = round(Valor - int(Valor))
            if len(str(zero)) <= 3:
                Valor = f"{round(float(Valor), 2)}0"
            self.ids.banca_crash.text = Valor
            self.ids.banca_double.text = Valor

    def info(self):
        if self.podeentrarinfo:
            self.ids.info.pos_hint = {"center_y": 0.5}
            self.entrarinstagram = True
            self.entrarlinkedin = True

    def instagram(self):
        if self.entrarinstagram:
            webbrowser.open_new("https://www.instagram.com/s.soares_marcelo/")

    def linkedin(self):
        if self.entrarlinkedin:
            webbrowser.open_new("https://www.linkedin.com/in/marcelo-soares-codes/")

    def CrashScreen(self):
        if self.podeentrartela:
            self.ids.banca_crash.text = self.ids.banca_double.text
            self.ids.quantia_crash.text = ""
            self.ids.txt_retirar.text = ""
            self.ids.Crash_Screen.pos_hint = {"center_y": .5}
            t = Thread(target=self.ultimas_velas, daemon=True)
            t.start()
            self.parar_crash = False
            self.podeentrartela = False
            self.entrarinstagram = False
            self.entrarlinkedin = False
            self.podemudarbanca = True
            self.podeentrarinfo = False
            self.ajuda = False


    def DoubleScreen(self):
        if self.podeentrartela:
            self.ids.banca_double.text = self.ids.banca_crash.text
            self.ids.txt_quantia_double.text = ""
            self.cor = ""
            self.ids.Double_Screen.pos_hint = {"center_y": .5}
            t = Thread(target=self.ultimas_pedras, daemon=True)
            t.start()
            self.parar_double = False
            self.podeentrartela = False
            self.entrarinstagram = False
            self.entrarlinkedin = False
            self.podemudarbanca = True
            self.podeentrarinfo = False
            self.ajuda = False
            self.cor = ""
            self.ids.bt_branco.md_bg_color = (255/255, 255/255, 255/255)
            self.ids.bt_preto.md_bg_color = (52/255, 59/255, 74/255)
            self.ids.bt_vermelho.md_bg_color = (241/255, 44/255, 76/255)
            self.bets_double = []
            self.teveaposta = False

    def HomeScreen(self):
        self.ids.Crash_Screen.pos_hint = {"center_y": 10}
        self.ids.Double_Screen.pos_hint = {"center_y": 10}
        self.ids.info.pos_hint = {"center_y": 10}
        self.parar_crash = True
        self.parar_double = True
        self.podeentrartela = True
        self.entrarinstagram = True
        self.podemudarbanca = False
        self.podeentrarinfo = True
        self.ajuda = True

    def vela_crash(self, vela, velafundo, designer):
        vela.text = designer[0]
        vela.color = designer[2]
        velafundo.md_bg_color = designer[1]

    def pedra_double(self, num, circulo, fundo, designer):
        num.text = designer[0]
        fundo.md_bg_color = designer[1]
        circulo.md_bg_color = designer[2]

    def bloq_jogar(self):
        time.sleep(3)
        self.pode_jogar_crash = True
        self.ids.bt_comecar_crash.md_bg_color = (241 / 255, 44 / 255, 76 / 255)
        self.ids.subindo.color = 187 / 255, 190 / 255, 198 / 255, 0
        self.ids.barra_progresso_crash.color = 7/255, 27/255, 36/255, 1
        self.ids.barra_progresso_crash.back_color = 241 / 255, 44 / 255, 76 / 255, 1
        for i in range(110):
            self.ids.barra_progresso_crash.value = i
            time.sleep(0.062)
        self.pode_jogar_crash = False
        self.ids.bt_comecar_crash.md_bg_color = (150/255, 20/255, 50/255)
        self.ids.barra_progresso_crash.color = 7/255, 27/255, 36/255, 0
        self.ids.barra_progresso_crash.back_color = 7 / 255, 27 / 255, 36 / 255, 0
        self.ids.subindo.color = 187 / 255, 190 / 255, 198 / 255, 1

    def bloq_jogar_double(self):
        time.sleep(4)
        self.pode_jogar_double = True
        self.ids.girando.color = 187 / 255, 190 / 255, 198 / 255, 0
        self.ids.bt_comecar_double.md_bg_color = (241 / 255, 44 / 255, 76 / 255)
        self.ids.barra_progresso_double.color = 7/255, 27/255, 36/255, 1
        self.ids.barra_progresso_double.back_color = 241 / 255, 44 / 255, 76 / 255, 1
        for i in range(110):
            self.ids.barra_progresso_double.value = i
            time.sleep(0.155)
        self.pode_jogar_double = False
        self.ids.bt_comecar_double.md_bg_color = (150/255, 20/255, 50/255)
        time.sleep(1)
        self.ids.barra_progresso_double.color = 7/255, 27/255, 36/255, 0
        self.ids.barra_progresso_double.back_color = 7 / 255, 27 / 255, 36 / 255, 0
        self.ids.girando.color = 187 / 255, 190 / 255, 198 / 255, 1

    def ultimas_velas(self):
        while True:
            self.pode_jogar_crash = False
            velas = get_velas()
            self.vela_crash(self.ids.v1, self.ids.vv1, cor_crash(velas[0]))
            self.vela_crash(self.ids.v2, self.ids.vv2, cor_crash(velas[1]))
            self.vela_crash(self.ids.v3, self.ids.vv3, cor_crash(velas[2]))
            self.vela_crash(self.ids.v4, self.ids.vv4, cor_crash(velas[3]))
            self.vela_crash(self.ids.v5, self.ids.vv5, cor_crash(velas[4]))
            self.vela_crash(self.ids.v6, self.ids.vv6, cor_crash(velas[5]))
            self.vela_crash(self.ids.v7, self.ids.vv7, cor_crash(velas[6]))
            self.vela_crash(self.ids.v8, self.ids.vv8, cor_crash(velas[7]))
            self.vela_crash(self.ids.v9, self.ids.vv9, cor_crash(velas[8]))
            self.vela_crash(self.ids.v10, self.ids.vv10, cor_crash(velas[9]))
            self.vela_crash(self.ids.v11, self.ids.vv11, cor_crash(velas[10]))
            self.vela_crash(self.ids.v12, self.ids.vv12, cor_crash(velas[11]))
            self.vela_crash(self.ids.v13, self.ids.vv13, cor_crash(velas[12]))
            self.vela_crash(self.ids.v14, self.ids.vv14, cor_crash(velas[13]))
            self.vela_crash(self.ids.v15, self.ids.vv15, cor_crash(velas[14]))
            time.sleep(3)
            wait_crash()
            d = Thread(target=self.bloq_jogar, daemon=True)
            d.start()
            if self.parar_crash:
                break

    def ultimas_pedras(self):
        while True:
            self.pode_jogar_double = False
            pedras = get_num()
            self.pedra_double(self.ids.c1, self.ids.cc1, self.ids.fc1, cor_double(pedras[0]))
            self.pedra_double(self.ids.c2, self.ids.cc2, self.ids.fc2, cor_double(pedras[1]))
            self.pedra_double(self.ids.c3, self.ids.cc3, self.ids.fc3, cor_double(pedras[2]))
            self.pedra_double(self.ids.c4, self.ids.cc4, self.ids.fc4, cor_double(pedras[3]))
            self.pedra_double(self.ids.c5, self.ids.cc5, self.ids.fc5, cor_double(pedras[4]))
            self.pedra_double(self.ids.c6, self.ids.cc6, self.ids.fc6, cor_double(pedras[5]))
            self.pedra_double(self.ids.c7, self.ids.cc7, self.ids.fc7, cor_double(pedras[6]))
            self.pedra_double(self.ids.c8, self.ids.cc8, self.ids.fc8, cor_double(pedras[7]))
            self.pedra_double(self.ids.c9, self.ids.cc9, self.ids.fc9, cor_double(pedras[8]))
            self.pedra_double(self.ids.c10, self.ids.cc10, self.ids.fc10, cor_double(pedras[9]))
            self.pedra_double(self.ids.c11, self.ids.cc11, self.ids.fc11, cor_double(pedras[10]))
            self.pedra_double(self.ids.c12, self.ids.cc12, self.ids.fc12, cor_double(pedras[11]))
            self.pedra_double(self.ids.c13, self.ids.cc13, self.ids.fc13, cor_double(pedras[12]))
            self.pedra_double(self.ids.c14, self.ids.cc14, self.ids.fc14, cor_double(pedras[13]))
            self.pedra_double(self.ids.c15, self.ids.cc15, self.ids.fc15, cor_double(pedras[14]))
            time.sleep(3)
            wait_double()
            d = Thread(target=self.bloq_jogar_double, daemon=True)
            d.start()
            if self.teveaposta:
                c = Thread(target=self.conferir_win_double, daemon=True)
                c.start()
            if self.parar_double:
                break

    def valor_maximo_bet_crash(self):
        self.banca_crash = float(self.ids.banca_crash.text)
        try:
            self.quantia = float(self.ids.quantia_crash.text.replace(",", "."))
        except:
            self.quantia = 1
        if self.quantia > self.banca_crash:
            self.ids.quantia_crash.txt = str(self.banca_crash)
            return float(self.banca_crash)
        return self.quantia

    def diminuir_bet_crash(self):
        self.valor_maximo_bet_crash()
        try:
            self.quantia = float(self.ids.quantia_crash.text.replace(",", "."))
        except:
            self.quantia = 1
        self.quantia /= 2
        if self.quantia <= 1:
            self.quantia = 1.0
        self.ids.quantia_crash.text = str(round(self.quantia, 2))

    def dobrar_bet_crash(self):
        self.valor_maximo_bet_crash()
        try:
            self.quantia = float(self.ids.quantia_crash.text.replace(",", "."))
        except:
            self.quantia = 1
        self.quantia *= 2
        if self.quantia <= 1:
            self.quantia = 1.0
        self.ids.quantia_crash.text = str(round(self.quantia, 2))

    def bet_crash(self):
        self.quantia = 0
        self.retirar = 0
        if self.pode_jogar_crash:
            try:
                self.retirar = round(float(self.ids.txt_retirar.text.replace(",", ".")), 2)
            except:
                self.retirar = 1.01
            if self.retirar <= 1:
                self.retirar = 1.01
            try:
                self.quantia = float(self.ids.quantia_crash.text.replace(",", "."))
            except:
                self.quantia = 1
            self.ids.txt_retirar.text = str(self.retirar)
            self.banca_crash = float(self.ids.banca_crash.text)
            self.quantia = self.valor_maximo_bet_crash()
            self.ids.quantia_crash.text = str(float(self.quantia))
            nova_banca = round(self.banca_crash - self.quantia, 2)
            # coverte o valor da banca para .00 no caso de estar apenas .0
            zero = round(nova_banca - int(nova_banca))
            if len(str(zero)) <= 3:
                nova_banca = f"{round(nova_banca, 2)}0"
            self.ids.banca_crash.text = str(nova_banca)
            self.pode_jogar_crash = False
            self.ids.bt_comecar_crash.md_bg_color = (150 / 255, 20 / 255, 50 / 255)
            d = Thread(target=self.conferir_win_crash, daemon=True)
            d.start()

    def conferir_win_crash(self):
        wait_crash()
        if float(self.retirar) < float(get_velas()[0]):
            nova_banca = round(float(self.ids.banca_crash.text) + (self.quantia * self.retirar), 2)
            if nova_banca > 99_999:
                nova_banca = 99_999.9
            # coverte o valor da banca para .00 no caso de estar apenas .0
            zero = round(nova_banca - int(nova_banca))
            if len(str(zero)) <= 3:
                nova_banca = f"{round(float(nova_banca), 2)}0"
            self.ids.banca_crash.text = str(nova_banca)

    def diminuir_bet_double(self):
        try:
            self.quantia_double = float(self.ids.txt_quantia_double.text.replace(",", "."))
        except:
            self.quantia_double = 1
        self.quantia_double /= 2
        if self.quantia_double <= 1:
            self.quantia_double = 1.0
        self.ids.txt_quantia_double.text = str(round(self.quantia_double, 2))

    def dobrar_bet_double(self):
        try:
            self.quantia_double = float(self.ids.txt_quantia_double.text.replace(",", "."))
        except:
            self.quantia_double = 1
        self.quantia_double *= 2
        if self.quantia_double <= 1:
            self.quantia_double = 1.0
        self.ids.txt_quantia_double.text = str(round(self.quantia_double, 2))

    def select_cor_double(self, cor):
        self.cor = cor
        if cor == "preto":
            self.ids.bt_preto.md_bg_color = (12/255, 14/255, 45/255)
            self.ids.bt_vermelho.md_bg_color = (241/255, 44/255, 76/255)
            self.ids.bt_branco.md_bg_color = (255/255, 255/255, 255/255)
        elif cor == "vermelho":
            self.ids.bt_vermelho.md_bg_color = (170/255, 9/255, 36/255)
            self.ids.bt_preto.md_bg_color = (52/255, 59/255, 74/255)
            self.ids.bt_branco.md_bg_color = (255 / 255, 255 / 255, 255 / 255)
        else:
            self.ids.bt_branco.md_bg_color = (150/255, 150/255, 150/255)
            self.ids.bt_preto.md_bg_color = (52/255, 59/255, 74/255)
            self.ids.bt_vermelho.md_bg_color = (241/255, 44/255, 76/255)
        return self.cor

    def bet_double(self):
        if self.pode_jogar_double:
            if self.cor != "":
                if float(self.ids.banca_double.text) >= 1:
                    if self.ids.txt_quantia_double.text != "":
                        try:
                            self.valor_bet = float(self.ids.txt_quantia_double.text.replace(",", "."))
                        except:
                            self.ids.txt_quantia_double.text = "1.0"
                            self.valor_bet = 1
                        self.banca_double = float(self.ids.banca_double.text)
                        if self.valor_bet > self.banca_double:
                            self.valor_bet = self.banca_double
                            self.ids.txt_quantia_double.text = str(round(self.banca_double, 2))
                        if self.valor_bet <= 1:
                            self.valor_bet = 1.0
                            self.ids.txt_quantia_double.text = str(round(self.valor_bet, 2))

                        self.bets_double.append({"cor": self.cor, "bet": self.valor_bet})
                        nova_banca = round(float(self.ids.banca_double.text) - self.valor_bet, 2)
                        zero = round(nova_banca - int(nova_banca))
                        if len(str(zero)) <= 3:
                            nova_banca = f"{round(float(nova_banca), 2)}0"
                        self.ids.banca_double.text = str(nova_banca)
                        self.teveaposta = True

    def conferir_win_double(self):
        self.teveaposta = False
        num_saiu = int(get_num()[0])
        if num_saiu > 7:
            cor = "preto"
        elif num_saiu > 0:
            cor = "vermelho"
        else:
            cor = "branco"
        for bet in self.bets_double:
            if bet["cor"] == cor:
                if cor == "branco":
                    nova_banca = round(float(self.ids.banca_double.text) + (bet["bet"] * 14), 2)
                    if nova_banca > 99_999:
                        nova_banca = 99_999.9
                    zero = round(nova_banca - int(nova_banca))
                    if len(str(zero)) <= 3:
                        nova_banca = f"{round(float(nova_banca), 2)}0"
                    self.ids.banca_double.text = str(nova_banca)
                else:
                    nova_banca = round(float(self.ids.banca_double.text) + (bet["bet"] * 2), 2)
                    zero = nova_banca - int(nova_banca)
                    if len(str(zero)) <= 3:
                        nova_banca = f"{round(float(nova_banca), 2)}0"
                    self.ids.banca_double.text = str(nova_banca)
        self.bets_double = []

class Screen_Manager(ScreenManager):
    pass

class Aplicativo_(MDApp):
    def build(self):
        Window.size = (440, 680)
        self.title = 'Blaze Demo'
        return Builder.load_file("main.kv")

    def Sair(self):
        self.stop()

if __name__ == "__main__":
    Aplicativo_().run()
