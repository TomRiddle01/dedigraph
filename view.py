from pyplanet.views.generics.widget import WidgetView


class GraphView(WidgetView):
    
    # under dedi
    # widget_x = -158
    # widget_y = -65
    
    # over dedi
    # widget_x = -160
    # widget_y = 15

    # head
    widget_x = -124
    widget_y = 65

    template_name = 'dedigraph/graph.xml'

    def __init__(self, app):
        super().__init__(self)
        self.app = app
        self.manager = app.context.ui
        self.id = 'pyplanet__widgets_graph'
        self.player_data = {}
        self.checkpoints = 0

    def create_if_not_exists(self, player):
        if player.login not in self.player_data:
            self.player_data[player.login] = {"cptimes": {}}
        
    async def reset(self, num_checkpoints):
        self.player_data = {}
        self.checkpoints = num_checkpoints

    async def update_other_nick(self, player, nick):
        self.create_if_not_exists(player)
        self.player_data[player.login]["other_nick"] = nick


    async def update_times(self, type, player, times):
        self.create_if_not_exists(player)

        if times is None:
            if type in self.player_data[player.login]["cptimes"]:
                del self.player_data[player.login]["cptimes"][type]

        elif len(times) == self.checkpoints and len(times) > 0:
            print(type, times)
            self.player_data[player.login]["cptimes"][type] = ",".join(map(str, map(float, times)))

    async def get_context_data(self):
        context = await super().get_context_data()

        # Add facts.
        context.update({
            'num_checkpoints': self.app.instance.map_manager.current_map.num_checkpoints,
        })

        return context

    async def get_player_data(self):
        data = await super().get_player_data()
        data.update(self.player_data)
        return data
