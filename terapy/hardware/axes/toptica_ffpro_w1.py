import wx
from terapy.core.button import OnOffIndicator
from terapy.core.validator import PositiveFloatValidator
from terapy.core.threads import WidgetUpdateThread
from time import sleep

class FFProOptimizerWidget(wx.ScrolledWindow):
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
        self.timer = FFProOptimizerUpdateThread(self)
        self.title = title
        self.instr = instr
        self.SetScrollbars(1,1,1,1)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.panel0 = wx.Panel(self)
        self.toggle_automatic = OnOffIndicator(self.panel0,label="Automatic optimization")
        self.toggle_block = OnOffIndicator(self.panel0,label="Block optimization")
        self.toggle_busy = OnOffIndicator(self.panel0,label="Optimizer busy")
        
        vbox0 = wx.BoxSizer(wx.VERTICAL)
        vbox0.Add(self.toggle_amp_state,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox0.Add(self.label_reprate,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox0.Add(self.label_level,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox0.Add(self.slider_level,0,wx.LEFT|wx.RIGHT|wx.EXPAND|wx.HORIZONTAL,2)
        
        self.panel0.SetSizerAndFit(vbox0)
        hbox.Add(self.panel0,0,wx.EXPAND|wx.ALL,2)
        hbox.Add(wx.StaticLine(self,-1,style=wx.LI_VERTICAL),0,wx.ALL|wx.EXPAND,2)

        self.panel1 = wx.Panel(self)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_minpower = wx.StaticText(self.panel1,-1,"Activation power")
        self.input_minpower = wx.TextCtrl(self.panel1,-1,"0",validator=PositiveFloatValidator(),style=wx.TE_PROCESS_ENTER)
        hbox0.Add(self.label_minpower,0,wx.EXPAND|wx.ALL,2)
        hbox0.Add(self.input_minpower,0,wx.EXPAND|wx.ALL,2)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_setpoint = wx.StaticText(self.panel1,-1,"Setpoint")
        self.input_setpoint = wx.TextCtrl(self.panel1,-1,"0",validator=PositiveFloatValidator(),style=wx.TE_PROCESS_ENTER)
        hbox1.Add(self.label_setpoint,0,wx.EXPAND|wx.ALL,2)
        hbox1.Add(self.input_setpoint,0,wx.EXPAND|wx.ALL,2)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_threshold = wx.StaticText(self.panel1,-1,"Threshold (%)")
        self.input_threshold = wx.TextCtrl(self.panel1,-1,"0",validator=PositiveFloatValidator(),style=wx.TE_PROCESS_ENTER)
        hbox2.Add(self.label_threshold,0,wx.EXPAND|wx.ALL,2)
        hbox2.Add(self.input_threshold,0,wx.EXPAND|wx.ALL,2)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_tolerance = wx.StaticText(self.panel1,-1,"Fine-tune tolerance (%)")
        self.input_tolerance = wx.TextCtrl(self.panel1,-1,"0",validator=PositiveFloatValidator(),style=wx.TE_PROCESS_ENTER)
        hbox3.Add(self.label_threshold,0,wx.EXPAND|wx.ALL,2)
        hbox3.Add(self.input_threshold,0,wx.EXPAND|wx.ALL,2)
        self.SetAutoLayout(True)
        self.SetSizerAndFit(hbox)

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(hbox0,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox1.Add(hbox1,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox1.Add(hbox2,0,wx.LEFT|wx.HORIZONTAL,2)
        vbox1.Add(hbox3,0,wx.LEFT|wx.HORIZONTAL,2)
        
        self.panel1.SetSizerAndFit(vbox1)
        hbox.Add(self.panel0,1,wx.EXPAND|wx.ALL,2)
        
    def RefreshDisplay(self):
        """
        
            Refresh display.
            
            Parameters:
                val    -    value to display (float)
        
        """
        self.toggle_automatic.Switch(self.instr.optimizer.automatic)
        self.toggle_block.Switch(self.instr.optimizer.blocked)
        self.toggle_busy.Switch(self.instr.optimizer.busy)
        self.input_minpower.SetValue("%0.2f" % self.instr.optimizer.minpower)
        self.input_setpoint.SetValue("%0.2f" % self.instr.optimizer.setpoint)
        self.input_threshold.SetValue("%0.1f" % self.instr.optimizer.threshold*100.0)
        self.input_tolerance.SetValue("%0.1f" % self.instr.optimizer.tolerance*100.0)
        self.Layout()
        
    def Enable(self, state):
        wx.ScrolledWindow.Enable(self, state)
        self.timer.pause(not(state))
    
class FFProOptimizerUpdateThread(WidgetUpdateThread):
    def __init__(self,widget):
        self.must_move = False
        self.must_home = False
        self.must_reset = False
        WidgetUpdateThread.__init__(self,widget)
    
    def update(self):
        try:
            self.widget.instr.update_optimizer_status()
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
