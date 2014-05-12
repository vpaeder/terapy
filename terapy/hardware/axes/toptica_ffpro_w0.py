import wx
from terapy.core.button import OnOffIndicator
from terapy.core.validator import PositiveFloatValidator
from terapy.core.threads import WidgetUpdateThread
from time import sleep

class FFProWidget(wx.ScrolledWindow):
    """
    
        Main widget for Toptica FemtoFiber Pro laser system 
    
    """
    def __init__(self,parent=None, title="", instr = None):
        """
        
            Initialization.
            
            Parameters:
                parent    -    parent window (wx.Window)
                instr    -    instrument to be controlled (TOPTFFPro object)
        
        """
        wx.ScrolledWindow.__init__(self,parent,style=wx.HSCROLL|wx.VSCROLL|wx.TAB_TRAVERSAL)
        self.timer = FFProUpdateThread(self)
        self.title = title
        self.instr = instr
        self.SetScrollbars(1,1,1,1)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.panel_osc = wx.Panel(self)
        self.toggle_amp_state = OnOffIndicator(self.panel_osc,label="Oscillator state")
        self.label_reprate = wx.StaticText(self.panel_osc,-1,"Oscillator rep. rate: 80000000.0 Hz")
        self.label_level = wx.StaticText(self.panel_osc,-1,"Amplifier level")
        self.slider_level = wx.Slider(self.panel_osc,value=0,minValue=0,maxValue=100,style=wx.SL_HORIZONTAL|wx.SL_VALUE_LABEL)
        
        vbox0 = wx.BoxSizer(wx.VERTICAL)
        vbox0.Add(self.toggle_amp_state,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox0.Add(self.label_reprate,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox0.Add(self.label_level,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox0.Add(self.slider_level,0,wx.LEFT|wx.RIGHT|wx.EXPAND|wx.HORIZONTAL,2)
        
        self.panel_osc.SetSizerAndFit(vbox0)
        hbox.Add(self.panel_osc,0,wx.EXPAND|wx.ALL,2)
        
        self.panel_shg = wx.Panel(self)
        self.label_shg = wx.StaticText(self.panel_shg,-1,"SHG power: 0 mW")
        self.toggle_shg_oven = OnOffIndicator(self.panel_shg,label=u"SHG oven temp.: 60.00 \N{DEGREE SIGN}C")
        self.label_shg_setpoint = wx.StaticText(self.panel_shg,-1,"Temperature setpoint")
        self.input_shg_setpoint = wx.TextCtrl(self.panel_shg,-1,"0",validator=PositiveFloatValidator(),style=wx.TE_PROCESS_ENTER)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(self.label_shg_setpoint,0,wx.CENTER|wx.VERTICAL,2)
        hbox1.Add(self.input_shg_setpoint,0,wx.CENTER|wx.VERTICAL,2)
        vbox1.Add(self.label_shg,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox1.Add(self.toggle_shg_oven,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox1.Add(hbox1,0,wx.LEFT|wx.HORIZONTAL,2)
        self.panel_shg.SetSizerAndFit(vbox1)
        self.panel_shg.SetAutoLayout(True)
        self.hline_shg = wx.StaticLine(self,-1,style=wx.LI_VERTICAL)
        hbox.Add(self.hline_shg,0,wx.ALL|wx.EXPAND,2)
        hbox.Add(self.panel_shg,0,wx.EXPAND|wx.ALL,2)

        self.panel_tnir = wx.Panel(self)
        self.label_tnir = wx.StaticText(self.panel_tnir,-1,"TNIR intensity: 0 a.u.")
        self.toggle_tnir_oven = OnOffIndicator(self.panel_tnir,label=u"TNIR oven temp.: 60.00 \N{DEGREE SIGN}C")
        self.label_tnir_setpoint = wx.StaticText(self.panel_tnir,-1,"Temperature setpoint")
        self.input_tnir_setpoint = wx.TextCtrl(self.panel_tnir,-1,"0",validator=PositiveFloatValidator(),style=wx.TE_PROCESS_ENTER)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(self.label_tnir_setpoint,0,wx.CENTER|wx.VERTICAL,2)
        hbox2.Add(self.input_tnir_setpoint,0,wx.CENTER|wx.VERTICAL,2)
        vbox2.Add(self.label_tnir,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox2.Add(self.toggle_tnir_oven,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox2.Add(hbox2,0,wx.LEFT|wx.HORIZONTAL,2)
        self.panel_tnir.SetSizerAndFit(vbox2)
        self.panel_tnir.SetAutoLayout(True)
        self.hline_tnir = wx.StaticLine(self,-1,style=wx.LI_VERTICAL)
        hbox.Add(self.hline_tnir,0,wx.ALL|wx.EXPAND,2)
        hbox.Add(self.panel_tnir,0,wx.EXPAND|wx.ALL,2)
        
        self.panel_tvis = wx.Panel(self)
        self.label_tvis = wx.StaticText(self.panel_tvis,-1,"TVIS intensity: 0 a.u.")
        self.toggle_tvis_oven = OnOffIndicator(self.panel_tvis,label=u"TVIS oven temp.: 60.00 \N{DEGREE SIGN}C")
        self.label_tvis_setpoint = wx.StaticText(self.panel_tvis,-1,"Temperature setpoint")
        self.input_tvis_setpoint = wx.TextCtrl(self.panel_tvis,-1,"0",validator=PositiveFloatValidator(),style=wx.TE_PROCESS_ENTER)
        vbox3 = wx.BoxSizer(wx.VERTICAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(self.label_tvis_setpoint,0,wx.CENTER|wx.VERTICAL,2)
        hbox3.Add(self.input_tvis_setpoint,0,wx.CENTER|wx.VERTICAL,2)
        vbox3.Add(self.label_tvis,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox3.Add(self.toggle_tvis_oven,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox3.Add(hbox3,0,wx.LEFT|wx.HORIZONTAL,2)
        self.panel_tvis.SetSizerAndFit(vbox3)
        self.panel_tvis.SetAutoLayout(True)
        self.hline_tvis = wx.StaticLine(self,-1,style=wx.LI_VERTICAL)
        hbox.Add(self.hline_tvis,0,wx.ALL|wx.EXPAND,2)
        hbox.Add(self.panel_tvis,0,wx.EXPAND|wx.ALL,2)
        
        self.panel_shg.Show(False)
        self.hline_shg.Show(False)
        self.panel_tnir.Show(False)
        self.hline_tnir.Show(False)
        self.panel_tvis.Show(False)
        self.hline_tvis.Show(False)
        
        self.SetAutoLayout(True)
        self.SetSizerAndFit(hbox)
        
    def RefreshDisplay(self):
        """
        
            Refresh display.
            
            Parameters:
                val    -    value to display (float)
        
        """
        if self.instr.mode_lock==0:
            self.toggle_amp_state.Switch(False)
            self.toggle_amp_state.SetLabel("Oscillator off")
        elif self.instr.mode_lock==-1:
            self.toggle_amp_state.Switch(False)
            self.toggle_amp_state.SetLabel("Oscillator on")
        elif self.instr.mode_lock==1:
            self.toggle_amp_state.Switch(True)
            self.toggle_amp_state.SetLabel("Oscillator on")
        
        self.label_reprate.SetLabel("Oscillator rep. rate: %d Hz" % self.instr.rep_rate)
        
        self.slider_level.SetValue(self.instr.amp_level*100)
        
        self.panel_shg.Show(self.instr.shg.installed)
        self.hline_shg.Show(self.instr.shg.installed)
        if self.instr.shg.installed:
            self.label_shg.SetLabel("SHG power: %0.2f mW" % self.instr.shg.power)
            if self.instr.shg.oven_notok==0:
                self.toggle_shg_oven.Switch(True)
            else:
                self.toggle_shg_oven.Switch(False)
            
            self.toggle_shg_oven.SetLabel(u"SHG oven temp.: %0.1f \N{DEGREE SIGN}C" % self.instr.shg.oven_temp)
            if not(self.input_shg_setpoint.HasFocus()):
                self.input_shg_setpoint.SetValue("%0.1f" % self.instr.shg.oven_settemp)
        
        self.panel_tnir.Show(self.instr.tnir.installed)
        self.hline_tnir.Show(self.instr.tnir.installed)
        if self.instr.tnir.installed:
            self.label_tnir.SetLabel("TNIR intensity: %0.2f a.u." % self.instr.tnir.intensity)
            if self.instr.tnir.oven_notok==0:
                self.toggle_tnir_oven.Switch(True)
            else:
                self.toggle_tnir_oven.Switch(False)
            
            self.toggle_tnir_oven.SetLabel(u"TNIR oven temp.: %0.1f \N{DEGREE SIGN}C" % self.instr.tnir.oven_temp)
            if not(self.input_tnir_setpoint.HasFocus()):
                self.input_tnir_setpoint.SetValue("%0.1f" % self.instr.tnir.oven_settemp)
        
        self.panel_tvis.Show(self.instr.tvis.installed)
        self.hline_tvis.Show(self.instr.tvis.installed)
        if self.instr.tvis.installed:
            self.label_tvis.SetLabel("TVIS intensity: %0.2f a.u." % self.instr.tvis.intensity)
            if self.instr.tvis.oven_notok==0:
                self.toggle_tvis_oven.Switch(True)
            else:
                self.toggle_tvis_oven.Switch(False)
            
            self.toggle_tvis_oven.SetLabel(u"TVIS oven temp.: %0.1f \N{DEGREE SIGN}C" % self.instr.tvis.oven_temp)
            if not(self.input_tvis_setpoint.HasFocus()):
                self.input_tvis_setpoint.SetValue("%0.1f" % self.instr.tvis.oven_settemp)
        
        self.Layout()
        
    def Enable(self, state):
        wx.ScrolledWindow.Enable(self, state)
        self.timer.pause(not(state))
    
class FFProUpdateThread(WidgetUpdateThread):
    def __init__(self,widget):
        self.must_move = False
        self.must_home = False
        self.must_reset = False
        WidgetUpdateThread.__init__(self,widget)
    
    def update(self):
        try:
            self.widget.instr.update_laser_status()
            return True
        except:
            return False
    
    def move(self, pos):
        self.pos = pos
        self.must_move = True
    
    def home(self):
        self.must_home = True
    
    def reset(self):
        self.must_reset = True
    
    def run(self):
        while self.can_run:
            if self.must_move:
                self.widget.axis.stop()
                self.widget.axis.goTo(self.pos)
                self.must_move = False
            elif self.must_home:
                self.widget.axis.stop()
                self.widget.axis.home()
                self.must_home = False
            elif self.must_reset:
                self.widget.axis.stop()
                self.widget.axis.reset()
                self.must_reset = False
            else:
                if self.need_display:
                    if self.update() and self.can_run:
                        wx.CallAfter(self.widget.RefreshDisplay)
            
            sleep(self.delay/1000.0)
    
    def pause(self, state):
        WidgetUpdateThread.pause(self,state)
        self.must_move = False
        self.must_home = False
        self.must_reset = False
    
    def stop(self):
        self.can_run = False
