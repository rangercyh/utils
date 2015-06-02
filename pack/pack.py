import sys
import os
import traceback
import md5
import subprocess
import string
from contextlib import contextmanager
import struct

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

@contextmanager
def _pushd(newDir):
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)

def _run_cmd(command):
    ret = subprocess.call(command, shell=True)
    if ret != 0:
        message = 'Error running command'
        raise Error(message)

def calc_md5(str):
    m = md5.new()
    m.update(str)
    return m.hexdigest()

def main():
    workpath = os.path.dirname(os.path.realpath(__file__))
    outpath = os.path.join(workpath, 'assets')

    try:
        os.makedirs(outpath)
        filelist = open(os.path.join(workpath, 'filehash'), "w")
    except OSError:
        if (os.path.exists(outpath) == False) or (os.path.exists(outpath + 'filelist') == False):
            raise Error("Error: cannot create folder or filelist in " + outpath)

    print('=======================================================')
    print('==> Prepare to pack files, please have a cup of coffee!')
    print('==> Begin to process lua script!')
    luanum = 0
    for parent, dir, file in os.walk(os.path.join(workpath, 'script')):
        for filename in file:
            if os.path.splitext(filename)[1] == ".lua":
                name = os.path.join(os.path.relpath(parent, workpath), filename)
                with _pushd(parent):
                    print(os.path.join(workpath, "luajit", "luajit.exe") + " -b " + filename + " " + filename + 'c')
                    _run_cmd(os.path.join(workpath, "luajit", "luajit.exe") + " -b " + filename + " " + filename + 'c')
                    os.remove(filename + 'c')

                    newfile = os.path.join(outpath, calc_md5(name.replace('\\', '/')))
                    _run_cmd('copy ' + filename + ' ' + newfile)

                    bytesFile = open(newfile, "rb+")
                    encryBytes = encrypt(bytesFile.read(), 'tinygame')
                    encryBytes = 'tinygame' + encryBytes
                    bytesFile.seek(0)
                    bytesFile.write(encryBytes)
                    bytesFile.close()

                    contentHash = calc_md5(encryBytes)
                    filelist.write(calc_md5(name.replace('\\', '/')) + '\t' + name.replace('\\', '/') + '\t' + contentHash + '\r')

                    luanum += 1
    print('==> Lua script process Completed!', luanum)
    print('==> Begin to process settings!')
    settingsnum = 0
    for parent, dir, file in os.walk(os.path.join(workpath, 'settings')):
        for filename in file:
            name = os.path.join(os.path.relpath(parent, workpath), filename)
            with _pushd(parent):
                newfile = os.path.join(outpath, calc_md5(name.replace('\\', '/')))
                _run_cmd('copy ' + filename + ' ' + newfile)

                bytesFile = open(newfile, "rb+")
                encryBytes = encrypt(bytesFile.read(), 'tinygame')
                encryBytes = 'tinygame' + encryBytes
                bytesFile.seek(0)
                bytesFile.write(encryBytes)
                bytesFile.close()


                contentHash = calc_md5(encryBytes)
                filelist.write(calc_md5(name.replace('\\', '/')) + '\t' + name.replace('\\', '/') + '\t' + contentHash + '\r')

                settingsnum += 1
    print('==> Settings process Completed!', settingsnum)
    print('==> Begin to process res!')
    resnum = 0
    for parent, dir, file in os.walk(os.path.join(workpath, 'res')):
        for filename in file:
            name = os.path.join(os.path.relpath(parent, workpath), filename)
            with _pushd(parent):
                newfile = os.path.join(outpath, calc_md5(name.replace('\\', '/')))
                _run_cmd('copy ' + filename + ' ' + newfile)

                bytesFile = open(newfile, "rb+")
                encryBytes = encrypt(bytesFile.read(), 'tinygame')
                encryBytes = 'tinygame' + encryBytes
                bytesFile.seek(0)
                bytesFile.write(encryBytes)
                bytesFile.close()

                contentHash = calc_md5(encryBytes)
                filelist.write(calc_md5(name.replace('\\', '/')) + '\t' + name.replace('\\', '/') + '\t' + contentHash + '\r')

                resnum += 1
    filelist.close()
    print('==> Res process Completed!', resnum)
    print('=============================Congratulations Completed!')
    print('Total file num = ', luanum + settingsnum + resnum)

    _run_cmd('node version.js')

# def test():
#     print(calc_md5('scriptmain.lua'))

# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
        # test()
        os.system("pause")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
