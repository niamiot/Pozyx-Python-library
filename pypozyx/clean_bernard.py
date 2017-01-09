import numpy as np
import scipy.io as io
from scipy.optimize import fmin, minimize
import matplotlib.pyplot as plt

# path = './MOB_CIR'
# filename = '/MobMeasData_28GHz_10KHz_801_1.mat'
# calibration = './B2B_MobMeas/B2B.mat'
# C = io.loadmat(calibration)
# H = io.loadmat(path + filename)
# S21 = H['S21mag'] * np.exp(1j * H['S21ang'] * 2 * np.pi / 180)
# cal = C['cal_trf']
# S21c = S21 / cal
ht = np.load('cira_pozyx.npy')


# ht = S21c[:, 400]
BW = 0.5
N = 993
fGHz = np.linspace(0, BW, N)
tauns = np.linspace(0, N / BW, N)


def energy(x, htl, fGHz):
    xr = x.reshape(3,len(x)/3)
    taul = xr[0,:]
    alpha_re = xr[1,:]
    alpha_im = xr[2,:]
    alphal = alpha_re + 1j * alpha_im
    # ptau : tau x fGHz
    #varg  = np.mod(2*np.pi*fGHz[None,:]*tauns[:,None],2*np.pi)
    #varg = np.mod(2*np.pi*fGHz*tau,2*np.pi)
    #ptau = np.exp(1j*varg)
    sptaul = sptau(taul,alphal,fGHz)
    u = htl - np.conj(sptaul)
    E = np.real(np.dot(u, np.conj(u)))
    # htl : ,fGHz
    # dp : , tau
    #dp = np.dot(ptau,np.conj(htl))
    #E = -np.real(dp*np.conj(dp))
    return(E)

# def energy1(alphal,taul,htl,fGHz):
#    ptaul = ptau(taul,fGHz)
#    u = htl - np.conj(ptaul)*alphal
#    E = u*np.conj(u)


def sptau(tau,alpha, fGHz):
    varg = np.mod(2 * np.pi * fGHz[None,:] * tau[:,None], 2 * np.pi)
    ptau = alpha[:,None]*np.exp(-1j * varg)
    sptau = np.sum(ptau,axis=0)
    return(sptau)

#varg = 2*np.pi*fGHz[None,:]*tauns[:,None]
#ptau = np.exp(1j*varg)
htls = ht
htl = ht
import pdb
# plt.ion()

Nt = 10
for l in range(Nt):
    cir = np.fft.ifft(htl)
    u = np.where(np.abs(cir) == max(np.abs(cir)))[0][0]
    tau0 = tauns[u]
    alpha0_re = np.real(cir[u])
    alpha0_im = np.imag(cir[u])
    # initial guess is obtained from CIR
    x0l= np.array([tau0, alpha0_re, alpha0_im])
    # try:
    #     x0 = np.hstack((x,x0l))
    # except:
    #     x0 = x0l
    x0=x0l
    #E  = energy(tauns,htl,fGHz)
    x = fmin(energy, x0, (htl, fGHz))
    xr = x.reshape(3,len(x)/3)
    taul = xr[0,:]
    alphal_re = xr[1,:]
    alphal_im = xr[2,:]
    alphal = alphal_re + 1j * alphal_im
    sptaul = sptau(taul,alphal,fGHz)
    #Eptaul = np.dot(ptaul,np.conj(ptaul))
    #alphal = np.dot(htl,np.conj(ptaul))/801
    pulse = np.fft.ifft(np.conj(sptaul))
    # plt.figure()
    # ax.plot(tauns, np.abs(cir))
    # ax.plot(tauns, np.abs(pulse))
    # print x0
    # print x
    try:
        hr = hr + np.conj(sptaul) 
    except:
        hr = np.conj(sptaul)
    htl = htl - np.conj(sptaul)
#    print tau

Xe = np.fft.ifft(hr)
X = np.fft.ifft(ht)
f,ax=plt.subplots(2,1,sharex=True,sharey=True)
ax[0].plot(tauns,abs(X))
ax[1].plot(tauns,abs(Xe))
plt.show()

#h = np.fft.fftshift(np.fft.ifft(S21c,axis=0),axes=0)
# plt.plot(tauns,np.abs(h))
# plt.show()
