from kivy.uix.listview import ListView, ListItemButton
from kivy.adapters.listadapter import ListAdapter
from kivy.logger import Logger


class IPList(ListView):
    def __init__(self, **kwargs):
        self.args_converter = lambda row_index, ip: {'text': ip,
                                                 'size_hint_y': None,
                                                 'size_hint_x': 1.0,
                                                 'height': 80}
        self.list_adapter = ListAdapter(data=['123.123.123.123'],
                                        selection_mode='single',
                                        cls=ListItemButton,
                                        args_converter=self.args_converter,
                                        allow_empty_selection=False)
        kwargs['adapter'] = self.list_adapter
        super(ListView, self).__init__(**kwargs)

    def add_ip(self, ip):
        Logger.fatal("Adding IP = " + ip)
        self.list_adapter.data.append(ip)
        self.populate()

    def add_ips(self, ips):
        if isinstance(ips, list):
            self.list_adapter.data.extend(ips)
            self.populate()

    def remove_ip(self, ip):
        if self.list_adapter.data.index(ip) != -1:
            Logger.fatal("Removing IP = " + ip)
            self.list_adapter.data.remove(ip)