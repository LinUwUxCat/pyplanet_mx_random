from pyplanet.views.generics.list import ManualListView

class MXRRanking(ManualListView):
    title="MX Random Ranking"
    icon_style = 'Icons128x128_1'
    icon_substyle = 'Rankings'
    
    def __init__(self, app):
        super().__init__(self)
        self.app = app

    async def get_fields(self):
        fields = [ #maybe change that to formatted name?
            {
                'name':'Login',
                'index':'user_login',
                'sorting':True,
                'searching':True,
                'width': 70,
                'type': 'label',
            },
            {
                'name':'Points',
                'index':'user_points',
                'sorting':True,
                'searching':True,
                'width': 40,
                'type': 'label',
            },
        ]
        return fields

    async def get_data(self):
        items = []
        user_and_points = await self.app.get_all_points()
        for i, j in user_and_points:
            items.append({
                'user_login':i,
                'user_points':j,
            })
        return items
            # Shoutouts to https://github.com/skybaks/pyplanet-cup_manager/blob/master/cup_manager/views/cup_view.py#L152 for the reference on how to use a ManualListView