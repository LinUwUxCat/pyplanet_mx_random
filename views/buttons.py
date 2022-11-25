from pyplanet.views import TemplateView

class MXRButtons(TemplateView):
    """
    2 buttons - 1 to see ranking, 1 to get help on MX_Random
    """
    template_name = "mx_random/buttons.xml"
    def __init__(self, app):
        super().__init__(app.context.ui)

        self.app = app
        self.id = "mx_random_buttons"

        self.subscribe('mx_random_help', self.mx_random_help)
        self.subscribe('mx_random_ranking', self.mx_random_ranking)

    async def mx_random_help(self, player, *args, **kwargs):
        return await self.app.instance.command_manager.execute(player, "/mxrhelp")
    
    async def mx_random_ranking(self, player, *args, **kwargs):
        return await self.app.instance.command_manager.execute(player, "/mxrrank")