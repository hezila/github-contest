#!/usr/bin/env python
try:
    import cPickle as pickle
except:
    import pickle

from datetime import date
import os

from math import log
from collections import defaultdict
from utils import msg
from pprint import pprint

class Database:
    def __init__(self,datadir):
        """Constructor
        """
        self.datadir = datadir
        self.test_u = []
        self.top_repos = []
        self.fields = ['test_u','top_repos']

        if self.pickle_jar():
            return
        
        fields = (
	    # dict		key		=value
	    ("watching_r	repos		=user",				list),
	    ("u_watching	user		=repos",			list),
	    ("r_info		repos		=author, name, creation",	list),
	    ("r_name		repos_name	=repos",			list),
	    ("r_langs		repos		=lang, kloc",			list),
            ("r_lang_tuple      repos           =tuple_of_lang",                list),
	    ("forks_of_r	parent		=child",			list),
	    ("parent_of_r	child		=parent",			int),
	    ("gparent_of_r	child		=grandparent",			int),
	    ("lang_by_r         lang            =kloc, repos",                  list),
            ("u_authoring	author		=repos",			list),
	)
        for defn, datatype in fields:
            name, key, _ = defn.split(None, 2)
            setattr(self, name, defaultdict(datatype))
            self.fields.append(name)
        self.fields.sort()

        # collect data
        self.parse_test()
        self.parse_watching()
        self.parse_repos()
        self.parse_lang()

        self.fill_pickle_jar()

    def pickle_jar(self):
        """Check whether we have save data to pickle
        """
        jar = "/".join((self.datadir,"pickle.jar"))
        if os.path.exists(jar):
            try:
                jarf = open(jar,'r')
                d = pickle.load(jarf)
                jarf.close()
            except:
                return False
            self.fields = d['fields']
            for field in self.fields:
                setattr(self,field,d[field])
            return True
        else:
            return False

    def fill_pickle_jar(self):
        """Fill the data to pickle
        """
        jar = '/'.join((self.datadir,"pickle.jar"))
        d = {}
        
        msg("Filling pickle jar '%s'" % jar)

        for field in self.fields:
            d[field] = getattr(self, field)
        d['fields'] = self.fields
        
        jarf = open(jar, 'w')
        pickle.dump(d, jarf)
        jarf.close()

    def parse_watching(self):
        """Parse watching data from file "data.txt"
        """
        msg("Parsing data.txt")
        lines = file('/'.join((self.datadir,"data.txt"))).read().split('\n')
        pairs = [[int(x) for x in line.split(':')] for line in lines if line]
        for user, repos in pairs:
            self.watching_r[repos].append(user)
            self.u_watching[user].append(repos)

    def parse_repos(self):
        """Parse repos information from file "repos.txt"
        """
        msg("Parsing repos.txt")
        lines = file('/'.join((self.datadir, "repos.txt"))).read().split('\n')
        pairs = [line.replace(':',',').split(',') for line in lines if line]
        pairs = [tuple([int(pair[0]),
                        int(pair[3]) if pair[3:4] else 0,
                        pair[1],
                        pair[2]
                    ])
                 for pair in pairs]
        for repos, parent, name, creation in pairs:
            if parent > 0:
                self.forks_of_r[parent].append(repos)
                self.parent_of_r[repos] = parent
            author, name = name.split('/')
            words = [int(x) for x in creation.split('-')]
            creation = date(words[0],words[1],words[2]).toordinal()
            self.r_info[repos] = (author, name, creation)
            self.u_authoring[author].append(repos)
            self.r_name[name].append(repos)

        for repos_gen1, repos_gen2 in self.parent_of_r.items():
            if repos_gen2 in self.parent_of_r:
                repos_gen3 = self.parent_of_r[repos_gen2]
                self.gparent_of_r[repos_gen1] = repos_gen3

    def parse_lang(self):
        """Parse the repos langs information from file "lang.txt"
        """
        msg("parsing lang.txt")
        lines = file('/'.join((self.datadir,"lang.txt"))).read().split('\n')

        pairs = [line.split(":") for line in lines if line]
        pairs = [(int(pair[0]),
                  [tuple(x.split(";")) for x in pair[1].split(",")])
                 for pair in pairs]
        pairs = [(x, tuple([(int(z[1]), z[0].lower()) for z in y]))
                 for (x, y) in pairs]


        all_langs = defaultdict(bool)
        for repos, langs in pairs:
            for kloc, lang in langs:
                all_langs[lang]=True
        all_langs = sorted(all_langs.keys())
        
        msg("building lang_by_r and r_langs")
        for repos, langs in pairs:
            for kloc, lang in langs:
                lnloc = int(log(kloc + 1, 10))
                self.lang_by_r[lang].append((lnloc, repos))
                self.r_langs[repos].append((lang,lnloc))
        for lang in self.lang_by_r.keys():
            self.lang_by_r[lang].sort(key=lambda x:x[1])

    def parse_test(self):
        """Parse the test user from file "test.txt"
        """
        msg("parsing test.txt")
        lines = file('/'.join((self.datadir, "test.txt"))).read().split('\n')
        self.test_u = sorted([int(line) for line in lines if line])

    def summary(self, unabridged=False):
        props= ("watching_r "
                "u_watching "
                "r_info "
                "r_name "
                "r_langs "
                "forks_of_r "
                "parent_of_r "
                "gparent_of_r "
                "lang_by_r "
                "u_authoring "
                ).split()
        for prop in props:
            print(">> %s" % prop)
            if unabridged:
                pprint(dict(getattr(self, prop)).items())
            else:
                pprint(dict(getattr(self, prop)).items()[:5])
            print("")

        msg(">> test_u")
        if unabridged:
            pprint(self.test_u)
        else:
            pprint(self.test_u[:5])
