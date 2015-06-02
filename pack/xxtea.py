import sys
import os
import traceback
import glob
import string
import struct
import subprocess

_DELTA = 0x9E3779B9

def _long2str(v, w):
    n = (len(v) - 1) << 2
    if w:
        m = v[-1]
        if (m < n - 3) or (m > n): return ''
        n = m
    s = struct.pack('<%iL' % len(v), *v)
    return s[0:n] if w else s

def _str2long(s, w):
    n = len(s)
    m = (4 - (n & 3) & 3) + n
    s = s.ljust(m, "\0")
    v = list(struct.unpack('<%iL' % (m >> 2), s))
    if w: v.append(n)
    return v

def encrypt(str, key):
    if str == '': return str
    v = _str2long(str, True)
    k = _str2long(key.ljust(16, "\0"), False)
    n = len(v) - 1
    z = v[n]
    y = v[0]
    sum = 0
    q = 6 + 52 // (n + 1)
    while q > 0:
        sum = (sum + _DELTA) & 0xffffffff
        e = sum >> 2 & 3
        for p in xrange(n):
            y = v[p + 1]
            v[p] = (v[p] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z))) & 0xffffffff
            z = v[p]
        y = v[0]
        v[n] = (v[n] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[n & 3 ^ e] ^ z))) & 0xffffffff
        z = v[n]
        q -= 1
    return _long2str(v, False)

def _run_cmd(command):
    ret = subprocess.call(command, shell=True)
    if ret != 0:
        message = 'Error running command'
        raise Error(message)

def main():
    workpath = os.path.dirname(os.path.realpath(__file__))
    outpath = os.path.join(workpath, 'xxtea')

    try:
        os.makedirs(outpath)
    except OSError:
        if (os.path.exists(outpath) == False):
            raise Error("Error: cannot create folder" + outpath)

    print('=======================================================')
    print('==> Begin to xxtea!')

    filelist = glob.glob('./*.json')
    for filename in filelist:
        print(os.path.join(outpath, filename))
        newfile = os.path.join(outpath, filename)
        _run_cmd('copy ' + filename + ' ' + newfile)
        bytesFile = open(newfile, "rb+")
        encryBytes = encrypt(bytesFile.read(), 'tinygame')
        encryBytes = 'tinygame' + encryBytes
        bytesFile.seek(0)
        bytesFile.write(encryBytes)
        bytesFile.close()

    print('==> Completed!')

# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
        os.system("pause")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
