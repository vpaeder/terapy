#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013  Vincent Paeder
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

    Harmonic inversion
    Adapted from Harminv: http://ab-initio.mit.edu/wiki/index.php/Harminv

"""

from terapy.filters.base import Filter
import numpy as np 
import numpy.linalg as npl
import wx
from terapy.core import icon_path
from terapy.core.validator import NumberValidator

SORT_FREQUENCY = 0
SORT_DECAY = 1
SORT_ERROR = 2
SORT_AMPLITUDE = 3
SORT_Q = 4

UNITY_THRESH = 1e-4

class Harminv(Filter):
    """
    
        Harmonic inversion
        Adapted from Harminv: http://ab-initio.mit.edu/wiki/index.php/Harminv
    
    """
    __extname__ = "Harmonic inversion"
    dim = 1
    def __init__(self):
        Filter.__init__(self)
        self.is_visible = True
        self.nf = 100
        self.config = ["nf"]

    def apply_filter(self, array):
        if len(array.shape)!=1:
            # can't treat anything else than 1D
            return
        dt = array.coords[0][1]-array.coords[0][0]
        fmax = 1.0/dt/2.0
        p = HarminvFilter(signal = array.data, dt = dt, fmin = 0.0, fmax = fmax, nf = self.nf)
        #p = HarminvFilter(signal = array.data, dt = 0.1, fmin = 0.0, fmax = 2.5, nf = 100)
        res = p.run()
        camps = np.array(res[1])
        amps = abs(camps)
        phases = np.arctan2(camps.imag,camps.real)
        decays = abs(np.array(res[2]))
        rc = np.zeros(array.data.shape)*1j
        coords = array.coords[0] - min(array.coords[0])
        for i in range(len(res[0])):
            rc = rc + amps[i]*np.exp(-2j*np.pi*res[0][i]*coords + 1j*phases[i] - decays[i]*coords) 
        array.data = rc.real
        return True
    
    def set_filter(self, parent = None):
        dlg = HarminvDialog(parent, nf=self.nf)
        if dlg.ShowModal() == wx.ID_OK:
            self.nf = dlg.GetValue()
            dlg.Destroy()
            return True
        else:
            dlg.Destroy()
            return False

    def get_icon(self):
        return wx.Image(icon_path + "filter-denoise.png").ConvertToBitmap()
    
class HarminvFilter():
    def __init__(self, signal = [], dt = 0.1, fmin = 0.0, fmax = 10, nf = 100):
        # adapted from harminv C++ library
        density = 1.0 # must see if it is useful or not to play with this
        self.nb = (fmax-fmin)*dt*density*len(signal)
        self.c = signal
        self.n = len(signal)
        self.nfreqs = -1 # number of computed modes (none at that stage)
        self.nf = nf # number of spectral basis functions
        self.fmin = fmin*dt
        self.fmax = fmax*dt
        self.K = self.n/2 - 1
        self.dt = dt
        freqs = np.linspace(fmin*dt,fmax*dt,self.nf)
        self.z = np.exp(-1j*2*np.pi*freqs)
        self.J = self.nf
        self.U0 = None
        self.U1 = None
        self.G0 = None
        self.G0_M = None
        self.D0 = None
        self.B = None
        self.u = None
        self.ok_d = mode_ok_data()
        self.init_z()

    def init_z(self):
        self.U0 = np.zeros((self.J,self.J))*1j
        self.U1 = np.zeros((self.J,self.J))*1j
        self.G0 = None
        self.G0_M = None
        self.D0 = None
        self.generate_U(self.U0, self.U1, 0, self.z, self.z, store_G=True)
    
    def generate_U(self, U, U1, p, z, z2, store_G=False):
        small = 1e-12
        J = U.shape[0]
        J2 = U.shape[1]
        K = self.K
        M = K - 1
        c = self.c
        i=0
        j=0
        m=0
        #if n>=2*K+p: return # too few coefficients
        #if J!=J2: return # invalid size
        if self.G0!=None:
            D = self.D0
            G = self.G0
            G_M = self.G0_M
        else:
            D = np.zeros(J)*1j
            G = np.zeros(J)*1j
            G_M = np.zeros(J)*1j
        
        if J==J2:
            z2_neq_z = (z2!=z).all()
        else:
            z2_neq_z = True
        
        z_inv = 1.0/z
        z_m = np.ones(J)+np.zeros(J)*1j
        z_M = z_inv**M
        
        if z2_neq_z:
            z2_inv = 1.0/z2
            z2_m = np.ones(J2)+np.zeros(J2)*1j
            z2_M = z2_inv**M
            G2 = np.zeros(J2)*1j
            G2_M = np.zeros(J2)*1j
        
        # loop over signal array to build up spectral functions
        for m in range(K):
            c1 = c[m+p]
            c2 = c[m+p+M+1]
            d = m+1
            d2 = M-m
            if self.G0==None:
                x1 = z_m*c1
                x2 = z_m*c2
                G += x1
                G_M += x2
                D += x1 * d + x2 * d2 * z_M * z_inv
                z_m = z_inv**(m+1)
            if z2_neq_z:
                G2 += z2_m*c1
                G2_M += z2_m*c2
                z2_m = z2_inv**(m+1)
            
        if z2_neq_z:
            for i in range(J):
                for j in range(J2):
                    if np.abs(z[i]-z2[j])<small:
                        U[i, j] = D[i]
                    else:
                        U[i, j] = (z[i] * G2[j] - z2[j] * G[i] + z2_M[j] * G_M[i] - z_M[i] * G2_M[j]) / (z[i] - z2[j])
                
            if U1!=None:
                for i in range(J):
                    for j in range(J2):
                        if np.abs(z[i]-z2[j])<small:
                            U1[i, j] = z[i] * (D[i] - G[i]) + z_M[i] * G_M[i]
                        else:
                            U1[i, j] = (z[i] * z2[j] * (G2[j] - G[i]) + z2_M[j] * z[i] * G_M[i] - z_M[i] * z2[j] * G2_M[j]) / (z[i] - z2[j])
        else: # z == z2
            for i in range(J):
                U[i, i] = D[i]
                for j in range(i+1,J):
                    U[i, j] = (z[i] * G[j] - z[j] * G[i] + z_M[j] * G_M[i] - z_M[i] * G_M[j]) / (z[i] - z[j])
        
            if U1!=None:
                for i in range(J):
                    U1[i, i] = z[i] * (D[i] - G[i]) + z_M[i] * G_M[i]
                    for j in range(i+1,J):
                        U1[i, j] = (z[i] * z[j] * (G[j] - G[i]) + z_M[j] * z[i] * G_M[i] - z_M[i] * z[j] * G_M[j]) / (z[i] - z[j])
                
                    
        if not(z2_neq_z):
            for i in range(J):
                for j in range(i+1,J):
                    U[j, i] = U[i, j]
            
            if U1!=None:
                for i in range(J):
                    for j in range(i+1,J):
                        U1[j, i] = U1[i, j]
        if store_G and self.G0==None:
            self.D0 = D
            self.G0 = G
            self.G0_M = G_M
    
    def run(self):        
        # solution variables
        ok_d = mode_ok_data(self.fmin,self.fmax)
        self.solve_ok_modes(None, None)
        
        self.mode_ok(-1, ok_d)
        
        isort = self.isort()
        
        freqs = map(lambda j: self.get_freq(j)/self.dt, isort)
        amp = map(lambda j: self.get_amplitude(j), isort)
        decay = map(lambda j: self.get_decay(j) / abs(self.dt), isort)
        Q = map(lambda j: self.get_Q(j), isort)
        err = map(lambda j: self.get_freq_error(j), isort)
        
        self.mode_ok(-2, ok_d)
        
        q = np.argwhere(map(lambda x: x>=self.fmin/self.dt and x<=self.fmax/self.dt, freqs))
        q.reshape((q.shape[0],))
        freqs = map(lambda j: freqs[j], q)
        amp = map(lambda j: amp[j], q)
        decay = map(lambda j: decay[j], q)
        Q = map(lambda j: Q[j], q)
        err = map(lambda j: err[j], q)
        
        return freqs,amp,decay,Q,err

    def solve_eigenvects(self, A0):
        [D,W] = npl.eig(A0)
        W = W.T
        for i in range(W.shape[0]):
            vnorm = 1.0/np.sqrt(np.sum(W[i,:]*W[i,:]))
            W[i,:] = W[i,:]*vnorm
        return D,W
    
    def harminv_solve_once(self):
        singular_threshold = 1e-5
        J = self.J
        
        v0,V0 = self.solve_eigenvects(self.U0)
        
        v = np.abs(v0)
        
        max_v0 = np.max(v)
        self.nfreqs = J
        
        #v0 = map(lambda x: 0 if np.abs(x)<singular_threshold*max_v0 else x, v0)
        #self.nfreqs -= sum(map(lambda x:x==0,v0))
        
        for i in range(J):
            if np.abs(v0[i]) < singular_threshold * max_v0:
                v0[i] = 0
                self.nfreqs -= 1
        for i in range(J-2,-1,-1):
            if v0[i]==0:
                V0[i:i+1,:] = V0[i+1:i+2,:]
                v0[i] = v0[i+1]
                v0[i+1] = 0
            s = 1.0 / np.sqrt(v0[i])
            V0[i,:] = V0[i,:]*s

        V0 = V0[:self.nfreqs,:]
        
        H1 = np.dot(np.dot(V0,self.U1),V0.T)
        
        self.u, V1 = self.solve_eigenvects(H1)
        
        self.B = np.dot(V1,V0)
        pass
    
    def solve_ok_modes(self, ok, ok_d):
        self.harminv_solve_once()
        prev_nf = 0
        nf_ok = 0
        cur_nf = self.nfreqs
        while cur_nf<prev_nf or nf_ok<cur_nf:
            prev_nf = cur_nf
            self.harminv_solve_again(ok, ok_d)
            cur_nf = self.nfreqs
            if ok:
                ok(-1, ok_d)
                for nf_ok in range(cur_nf):
                    if not(ok(nf_ok,ok_d)): break
                ok(-2, ok_d)
            else:
                nf_ok = cur_nf

    def harminv_solve_again(self, ok, ok_d):
        mode_ok = []
        if self.nfreqs==0: return # no eigensolutions to work with
        if ok:
            ok(-1, ok_d) # initialize
            for i in range(self.nfreqs):
                mode_ok.append(ok(i, ok_d))
                
        # Spectral grid needs to be on the unit circle or system is unstable
        j = 0
        for i in range(self.nfreqs):
            if not(ok) or mode_ok[i]:
                self.u[j] = self.u[i]/abs(self.u[i])
                j+=1
        self.nfreqs = j
        
        if ok:
            ok(-2, ok_d) # finish
        
        self.u = self.u[:self.nfreqs]
        if self.nfreqs==0: return # no eigensolutions to work with
        
        self.z = self.u
        self.J = self.nfreqs
        self.init_z()
        self.nfreqs = 0
        self.harminv_solve_once()

    def get_freq(self, k):
        if k>=0 and k<self.nfreqs:
            return -np.arctan2(self.u[k].imag,self.u[k].real)/(2*np.pi)
    
    def get_decay(self, k):
        if k>=0 and k<self.nfreqs:
            return -np.log(abs(self.u[k]))
    
    def get_Q(self, k):
        if k>=0 and k<self.nfreqs:
            return 2*np.pi*abs(self.get_freq(k))/(2*self.get_decay(k))

    def get_omega(self, k):
        if k>=0 and k<self.nfreqs:
            return 1j*np.log(self.u[k])
    
    def get_amplitude(self, k):
        if not(hasattr(self, 'amps')):
            self.amps = self.compute_amplitudes()
        return self.amps[k]

    def get_freq_error(self, k):
        if not(hasattr(self, 'freqerrs')):
            self.freqerrs = self.compute_frequency_errors()
        return self.freqerrs[k]
    
    def isort(self,criterion=SORT_FREQUENCY):
        # sort computed eigenvalues by given criterion and return sorted indices
        if criterion==SORT_FREQUENCY:
            v = map(lambda i: self.get_freq(i),range(self.nfreqs))
        if criterion==SORT_DECAY:
            v = map(lambda i: self.get_decay(i),range(self.nfreqs))
        if criterion==SORT_ERROR:
            v = map(lambda i: self.get_freq_error(i),range(self.nfreqs))
        if criterion==SORT_AMPLITUDE:
            v = map(lambda i: self.get_amplitude(i),range(self.nfreqs))
        if criterion==SORT_Q:
            v = map(lambda i: self.get_freq(i)/self.get_decay(i),range(self.nfreqs))
        return np.argsort(v)

    def u_near_unity(self, u, n):
        nlagbsu = n*np.log(abs(u))
        return (np.log(UNITY_THRESH) < nlagbsu and nlagbsu < -np.log(UNITY_THRESH))

    # Return an array (of size self.nfreqs of complex
    # amplitudes of each sinusoid in the solution.
    def compute_amplitudes(self):
        if self.nfreqs==0: return
        u = []
        for k in range(self.nfreqs):
            if self.u_near_unity(self.u[k],self.n):
                u.append(self.u[k])
        
        Uu = np.zeros((self.J,len(u)))*1j
        self.generate_U(Uu, None, 0, self.z, np.array(u), store_G=True)

        # compute the amplitudes via eq. 27 of M&T, except when |u| is
        # too small..in that case, the computation of Uu is unstable,
        # and we use eq. 26 instead (which doesn't use half of the data,
        # but doesn't blow up either):
        
        ku = 0
        a = []
        for k in range(self.nfreqs):
            asum = 0.0 + 0.0j
            if self.u_near_unity(self.u[k], self.n): # eq. 27
                for j in range(self.J):
                    asum += self.B[k, j] * Uu[j, ku]
                asum /= self.K
                ku+=1
            else: # eq. 26
                for j in range(self.J):
                    asum += self.B[k, j] * self.G0[j]
            a.append(asum * asum)
        
        return a

    def compute_frequency_errors(self):
        if self.nfreqs==0: return
        U2 = np.zeros((self.J,self.J))*1j
        self.generate_U(U2, None, 2, self.z, self.z)
        # For each eigenstate, compute an estimate of the error, roughly as suggested in W&N, eq. (2.19).
        freq_err = []
        for i in range(self.nfreqs):
            U2b = np.dot(U2,self.B)
            
            # ideally, B[i] should satisfy U2 B[i] = u^2 U0 B[i].
            # since B U0 B = 1, then we can get a second estimate
            # for u by sqrt(B[i] U2 B[i]), and from this we compute
            # the relative error in the (complex) frequency. 

            freq_err.append(abs(np.log(np.sqrt(np.sum(self.B*U2b)) / self.u[i])) / abs(np.log(self.u[i])))
        
        return freq_err
    
    def mode_ok(self, k, ok_d):
        if k==-1: # initialize
            ok_d.num_ok = 0
            if self.nfreqs == 0: return 0
            ok_d.min_err = self.get_freq_error(0)
            ok_d.max_amp = abs(self.get_amplitude(0))
            for i in range(1,self.nfreqs):
                ok_d.min_err = min([ok_d.min_err, self.get_freq_error(i)])
                ok_d.max_amp = max([ok_d.max_amp, abs(self.get_amplitude(i))])
        elif k==-2: # finish
            if ok_d.verbose:
                print "# harminv: %d/%d modes are ok: errs <= %e and %e * %e\n, amps >= %g, %e * %g, |Q| >= %g\n" % (ok_d.num_ok, self.nfreqs, ok_d.err_thresh, ok_d.rel_err_thresh, ok_d.min_err, ok_d.amp_thresh, ok_d.rel_amp_thresh, ok_d.max_amp, ok_d.Q_thresh)
        else:
            f = abs(self.get_freq(k))
            errk = self.get_freq_error(k)
            ampk = abs(self.get_amplitude(k))

            ok = (not(ok_d.only_f_inrange) or (f >= ok_d.fmin and f <= ok_d.fmax)) and (errk <= ok_d.err_thresh) and (errk <= ok_d.min_err * ok_d.rel_err_thresh) and (ampk >= ok_d.amp_thresh) and (ampk >= ok_d.rel_amp_thresh * ok_d.max_amp) and (abs(self.get_Q()) >= ok_d.Q_thresh)

            ok_d.num_ok += ok

            return ok

class mode_ok_data():
    def __init__(self, fmin=0.0, fmax=1.0):
        self.verbose = 0
        self.fmin = fmin
        self.fmax = fmax
        self.only_f_inrange = True
        self.err_thresh = 0.1
        self.rel_err_thresh = np.Inf
        self.amp_thresh = 0
        self.rel_amp_thresh = -1.0
        self.Q_thresh = 10.0
        self.min_err = 0
        self.max_amp = 0
        self.num_ok = 0

class HarminvDialog(wx.Dialog):
    def __init__(self, parent = None, title="Harmonic inversion settings", nf = 100):
        wx.Dialog.__init__(self, parent, title=title)
        self.label_size = wx.StaticText(self, -1, "Number of basis functions")
        self.input_size = wx.TextCtrl(self, -1, str(nf), validator=NumberValidator(floats=False), style=wx.TE_PROCESS_ENTER)
        self.button_OK = wx.Button(self, wx.ID_OK)
        self.button_Cancel = wx.Button(self, wx.ID_CANCEL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.AddStretchSpacer(1)
        hbox.Add(self.button_Cancel, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        hbox.Add(self.button_OK, 0, wx.RIGHT|wx.ALIGN_RIGHT, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label_size, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(self.input_size, 0, wx.ALL|wx.EXPAND, 2)
        sizer.Add(hbox, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizer)
        self.Fit()
    
    def GetValue(self):
        return int(self.input_size.GetValue())
