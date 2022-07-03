import itertools
import random
import time

from kivy.clock import Clock

from watten_py.objects.client import Client
from watten_py.objects.database import WattenDatabase
from watten_py.objects.game.player import Player
from watten_py.objects.game.cards import CardDek, CardBase
from watten_py.objects.network import GamePacket, Packet
from watten_py.tools.database import DatabaseAttribute
from watten_py.tools.game import convert_to_readable


class Game:
    def __init__(self, game_id: int, player: list[list[Player]], team1_points: list[int], team2_points: list[int], played_cards: list[CardBase]):
        self.game_id = game_id
        self.team1_player: list[Player] = player[0]
        self.team2_player: list[Player] = player[1]
        self.team1_points: list[int] = team1_points
        self.team2_points: list[int] = team2_points
        self.played_cards: list[CardBase] = played_cards
        pass

    def to_sendable_game(self, player: Player):
        sendable_player = []
        all_player = [self.team1_player, self.team2_player]
        for team in all_player:
            lst = []
            for pl in team:
                if pl.player_id == player.player_id:
                    lst.append(player)
                else:
                    lst.append(player.to_not_viewable())
            sendable_player.append(lst)
        return Game(self.game_id, sendable_player, self.team1_points, self.team2_points, self.played_cards)


class ServerSideGame:
    card_dek: CardDek
    curr_round: list[CardBase] = []
    game_player_loop: list[Client] | None = None
    round_winner: int = None
    highest: CardBase = None

    def __init__(self, game_id: int, player: list[list[Client]], team1_points: DatabaseAttribute, team2_points: DatabaseAttribute):
        self.game_id = game_id
        self.team1_player: list[Client] = player[0]
        self.team2_player: list[Client] = player[1]
        self.team1_points: DatabaseAttribute = team1_points
        self.team2_points: DatabaseAttribute = team2_points
        self.play_card_timeout: int = 10

    @classmethod
    def new_game(cls, game_id: int, player: list[list[Client]], connection):
        return cls(
            game_id,
            player,
            DatabaseAttribute(connection, "GameData", "team1_points", "game_id=%s", game_id),
            DatabaseAttribute(connection, "GameData", "team2_points", "game_id=%s", game_id)
        )

    def to_Game(self):
        player = [[cl.player for cl in self.team1_player], [cl.player for cl in self.team2_player]]
        return Game(self.game_id, player, self.team1_points.get(), self.team2_points.get(), self.curr_round)

    def start(self):
        # self.send_to_game(GamePacket("GAMESTART", game=self.to_Game(), highest=self.highest))
        for _ in range(5):
            self.card_dek = CardDek.get_mixed_dek()
            self.update_game_player_loop()
            for card_amount in [3, 2]:
                for client in self.game_player_loop:
                    cards = self.card_dek.deal_top_card(card_amount)
                    client.player.cards = client.player.cards + cards
                    cards = None
            self.highest = CardBase.new_card(self.game_player_loop[0].player.cards[0].num(), self.game_player_loop[3].player.cards[0].col())
            try:
                print(self.highest)
            except IndexError: #########################################################################################################sadfasdf
                pass
            self.send_to_game(GamePacket("ROUNDSTART", self.game_id, game=self.to_Game(), highest=self.highest))
            self.start_round()

    def start_round(self):
        for _ in range(5):
            for cl in self.game_player_loop:
                possible = self.get_possible_cards(cl)
                print(possible)
                self.send_to(cl, GamePacket("TURN", self.game_id, game=self.to_Game(), possible=possible))
                if self.play_card_timeout is None:
                    while len(self.curr_round) != self.game_player_loop.index(cl) + 1:
                        time.sleep(1)
                else:
                    for del_counter in range(self.play_card_timeout):
                        if len(self.curr_round) != self.game_player_loop.index(cl) + 1:
                            time.sleep(1)
                if len(self.curr_round) != self.game_player_loop.index(cl) + 1:
                    try:
                        self.curr_round.append(random.choice(possible))
                    except TypeError:
                        return
                    cl.player.cards.pop(cl.player.cards.index(self.curr_round[-1]))
                else:
                    cl.player.cards.pop(cl.player.cards.index(self.curr_round[-1]))
                self.send_to_game(GamePacket("UPD_G", self.game_id, game=self.to_Game()))
        self.decide_round_winner()

    def decide_round_winner(self):
        self.round_winner = 0
        for card in self.curr_round[1:]:
            # Card is the highest card
            if card == self.highest and card.num() == self.highest.num():
                self.round_winner = self.curr_round.index(card)
                return
            # Card is the highest number and before round_winner is not the highest number
            if card.num() == self.highest.num() and self.curr_round[self.round_winner].num() != self.highest.num():
                self.round_winner = self.curr_round.index(card)
            # Card is not the highest number
            else:
                # Card is the same color as the first card and the first card was the highest color
                if card == self.curr_round[0] and card == self.highest:
                    if card > self.curr_round[self.round_winner]:
                        self.round_winner = self.curr_round.index(card)
                # card color is matching with the color of the first played card
                elif card == self.curr_round[0]:
                    if card > self.curr_round[self.round_winner]:
                        self.round_winner = self.curr_round.index(card)
                # Card Color is the highest color
                elif card == self.highest:
                    self.round_winner = self.curr_round.index(card)
                # Card is a random card
                else:
                    pass

    def get_possible_cards(self, cl: Client):
        cards = cl.player.cards
        if cl in [self.game_player_loop[0], self.game_player_loop[3]]:
            if not self.curr_round:
                return cards
            if self.highest == self.curr_round[0]:
                poss_cards = []
                for card in cards:
                    if card == self.highest:
                        poss_cards.append(card)
                return poss_cards if poss_cards else cards
        else:
            return cards

    def wait_for_card_played(self, cl: Client, exec_after):
        while len(self.curr_round) < self.game_player_loop.index(cl) + 1:
            pass
        return True

    def recv_card(self, card: CardBase):
        print(card)

    def schenere(self):
        self.game_player_loop[0].player.cards = []
        self.game_player_loop[3].player.cards = []
        for card_amount in [3, 2]:
            for client in [self.game_player_loop[0], self.game_player_loop[3]]:
                cards = self.card_dek.deal_top_card(card_amount)
                client.player.cards = client.player.cards + cards
                cards = None

    def update_game_player_loop(self):
        if not self.game_player_loop:
            self.game_player_loop = [self.team1_player[0], self.team2_player[0], self.team1_player[1], self.team2_player[1]]
        else:
            if self.round_winner:
                self.game_player_loop = self.game_player_loop[:self.round_winner] + self.game_player_loop[self.round_winner:]

    def send_to_game(self, packet: Packet | GamePacket):
        for cl in self.team1_player + self.team2_player:
            self.send_to(cl, packet)

    @staticmethod
    def send_to(client: Client, packet: Packet | GamePacket):
        if "game" in packet.data.keys():
            sendable = packet.data["game"].to_sendable_game(client.player)
            packet.data["game"]: Game = sendable
            kwargs = packet.data
            del kwargs["game"]
            client.send(GamePacket(packet.task_type, packet.game_id, game=sendable, **kwargs))
        else:
            client.send(packet)


