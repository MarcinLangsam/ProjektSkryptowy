import player, UI_manager as UI, text_pop as tp, tooltip as tt
from itertools import islice
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.behaviors import DragBehavior
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

global screen
screen = ""

def check_whitch_screen(s):
    global screen
    screen = s

gold_on_screen = Label(pos=(-40,-300), text=("Złoto: "+str(player.gold)), font_size=30, halign="right", valign="middle")
def update_gold():
    gold_on_screen.text = "Złoto: "+str(player.gold)

class ItemSlot(DragBehavior, Widget):
    sprite = StringProperty("")
    
    def __init__(self, **kwargs):
        Window.bind(mouse_pos=self.on_mouse_pos)
        super().__init__(**kwargs)
        self.check_collision = False
        self.check_touch = False
        self.select = 0
        self.drop = 0
        self.temp = ""
        self.t = 0
        self.p = 0

    def switch_items_in_invetory(self):
        self.temp = inventory[self.select].sprite
        inventory[self.select].sprite = inventory[self.drop].sprite
        player.current_player.inventory[self.select][2] = inventory[self.drop].sprite
        inventory[self.drop].sprite = self.temp
        player.current_player.inventory[self.drop][2] = self.temp
        inventory[self.select].pos=(player.current_player.inventory[self.select][0],player.current_player.inventory[self.select][1])

    def on_touch_down(self, touch):
        if self.pos[0] <= touch.pos[0] <= self.pos[0]+75 and self.pos[1] <= touch.pos[1] <= self.pos[1]+75: 
            for x in player.current_player.inventory.keys():
                    if self.pos[0] == player.current_player.inventory[x][0] and self.pos[1] == player.current_player.inventory[x][1]:
                        self.select = x
                        self.check_touch = True
        else:
            pass
        return super(ItemSlot, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
            for x in player.current_player.inventory.keys():
                if player.current_player.inventory[x][0] <= touch.pos[0] <= player.current_player.inventory[x][0]+75 and player.current_player.inventory[x][1] <= touch.pos[1] <= player.current_player.inventory[x][1]+75:
                    self.drop = x
                    self.check_collision = True
                else:
                    pass
            #kontrola będów i oszustwa
            if self.check_collision is False and self.check_touch is True: #powrót slotu w przypadku nie wykrycia "dokowania"
                inventory[self.select].pos=(player.current_player.inventory[self.select][0],player.current_player.inventory[self.select][1])        
            if player.current_player.inventory[self.select][2] == "graphics/items/empty_slot.png": #zapobiega oszustwa z wykożystaniem pustego pola przy wyposażaniu
                inventory[self.select].pos=(player.current_player.inventory[self.select][0],player.current_player.inventory[self.select][1])
            if self.drop in range(39,80) and player.current_player.inventory[self.drop][2] != "graphics/items/empty_slot.png": #zapobiega oszustwa z wykożystaniem pustego pola przy kupowaniu
                inventory[self.select].pos=(player.current_player.inventory[self.select][0],player.current_player.inventory[self.select][1])
            if self.drop in range(39,80) and screen != "shop": #naprawia bug z przenoszeniem do sklepu z poziomu drużyny
                inventory[self.select].pos=(player.current_player.inventory[self.select][0],player.current_player.inventory[self.select][1])
            ##########################

            elif self.check_collision is True and self.check_touch is True:
                if self.select in range (0,40) or self.select in ["main_hand","off_hand","armor","accessory"]:
                    if self.drop in range(39,80) and player.current_player.inventory[self.drop][2] == "graphics/items/empty_slot.png" and screen == "shop": #sprzedawanie przedmiotu
                        player.gold += (items.item_list[player.current_player.inventory[self.select][2]][4]/10)
                        update_gold()
                        tp.text_pop.text = "Sprzedano przedmiot"
                        self.switch_items_in_invetory()
                    
                    elif self.drop in ["main_hand","off_hand","armor","accessory"]: #zakładnie przedmitów
                        if items.item_list[player.current_player.inventory[self.select][2]][0] == player.current_player.inventory[self.drop][3] or player.current_player.inventory[self.drop][3] == "item":
                            items.unequip()
                            self.switch_items_in_invetory()
                            items.equip()
                            self.parent.refresh_items()
                        else:
                            inventory[self.select].pos=(player.current_player.inventory[self.select][0],player.current_player.inventory[self.select][1])
                            tp.text_pop.text = "Nie możesz założyć tutaj tego przedmiotu"
                    elif self.drop in range(0,40):
                        if self.select in ["main_hand","off_hand","armor","accessory"]:
                            items.unequip()
                            self.switch_items_in_invetory()
                            items.equip()
                            self.parent.refresh_items()
                        else:
                            self.switch_items_in_invetory()
                elif self.select in range(39,80):
                    if self.drop in range(0,40):
                        if screen == "shop": #kupowanie przedmitów
                            if player.gold >= items.item_list[player.current_player.inventory[self.select][2]][4] and screen == "shop":
                                player.gold -= items.item_list[player.current_player.inventory[self.select][2]][4]
                                update_gold()
                                self.switch_items_in_invetory()
                                tp.text_pop.text = "Kupiono przedmiot"
                            else:
                                tp.text_pop.text = "Nie masz wsytarczająco złota"
                                inventory[self.select].pos=(player.current_player.inventory[self.select][0],player.current_player.inventory[self.select][1])
                        elif screen != "shop":
                            self.switch_items_in_invetory()
                    elif self.drop in range(39,80): #uniemożliwia przesuwanie przedmitów w sklepie
                        inventory[self.select].pos=(player.current_player.inventory[self.select][0],player.current_player.inventory[self.select][1])
                 
                
                self.check_collision = False
                self.check_touch = False
                self.select = 0
                self.drop = 0
                self.temp = ""
                Clock.schedule_once(tp.clear_pop_up,2)
            return super(ItemSlot, self).on_touch_up(touch)
    
    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        Clock.unschedule(self.display_tooltip)
        self.close_tooltip()
        if self.collide_point(*self.to_widget(*pos)) and self.check_touch == False:
            for x in player.current_player.inventory.keys():
                    if self.pos[0] == player.current_player.inventory[x][0] and self.pos[1] == player.current_player.inventory[x][1]:
                            if player.current_player.inventory[x][2] == "graphics/items/empty_slot.png":
                                self.t = ""
                            else:
                                if x in range(0,40) or x in ["main_hand","off_hand","armor","accessory"]:
                                    self.t = items.item_list[player.current_player.inventory[x][2]][3]+"  \nWartość sprzedarzy: "+ str((items.item_list[player.current_player.inventory[x][2]][4]/10))
                                else:
                                    self.t = items.item_list[player.current_player.inventory[x][2]][3]+"  \nWartość kupna: "+ str(items.item_list[player.current_player.inventory[x][2]][4])
                                self.p = (player.current_player.inventory[x][0]+40,player.current_player.inventory[x][1]+40)
                                Clock.schedule_once(self.display_tooltip, 0.5)

    def close_tooltip(self, *args):
        tt.clear_tooltip()
    def display_tooltip(self, *args):
        tt.set_tooltip(self.t, self.p)

class Items(Widget):
    def __init__(self):
        self.item_list={
            "graphics/items/empty_slot.png" : ["none","","","",0],
            #main_hand
            "graphics/items/zelazny_miecz.png" : ["main_hand","player.current_player.weapon += 10","player.current_player.weapon -= 10","Żelazny Miecz  |   BROŃ\nObrażenia +10",50],
            "graphics/items/miecz_z_brazu.png" : ["main_hand","player.current_player.weapon += 5","player.current_player.weapon -= 5","Miecz z brązu    |   BROŃ\nObrażenia +5",10],
            "graphics/items/miecz_poltorareczny.png" : ["main_hand","player.current_player.weapon += 15","player.current_player.weapon -= 15","Półtorak    |   BROŃ\nObrażenia +15",300],
            "graphics/items/laska_maga.png" : ["main_hand","player.current_player.weapon += 5\nplayer.current_player.INT +=5","player.current_player.weapon -= 5\nplayer.current_player.INT -=5","Laska Maga    |   BROŃ\nObrażenia +5  Iteligencja +5",450],
            "graphics/items/majcher_lotra.png" : ["main_hand","player.current_player.weapon += 8\nplayer.current_player.DEX +=5","player.current_player.weapon -= 8\nplayer.current_player.DEX -=5","Majcher Łotra    |   BROŃ\nObrażenia +8  Zręczność +5",450],
            #off_hand
            "graphics/items/drewniany_puklerz.png" : ["off_hand","player.current_player.defence += 5","player.current_player.defence -= 5","Drewniany Puklerz   |   DRUGA RĘKA\nPancerz +5",300],
            "graphics/items/ksiega_czarow.png" : ["off_hand","player.current_player.INT += 5","player.current_player.INT -= 5","Księga Czarów   |   DRUGA RĘKA\nInteligencja +5",300],
            #armor
            "graphics/items/skorzany_pancerz.png" : ["armor","player.current_player.defence += 5","player.current_player.defence -= 5 ","Skórzany Pancerz   |   PANCERZ\nPancerz +5",1000],
            "graphics/items/szata_maga.png" : ["armor","player.current_player.defence += 5\nplayer.current_player.INT += 5","player.current_player.defence -= 5\nplayer.current_player.INT -= 5","Szata Maga   |   PANCERZ\nPancerz +5  Inteligencja +5",2000],
            "graphics/items/zbroja_plytowa.png" : ["armor","player.current_player.defence += 10\nplayer.current_player.HP += 30\nplayer.current_player.MAX_HP += 30","player.current_player.defence -= 10\nplayer.current_player.HP -= 30\nplayer.current_player.MAX_HP -= 30","Zbroja Płytowa   |   PANCERZ\nPancerz +10  Zdrowie +30",2000],
            "graphics/items/kaftan_zlodzieja.png" : ["armor","player.current_player.defence += 7\nplayer.current_player.weapon += 5","player.current_player.defence -= 7\nplayer.current_player.weapon -= 5","Kaftan Złodzieja   |   PANCERZ\nPancerz +7  Obrażenia +5",2000],
            
            #accessory
            "graphics/items/pierscien_sily.png" : ["accessory","player.current_player.STR += 5","player.current_player.STR -= 5","Pierścień Siły    |   AKCESORIA\nSiła +5",10],
            "graphics/items/pierscien_zrecznosci.png" : ["accessory","player.current_player.DEX += 5","player.current_player.DEX -= 5","Pierścień Zręczności    |   AKCESORIA\nZręczność +5",100],
            "graphics/items/pierscien_inteligencji.png" : ["accessory","player.current_player.INT += 5","player.current_player.INT -= 5","Pierścień Inteligencji   |   AKCESORIA\nInteligencja +5",100],
            "graphics/items/pierscien_zdrowia.png" : ["accessory","player.current_player.HP += 20\nplayer.current_player.MAX_HP += 20","player.current_player.HP -= 20\nplayer.current_player.MAX_HP += 20","Pierścień Zdrowia    |   AKCESORIA\nZdrowie +20",100],
            "graphics/items/pierscien_many.png" : ["accessory","player.current_player.MP += 10\nplayer.current_player.MAX_MP += 10","player.current_player.MP -= 10\nplayer.current_player.MAX_MP += 10","Pierścień Many    |   AKCESORIA\nMana +10",100]

        }

    def equip(self):
        exec(self.item_list[player.current_player.inventory["main_hand"][2]][1])
        exec(self.item_list[player.current_player.inventory["off_hand"][2]][1])
        exec(self.item_list[player.current_player.inventory["armor"][2]][1])
        exec(self.item_list[player.current_player.inventory["accessory"][2]][1])
        UI.ui.stats_refresh(player.current_player)

    def unequip(self):  
        exec(self.item_list[player.current_player.inventory["main_hand"][2]][2])
        exec(self.item_list[player.current_player.inventory["off_hand"][2]][2])
        exec(self.item_list[player.current_player.inventory["armor"][2]][2])
        exec(self.item_list[player.current_player.inventory["accessory"][2]][2])
        UI.ui.stats_refresh(player.current_player)

inventory = {}
items = Items()