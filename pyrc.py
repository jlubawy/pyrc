#!/usr/bin/env python

import os
import re
import sys

class Conf:
    SPACE_ENC    = (1 << 0)
    CONST_LENGTH = (1 << 1)

    def __init__(self, fname):
        self.filename = os.path.normpath(fname)

        self.name = ""
        self.bits = 0
        self.flags = 0
        self.eps = 0
        self.aeps = 0
        self.header = [0, 0]
        self.one = [0, 0]
        self.zero = [0, 0]
        self.ptrail = 0
        self.repeat = [0, 0]
        self.pre_data_bits = 0
        self.pre_data = 0
        self.gap = 0
        self.toggle_bit = 0
        self.codes = {}

        self.__parse(self.filename)

    def __getitem__(self, prop):
        return getattr(self, prop)

    def __setitem__(self, prop, value):
        setattr(self, prop, value)

    def __parse(self, fname):
        with open(fname, 'rb') as f:
            tokens = self.__remove_comments(f)

            try:
                self.__parse_tokens(tokens)
            except (TypeError, ValueError):
                print "%s - %s" % (fname, sys.exc_info()[1])
            except StopIteration:
                print "%s - %s" % (fname, "StopIteration")

    def __remove_comments(self, file):
        tokens = []

        for line in file:
            ts = line.split()
            for t in ts:
                if t[0] == '#':
                    break
                else:
                    tokens.append(t)
            else:
                continue

        return tokens

    def __parse_tokens(self, tokenlist):
        tokens = iter(tokenlist)

        for tok in tokens:
            if tok == 'name':
                self.name = next(tokens)
            elif tok == 'bits':
                self.bits = int(next(tokens), 0)
            elif tok == 'flags':
                self.__parse_flags(next(tokens))
            elif tok == 'eps':
                self.eps = int(next(tokens), 0)
            elif tok == 'aeps':
                self.aeps = int(next(tokens), 0)
            elif tok == 'header':
                self.header[0] = int(next(tokens), 0)
                self.header[1] = int(next(tokens), 0)
            elif tok == 'one':
                self.one[0] = int(next(tokens), 0)
                self.one[1] = int(next(tokens), 0)
            elif tok == 'zero':
                self.zero[0] = int(next(tokens), 0)
                self.zero[1] = int(next(tokens), 0)
            elif tok == 'ptrail':
                self.ptrail = int(next(tokens), 0)
            elif tok == 'repeat':
                self.repeat = int(next(tokens), 0)
            elif tok == 'pre_data_bits':
                self.pre_data_bits = int(next(tokens), 0)
            elif tok == 'pre_data':
                self.pre_data = int(next(tokens), 0)
            elif tok == 'gap':
                self.gap = int(next(tokens), 0)
            elif tok == 'toggle_bit':
                self.toggle_bit = int(next(tokens), 0)
            elif tok == 'begin' and next(tokens) == 'codes':
                for key in tokens:
                    longcode = next(tokens)

                    if key == 'end' and longcode == 'codes':
                        break

                    pkey = key.lstrip('KEY_')
                    pkey = re.split('_|-| ', pkey)
                    pkey = ' '.join(pkey).title()

                    self.codes[pkey] = self.__parse_longcode(longcode)

    def __parse_flags(self, flagstr):
        flags = flagstr.split('|')
        for f in flags:
            if   f == 'SPACE_ENC':    self.flags |= self.SPACE_ENC
            elif f == 'CONST_LENGTH': self.flags |= self.CONST_LENGTH

    def __parse_longcode(self, longcode):
        if len(longcode) > 1 and longcode[0] == '0' and longcode[1] == 'x':
            s = longcode.lstrip('0x')
            s = s.lstrip('0')
            return int(s, 16)
        else:
            return int(longcode, 10)

def confwalk(root):
    for root, dirs, files in os.walk(root):
        for f in files:
            _, ext = os.path.splitext(f)
            if ext == '.conf':
                yield os.path.join(root, f)

        for d in dirs:
            for f in confwalk(d):
                yield os.path.join(root, d, f)

def main():
    args = sys.argv

    if len(args) < 2:
        print "usage: %s [conf directories]\n" % args[0]
        sys.exit(1)

    for dirname in args[1:]:
        for f in confwalk(dirname):
            c = Conf(f)

            if c.name and c.bits == 16 and len(c.codes) > 0:
                print "%s %s" % (c.filename, c.codes)


if __name__ == "__main__":
    main()
