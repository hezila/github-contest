#!/usr/bin/env python

import sys

def msg(info):
    """Debug output
    """
    print >> sys.stderr, ">>", str(info)
