#!/usr/bin/env python

import sys

from pprint import pprint
from utils import msg
from database import *
from knn.knn import *
 
def main(argv):
    if 'production' in argv:
        return production(argv)
    else:
        return testing(argv)

def production(argv):
    db = Database('data')
    #db.summary()
    knn = Knn(db)
    for user in db.test_u:
        recos = knn.recomend(user)
        pprint(recos)
    return 0

def testing(argv):
    db = Database('minidata')
    if 'stats' in argv:
        db.summary()

    # make recomendent for special user
    knn = Knn(db)
    for user in db.test_u:
        reco = knn.recommend(user)
        pprint(reco)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