class ServerSideSet:
    continue_set: bool = True

    def __init__(self, set_id: int, player: list[list[Client]], first_game: ServerSideGame, team1_set_points: DatabaseAttribute, team2_set_points: DatabaseAttribute):
        self.set_id = set_id
        self.team1_set_points: DatabaseAttribute = team1_set_points
        self.team2_set_points: DatabaseAttribute = team2_set_points
        self.team1: list[Client] = player[0]
        self.team2: list[Client] = player[1]
        self.games = [first_game]

    def __repr__(self):
        return f"<ServerSideSet #{self.set_id} games={len(self.games)}>"

    @classmethod
    def new_set(cls, player: list[list[Client]], database: WattenDatabase):
        set_id, game_id = database.new_set([list(map(lambda x: x.user.user_id, team)) for team in player])
        game = ServerSideGame.new_game(game_id, player, database.connection)
        return cls(
            set_id,
            player,
            game,
            DatabaseAttribute(database.connection, "SetData", "team1_set_points", "set_id=%s", set_id),
            DatabaseAttribute(database.connection, "SetData", "team2_set_points", "set_id=%s", set_id)
        )

    def start_set(self, exec_after):
        while self.continue_set:
            self.games[-1].start()
            break

    def send_to_set(self, packet: Packet | GamePacket):
        for cl in self.team1 + self.team2:
            self.send_to(cl, packet)

    @staticmethod
    def send_to(client: Client, packet: Packet | GamePacket):
        client.send(packet)
