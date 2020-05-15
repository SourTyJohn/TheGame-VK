class gEvent:
    def do_event(self, vk_id, **kwargs):
        pass


class OpenChestEvent(gEvent):
    def do_event(self, vk_id, **kwargs):
        lvl = kwargs['level']
        pass