#!/usr/bin/env python

from math import log, sqrt
from collections import defaultdict
from pprint import pprint
from utils import msg

class Knn:
    def __init__(self, data):
        """Constructor
        """
        self.data = data
        self.r_similar = {} # repos similarity list
        self.u_similar = {} # user similarity list
        
    def item_model(self):
        """construct item similarities
        """
        msg("building r_matrix")
        repos=set(self.data.watching_r.keys())
        for repo in repos:
            r_similar[repo] = self.related_items(repo)
        r_similar.sort(reverse=True)

    def user_model(self):
        """construct user similarities
        """
        msg("building u_matrix")
        users = set(self.data.u_watching.keys())
        for user in users:
            u_similar[user] = self.related_users(user)
        u_similar.sort(reverse=True)
        
    def related_users(self, user):
        """Return list of scores of related users
        """
        scores = {}
        for r in self.data.u_watching[user]:
            n = len(self.data.watching_r[r])
            for u in self.data.watching_r[r]:
                if u == user:
                    continue
                if u in scores:
                    scores[u] += 1 / log(3 + n, 10)
                else:
                    scores[u] = 1 / log(3 + n, 10)
            related = []
            for u, s in scores.items():
                related.append((s/sqrt(len(self.data.u_watching[user])*
                                       len(self.data.u_watching[u])),u))
            related.sort(reverse=True)
            return related

    def related_items(self, item):
        """Return list of scores of related items
        """
        scores = {}
        for u in self.data.watching_r[item]:
            n = len(self.data.u_watching[u])
            for r in self.data.u_watching[u]:
                if r == item:
                    continue
                if r in scores:
                    scores[r] += 1 / log(3 + n, 10)
                else:
                    scores[r] = 1 / log(3 + n, 10)
                    
        related = []
        for r, s in scores.items():
            related.append((s/sqrt(len(self.data.watching_r[item]) * 
                                   len(self.data.watching_r[r])), r))
        related.sort(reverse=True)
        return related

    def recommend(self, user, type='item_based', topk=10):
        """Recommend repos for user 'user'
        """
        repos = {}
        if not cmp(type,'item_based'):
            # Item based recommend
            for repo in self.data.u_watching[user]:
                for s, r in self.related_items(repo):
                    if r in repos:
                        repos[r] += s
                    else:
                        repos[r] = s
            recs = []
            for r, s in repos.items():
                if r in self.data.u_watching[user]:
                    continue
                recs.append((s,r))
            recs.sort(reverse=True)
            return recs[:topk]
        else:
            # User based recommend
            for s, u in self.related_users(user):
                for r in self.data.u_watching[u]:
                    if r in repos:
                        repos[r] += s
                    else:
                        repos[r] = s
            recs = []
            for r, s in repos.items():
                if r in self.data.u_watching[user]:
                    continue
                recs.append((s,r))
            recs.sort(reverse=True)
            return recs[:topk]
