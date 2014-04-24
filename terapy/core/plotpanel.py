import wxmpl
import wx

class PlotPanel(wxmpl.PlotPanel):
    def __init__(self, parent, id, size=(6.0, 3.70), dpi=96, cursor=True,
     location=True, crosshairs=True, selection=True, zoom=True,
     autoscaleUnzoom=True):
        try:
            wxmpl.PlotPanel.__init__(self, parent, id, size, dpi, cursor, location, crosshairs, selection, zoom, autoscaleUnzoom)
        except:
            topwin = wxmpl.toplevel_parent_of_window(self)
            topwin.Connect(self.GetId()-1, self.GetId(), wx.wxEVT_ACTIVATE, self.OnActivate)
    
            wx.EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
            wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)
