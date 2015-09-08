from beaconing import BeaconingModule
from blacklisted import BlacklistedModule
from scan import ScanModule
from duration import DurationModule
from long_urls import LongUrlsModule

def Register():
    res = []
    
    beac = BeaconingModule()
    res.append(beac)

    blist = BlacklistedModule()
    res.append(blist)

    scan = ScanModule()
    res.append(scan)

    dur = DurationModule()
    res.append(dur)

    lu = LongUrlsModule()
    res.append(lu)

    return res
