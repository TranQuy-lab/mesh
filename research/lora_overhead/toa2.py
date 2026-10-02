import math
def toa(sf,bw_khz,crden,pl,npreamble=8,crc=1,ih=0,de=None):
    """crden: coding rate denominator (5,6,7,8) => 4/crden"""
    cr=crden-4
    bw=bw_khz*1000.0; ts=(2**sf)/bw
    if de is None: de = 1 if ts>0.016 else 0
    tp=(npreamble+4.25)*ts
    num=8*pl-4*sf+28+16*crc-20*ih; den=4*(sf-2*de)
    npl=8+max(math.ceil(num/den)*(cr+4),0)
    return (tp+npl*ts)*1000.0, ts*1000.0, npl, tp*1000.0, de
presets={'SHORT_TURBO':(7,500,5),'SHORT_SLOW':(8,250,5),'MEDIUM_FAST':(9,250,5),
 'MEDIUM_SLOW':(10,250,5),'LONG_TURBO':(11,500,8),'LONG_FAST(default)':(11,250,5),
 'LONG_MODERATE':(11,125,8),'LONG_SLOW':(12,125,8)}
hdr="preset                 SF  BW   CR   ToA10B  ToA20B  ToA50B ToA100B ToA237B  pkt/h@1%(20B) pkt/min@1%(20B) preamble_ms preamble_share@20B"
print(hdr)
for k,(sf,bw,cr) in presets.items():
    row=[toa(sf,bw,cr,pl) for pl in (10,20,50,100,237)]
    t20=row[1][0]; pre=row[1][3]
    print(f"{k:22s} {sf:2d} {bw:4.0f} 4/{cr} "+" ".join(f"{v[0]:7.1f}" for v in row)+
          f"   {0.01*3600/(t20/1000):8.1f}     {0.01*60/(t20/1000):8.2f}      {pre:7.1f}    {pre/t20*100:5.1f}%")
print()
print("=== LONG_FAST (SF11/BW250/CR4-5) payload sweep, CRC on, preamble 8 ===")
for pl in (5,10,20,30,50,100,150,200,237):
    t,ts,npl,pre,de=toa(11,250,5,pl)
    print(f" {pl:4d} B -> ToA {t:8.1f} ms | pkt/h@1% {0.01*3600/(t/1000):7.1f} | pkt/min@1% {0.01*60/(t/1000):5.2f} | preamble {pre:.0f} ms ({pre/t*100:.0f}%)")
print()
print("=== 1% duty budget: 36 s airtime per hour (ETSI Tobs=1h) ===")
for name,(sf,bw,cr) in presets.items():
    t20=toa(sf,bw,cr,20)[0]/1000.0
    print(f" {name:22s} 20B ToA={t20*1000:7.1f} ms -> max {36/t20:7.1f} packets/hour = {36/t20/60:5.2f} packets/min")
