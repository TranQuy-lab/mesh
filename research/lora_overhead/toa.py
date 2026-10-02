import math
def toa(sf,bw_khz,cr,pl,npreamble=8,crc=1,ih=0,de=None):
    bw=bw_khz*1000.0
    ts=(2**sf)/bw
    if de is None:
        de = 1 if ts>0.016 else 0
    tp=(npreamble+4.25)*ts
    num=8*pl-4*sf+28+16*crc-20*ih
    den=4*(sf-2*de)
    npl=8+max(math.ceil(num/den)*(cr+4),0)
    tpay=npl*ts
    return (tp+tpay)*1000.0, ts*1000.0, npl, de
print("SF BW CR payloadB  ToA_ms  Tsym_ms n_payload DE  pkt/h_at_1%  rawbits eff_bps")
for bw in (125,250,500):
  for sf in range(7,13):
    for pl in (10,20,50,100,255):
        t,ts,npl,de=toa(sf,bw,1,pl)
        if de==1 and bw!=125 and sf<11: pass
        ph=0.01*3600/(t/1000.0)
        rb=sf/(ts/1000.0)*(4/5)
        eff=pl*8/(t/1000.0)
        print(f"{sf:2d} {bw:4d} 4/5 {pl:5d} {t:9.2f} {ts:8.3f} {npl:4d} {de} {ph:10.1f} {pl*8:6d} {eff:8.1f}")
