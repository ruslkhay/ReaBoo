from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
                     
from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDListItem
import kivymd.uix.list as kvl
import kivymd.uix.divider as kvdiv
import kivymd.uix.appbar.appbar as kvap
from kivy.uix.screenmanager import FadeTransition, SlideTransition, NoTransition

class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()


class BaseScreen(MDScreen):
    ...

class TopBar(kvap.MDTopAppBar):
    """"""
    ...

class StudyScreen(MDScreen):
    """Main screen, that appears first."""
    ...

class DictionaryScreen(MDScreen):
    """Second screen, manager of flash-cards sets."""
    ...

class CardListItem(MDListItem):
    """Unit of card list."""
    card_id = NumericProperty(defaultvalue=-1)
    word = StringProperty() 
    meaning = StringProperty() 
    example = StringProperty() 
    image = StringProperty(defaultvalue="data/fill_image_placeholder.png") 


    


class CardsListScreen(MDScreen):
    """Manage and look through flash-cards set content."""

    def get_item(self, card_id: int):
        """Return card (widget) from list by it's id."""
        cards = self.ids.container.children
        ids = list(map(lambda x: x.card_id, cards))
        return cards[ids.index(card_id)]

    def remove_item(self, card_id: int):
        """Remove element from card list."""
        self.ids.container.remove_widget(self.get_item(card_id))
        pass

    def add_item(self, card_id:int, word:str, meaning:str, example:str, 
                 image:str, *args):
        self.ids.container.add_widget(
            CardListItem(card_id=card_id, word=word, meaning=meaning, 
                         example=example, image=image,
                         on_release=self.open_item))
    
    def update_item(self, card_id:int, word:str, meaning:str, example:str, 
                 image:str, *args):
        """Update content of existed card in list."""
        card = self.get_item(card_id)
        card.word = word
        card.meaning = meaning 
        card.example = example 
        card.image = image


    def open_item(self, item: CardListItem=None):
        sm = self.parent
        card = sm.get_screen("Card")
        card.ids.button_delete.disabled = False 
        if not item:
            card.ids.button_delete.disabled = True
            item = CardListItem()
        card.card_id = item.card_id
        card.word = item.word 
        card.meaning = item.meaning 
        card.example = item.example 
        card.image = item.image 
        sm.current = "Card"

class CardScreen(MDScreen):
    """Manage content of one flash-card unit."""
    card_id = NumericProperty(defaultvalue=88)
    word = StringProperty() 
    meaning = StringProperty() 
    example = StringProperty() 
    image = StringProperty() 

    def save(self):
        sm = self.parent
        cl: CardsListScreen = sm.get_screen("Cards")
        if self.card_id == -1:  
            cl.add_item(
                card_id=-1, word=self.word, meaning=self.meaning, example=self.example, 
                image=self.image
            )
        else:  #i.e. element was in list
            cl.update_item(card_id = self.card_id, word=self.word, meaning=self.meaning, example=self.example, 
                image=self.image)
        self.close()

    def delete(self):
        self.close()
        cl = self.parent.get_screen("Cards")
        cl.remove_item(self.card_id)
        pass

    def close(self):
        sm = self.parent
        sm.current = "Cards"
        # print(sm.screens)


def load_cards(i):
    from kivymd.uix.card import (MDCardSwipe, MDCardSwipeLayerBox, MDCardSwipeFrontBox)
    from kivymd.uix.list import OneLineListItem
    card_item = MDCardSwipe(
        MDCardSwipeLayerBox(),
        MDCardSwipeFrontBox(
            OneLineListItem(
                id="content",
                text=f"One-line item {i}",
                _no_ripple_effect=True,
            )
        ),
        size_hint_y=None,
        height="48dp",
        ) 

    return card_item


class MainScreen(MDScreen):
    ...

Builder.load_file("screen_dict.kv")


__version__ = "2.0.0"
class ReaBooApp(MDApp):
    def on_switch_tabs(
        self,
        bar: MDNavigationBar,
        item: MDNavigationItem,
        item_icon: str,
        item_text: str,
    ):
        previous = self.root.ids.screen_manager.current  
        # print('prev',previous)
        # print(item_text, '\n')
        sm = self.root.ids.screen_manager
        sm.transition = NoTransition()

        match previous:
            case "Flashcards":
                match item_text:
                    case "Study":
                        sm.transition = SlideTransition(direction="down")
                    case "Cards":
                        sm.transition = FadeTransition()
            # case "Study":
            #     sm.transition = SlideTransition(direction="right")
            # case "Cards":
            #     sm.transition = SlideTransition(direction="left")
        sm.current = item_text        
        sm.transition = NoTransition()


    def start_learning(self):
        sm = self.root.ids.screen_manager
        sm.transition = SlideTransition(direction="up")
        sm.current = 'Flashcards'
        # self.root.remove_widget(self.root.ids.navigation_bar)
        

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        pass
    #     return Builder.load_file(KVfile)

    def on_start(self):
        print(self.root.ids)
        cl: CardsListScreen = self.root.ids.screen_cardlist

        for i in range(4):
            cl.add_item(i, f"Word {i}", f"meaning {i}", '', "data/icon_512.png")


ReaBooApp().run()