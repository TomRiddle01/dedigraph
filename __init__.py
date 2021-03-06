from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command

from .view import GraphView


class DediGraphApp(AppConfig):
    game_dependencies = ['trackmania', 'shootmania']
    mode_dependencies = ['TimeAttack']
    app_dependencies = ['core.maniaplanet']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = None
        self.local_records = None
        self.dedimania = None

    async def on_init(self):
        await super().on_init()

    async def on_stop(self):
        await super().on_stop()

    async def on_destroy(self):
        await super().on_destroy()

    async def on_start(self):
        await super().on_start()

        self.context.signals.listen(mp_signals.ui.manialink_answer, self.compare_click)
        self.context.signals.listen(mp_signals.map.map_start, self.map_start)
        self.context.signals.listen(tm_signals.start_countdown, self.display_graph)

        await self.instance.command_manager.register(
            Command(command='compare',
                    target=self.compare_chat).add_param('playerlogin', nargs='1', type=str, required=True,
                                                        help='Playerlogin to compare to. (Will be plotted in blue.)'),
        )

        self.widget = GraphView(self)
        self.local_records = self.instance.apps.apps["local_records"]

        if "dedimania" not in self.instance.apps.apps:

            class StubDedi():
                def __init__(self):
                    self.current_records = []

            class StubRecord():
                def __init__(self, cps, player):
                    self.cps = cps
                    self.login = player

            self.dedimania = StubDedi()
            # self.dedimania.current_records.append(StubRecord("1000,2300,2800,3000", "tomriddle"))
            # self.dedimania.current_records.append(StubRecord("1300,2400,2800,3500", "steven"))
            # self.dedimania.current_records.append(StubRecord("1100,2300,2400,3700", "peavis"))
        else:
            self.dedimania = self.instance.apps.apps["dedimania"]

        await self.reset_widget()

    async def compare_click(self, player, action, **kwargs):
        if action.startswith("records_widget_"):
            target = action.replace("records_widget_", "")
            await self.compare(player, target)

    async def compare_chat(self, player, data, **kwargs):
        await self.compare(player, data.playerlogin)

    async def compare(self, player, target, **kwargs):
        await self.load_selected_player_graph(target, player)
        await self.display_graph(player)

    async def map_start(self, map, **kwargs):
        await self.widget.reset(map.num_checkpoints)
        for player in self.instance.player_manager.online:
            await self.display_graph(player)

    async def reset_widget(self, **kwargs):
        await self.widget.reset(self.instance.map_manager.current_map.num_checkpoints)
        for player in self.instance.player_manager.online:
            await self.display_graph(player)



    async def display_graph(self, player, **kwargs):
        await self.load_dedi_graph(player)
        await self.load_local_graph(player)
        await self.display_own_records_graph(player)
        await self.widget.display(player=player.login)

    async def load_selected_player_graph(self, selected_player, player, **kwagrs):
        cps = None
        nickname = None
        for record in self.dedimania.current_records:
            if record.login == selected_player:
                if type(record.cps) is str:
                    cps = record.cps.split(",")
                elif type(record.cps) is list:
                    cps = record.cps
                nickname = record.nickname
        await self.widget.update_times("other_dedi", player, cps)

        cps = None
        for record in self.local_records.current_records:
            if record.player.login == selected_player:
                if type(record.checkpoints) is str:
                    cps = record.checkpoints.split(",")
                elif type(record.checkpoints) is list:
                    cps = record.checkpoints
                nickname = record.player.nickname
        await self.widget.update_times("other_local", player, cps)

        if nickname:
            await self.widget.update_other_nick(player, nickname)
            await self.instance.chat("You are now comparing to "+nickname+"$z (displayed in blue).", player.login)
        else:
            await self.instance.chat("No records found for " + selected_player, player.login)

    async def display_own_records_graph(self, player, **kwagrs):
        for record in self.dedimania.current_records:
            if record.login == player.login:
                cps = []
                if type(record.cps) is str:
                    cps = record.cps.split(",")
                elif type(record.cps) is list:
                    cps = record.cps

                await self.widget.update_times("own_dedi", player, cps)
        
        for record in self.local_records.current_records:
            if record.player.login == player.login:
                cps = []
                if type(record.checkpoints) is str:
                    cps = record.checkpoints.split(",")
                elif type(record.checkpoints) is list:
                    cps = record.checkpoints
                await self.widget.update_times("own_local", player, cps)


    async def load_local_graph(self, player, **kwagrs):
        num_records = len(self.local_records.current_records)

        if num_records > 0:
            record = self.local_records.current_records[0]
            if type(record.checkpoints) is str:
                cps = record.checkpoints.split(",")
                await self.widget.update_times("local_first", player, cps)
            elif type(record.checkpoints) is list:
                cps = record.checkpoints
                await self.widget.update_times("local_first", player, cps)

    async def load_dedi_graph(self, player, **kwagrs):
        num_records = len(self.dedimania.current_records)

        if num_records > 0:
            record = self.dedimania.current_records[0]
            if type(record.cps) is str:
                cps = record.cps.split(",")
                await self.widget.update_times("dedi_first", player, cps)
            elif type(record.cps) is list:
                cps = record.cps
                await self.widget.update_times("dedi_first", player, cps)

