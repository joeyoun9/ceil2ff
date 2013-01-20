"""
    Read CT12K obs
"""
from numpy import exp, zeros, float32, array, arange

def read(ob):
    """
        process ct12 data
        -- this instrument formats it's data in feet, so, you must use feet
        -- however, cloud heights may not be in feet
        """
    # check if the text you have been given is a proper ct12 message:

    dls = ob.split("\n")
    dl = []
    if len(dls) < 15 or ":" in ob:
        return False

    # purify the ob so that i dont have to care about formatting
    for l in dls:
        if len(l.strip()) > 3:
            # then i guess there is content
            dl.append(l) #NOT STRIP!!
    del dls

    'cloud line'
    cl = dl[0].strip()
    'info line'
    il = dl[1].strip()
    'that x for x is NECESSARY.'
    data = [cl[0:1], cl[4:9], cl[10:15], cl[16:21], cl[22:27]] + [x for x in cl[28:39]]
    data += [ il[0:1], il[2:3], il[4:8], il[9:12], il[13:16], il[17:20],
             il[21:25], il[26:31], il[32:34], il[35:37], ]

    'Translate these values into a single numpy array'
    def to(x):
        if '/' in x: return 0.
        return float(x)
    status = array(map(to,data),dtype=float32)
    
    values = zeros((250), dtype=float32) # 250 is the only length this msg can be
    # the first values are heights of the beginning of the row...
    string = '\n'.join(dl[2:]).replace(' ', '0').replace("\n", "").replace("\r", "").strip()
    index = 0
    for i in xrange(2, len(string[2:]) + 1, 2):
        if i % 42 == 0: continue # height indices
        val = (int(string[i:i + 2], 16) - 1) / 50. # compute the SS value...
        values[index] = val
        index += 1
    out = {
           'height':arange(250) * 15,
           'bs':exp(values),
           'status':status,
           } # 15 m vertical resolution is the only reportable form!
    
    return out
