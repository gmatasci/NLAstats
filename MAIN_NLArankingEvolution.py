#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Fri Jan  9 00:53:18 2015

@author: gmatasci
"""


import numpy as np    # numpy for MATLAB-like operations
import matplotlib.pyplot as plt
import urllib2        # read URLs
from bs4 import BeautifulSoup   # parse URLs


plt.close("all")

figdir = '/home/gmatasci/Dropbox/PythonProjects/URLscrape/Figures/'

# initialize lists of strings ('' or "" are the same)
teams = ['HC Davos',
'SC Bern',
'EV Zug',
'ZSC Lions',
'Kloten Flyers',
'Lakers',
'Geneve',
'HC Lugano',
'EHC Biel',
'Ambri-Piotta',
'SCL Tigers',
'Fribourg',
'Lausanne HC']

teamColors = np.array(
            [[240, 240, 0],
            [255, 0, 0],
            [70, 130, 180],
            [0, 0, 0],
            [127, 255, 212],
            [128, 0, 128],
            [165, 42,  42],
            [225, 195, 0],
            [255, 140, 0],
            [0, 0, 139],
            [205, 133,  63],
            [0, 64, 0],
            [255, 0, 255]], dtype = 'f')/255
                           
seasons = np.array([2010, 2011, 2012, 2014, 2015])

months = np.array([9, 10, 11, 12, 1, 2, 3])
monthNames = ['Sept.', 'Oct.', 'Nov.', 'Dec.', 'Jan.', 'Febr.', 'Mar.']

for s in seasons:
    for t in teams:
        exec("{0}GFpct = []".format(t.replace(" ", "").replace("-", "")))
        exec("{0}PTSpct = []".format(t.replace(" ", "").replace("-", "")))
        
    for m in months:
     
        link = 'http://www.nationalleague.ch/NL/spiele/nla/fr/phase1_ranking.php?league=1&season={}&month={}'.format(s, m) # format string t to be included in string "link"
        page = urllib2.urlopen(link)
        soup = BeautifulSoup(page)  # parse with BeautifulSoup
        
        NLAdata = []
        for tr in soup.find_all('tr'):
            teamData = []
            for td in tr.find_all('td', class_="dark"):
                if td.text and not td.isSelfClosing:
                    case = td.text
                    if case == 'Genève':
                        case = 'Geneve'
                    teamData.append(case)
            if teamData:
                gp = float(teamData[2])
                pts = float(teamData[10])
                gf = float(teamData[9].split(':')[0])
                ga = float(teamData[9].split(':')[1])
                teamData[11] = gf/(gf+ga)
                teamData.append( pts/(gp*3) )
                NLAdata.append(teamData)
        
        for t in teams:
            for row in NLAdata:
                if row[1] == t:
                    exec("{0}GFpct.append(row[11])".format(t.replace(" ", "").replace("-", "")))
                    exec("{0}PTSpct.append(row[12])".format(t.replace(" ", "").replace("-", "")))
    
    plt.figure()
    for idxT, t in enumerate(teams):
        exec("plt.plot({0}GFpct, color = teamColors[idxT,], linewidth=2, label=t)".format( t.replace(" ", "").replace("-", "")))
    plt.xticks( range(len(months)), monthNames )
    plt.axis([-0.5, len(months)-0.5, 0.25, 0.7])
    plt.grid('on')
    plt.legend(bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.)
    plt.xlabel('Month of the season')
    plt.ylabel('Goals For %')
    plt.title('Season {}/{}'.format(s-1,s))   
    plt.savefig(figdir + 'GFpct_{}_{}.png'.format(s-1,s), bbox_inches='tight')
    plt.close("all")

    plt.figure()
    for idxT, t in enumerate(teams):
        exec("plt.plot({0}PTSpct, color = teamColors[idxT,], linewidth=2, label=t)".format( t.replace(" ", "").replace("-", "")))
    plt.xticks( range(len(months)), monthNames )
    plt.axis([-0.5, len(months)-0.5, 0.15, 0.85])
    plt.grid('on')
    plt.legend(bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.)
    plt.xlabel('Month of the season')
    plt.ylabel('Points %')
    plt.title('Season {}/{}'.format(s-1,s))
    plt.savefig(figdir +'PTSpct_{}_{}.png'.format(s-1,s), bbox_inches='tight')
    plt.close("all")

        

    
    

                
    

