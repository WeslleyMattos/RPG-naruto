import data_management
import emojis
import messager
import player


class Shop:
    """Class that represents a ninja shop in the game."""

    def __init__(self, area_number: int, item_list: list):
        self.area_number = area_number
        self.item_list = item_list

    def show_items(self) -> str:
        shop_str = ""
        for item_name in self.item_list:
            i = data_management.search_cache_item_by_name(item_name)
            if i is not None:
                shop_str += f"**{i.name}** ({i.object_type} - {i.individual_value} Ryo)\n"
        return shop_str

    @property
    def area_number(self) -> int:
        return self._area_number

    @area_number.setter
    def area_number(self, value: int) -> None:
        self._area_number = value

    @property
    def item_list(self) -> list:
        return self._item_list

    @item_list.setter
    def item_list(self, value: list) -> None:
        self._item_list = value


def buy_item(player: player.Player, item_name: str) -> bool:
    item = data_management.search_cache_item_by_name(item_name)
    if item is None:
        messager.add_message(player.name, f"Item {item_name} não encontrado.")
        return False
    if item.individual_value > player.ryo:
        messager.add_message(player.name, f"Você não tem Ryo suficiente para comprar {item.name}.")
        return False
    player.ryo -= item.individual_value
    player.inventory.add_item(item.name, 1)
    messager.add_message(
        player.name,
        f"Você comprou {item.name}. Saldo: {player.ryo} {emojis.RYO_EMOJI}.",
    )
    return True
