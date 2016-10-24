#!/usr/bin/env python

# or after having  added ! in front
# /home/gmatasci/anaconda/bin python

# -*- coding: utf-8 -*-
"""
Created on Fri Jan  9 00:53:18 2015

@author: gmatasci
"""

import numpy as np    # numpy for MATLAB-like operations
import urllib2        # read URLs
from bs4 import BeautifulSoup   # parse URLs
import xlwt    # export to Excel
from tempfile import TemporaryFile

# initialize lists of strings ('' or "" are the same)
teams = ['biel', 'kloten_flyers', 'zug', 'lausanne', 'geneve_servette',
         'ambri_piotta', 'davos', 'fribourg_gotteron', 'lugano',
         'rapperswil_jona', 'bern', 'zsc_lions']

#teams = ['zsc_lions']

columnNames = ["table_cell Nr", 
           "table_cell Name",
           "table_cell S",
           "table_cell G",
           "table_cell A",
           "table_cell P",
           "table_cell St",
           "table_cell plusMinus",
           "table_cell SoG"]

headersPl = ["Team",
            "Nr", 
            "Name",
            "GP",
            "G",
            "A",
            "P",
            "PIM",
            "+/-",
            "SoG",
            "Sh%",
            "GPG",
            "APG",
            "PPG",
            "SoGPG",]

headerTmCorner = "Team"            
headersTm = ["GF", 
            "SF",
            "GA",
            "SA",
            "Sh %",
            "Sv %",
            "PDO",
            "GF %",
            "SF %"]        
            
# initialize a list of empty lists (10)
tableNLA = [[] for i in range(10)]
teamTotals = np.zeros((len(teams),9))        
# loop over the elements of the list "teams"
for idxT, t in enumerate(teams):
    link = 'http://www.nationalleague.ch/NL/clubs/fr/{}.php'.format(t) # format string t to be included in string "link"
    page = urllib2.urlopen(link)
    soup = BeautifulSoup(page)  # parse with BeautifulSoup
    
    regSeasonSoup = soup.find_all("div", {"id": 'table_qualification'})

    table = []
    # loop over the columns of the stat tables
    for colName in columnNames:
        column = []
        # loop over all the div tags of the HTML source code with a class value equal to colName
        for node in regSeasonSoup[0].find_all("div", {"class": colName}):
            caseSpaced = ''.join(node.find_all(text=True))   # join all the strings found in this node (a list) with a void string to concatenate them
            if colName == "table_cell Name":    # leave the player name in Unicode (because of accents)
                column.append(caseSpaced.strip()) # append to list column the caseSpaced stripped of any trailing spaces
            else:   # for all the rest of the columns convert Unicode to a normal string
                column.append(caseSpaced.strip().encode('UTF8'))
        table.append(column)   # once the list column contains the data for all the players and it to the list of lists table
        
    # to remove goalies
    goalieTable = []
    nrMen = len(table[1])  # nr of players + goalies (length of the 2nd list of table, index = 1)
    nrPlayers = len(table[len(table)-1])  # nr of players (length of the last list of table, i.e. SoG valid only for players)
    for idxCol in range(len(table)-2):  # iterate idxCol over a vector of values created by range()
        for idxPl in range(nrMen):
            if idxPl >= nrPlayers:   # when idxPl reaches nrPlayers...
                table[idxCol].pop(len(table[idxCol-1]))   # ...remove (pop out) the last element of table[idxCol], i.e. the goalie-related data
    table.insert(0,[t]*nrPlayers)   # insert a first column (1st list at position 0) with the name of the current team t (repeat team name with operator * nrPlayers times)
    
    # fill the big table tableNLA by extending the corresponding lists (add elements of table to the initial list tableNLA)
    for idxCol in range(len(table)):        
        tableNLA[idxCol].extend(table[idxCol])
    
    gf = sum(np.array(table[4], dtype='f'))    
    sf = sum(np.array(table[9], dtype='f'))
    
    sv = float(0)
    sa = float(0)
    for node in regSeasonSoup[0].find_all("div", class_="table_cell SaSoG"):
        case = ''.join(node.find_all(text=True))
        sv += float(case.split('/')[0])
        sa += float(case.split('/')[1])
    
    ga = sa-sv
    
    sh_pct = gf/sf * 100
    sv_pct = sv/sa * 100
    
    PDO = (sh_pct + sv_pct)
    gf_pct = gf / (gf+ga) * 100
    sf_pct = sf / (sf+sa) * 100
     
    teamTotals[idxT,0] = gf
    teamTotals[idxT,1] = sf
    teamTotals[idxT,2] = ga
    teamTotals[idxT,3] = sa
    teamTotals[idxT,4] = sh_pct
    teamTotals[idxT,5] = sv_pct
    teamTotals[idxT,6] = PDO
    teamTotals[idxT,7] = gf_pct
    teamTotals[idxT,8] = sf_pct

# compute new column Sh%
shPct = list( np.array(map(float, tableNLA[4])) / np.array(map(float,tableNLA[9])) )   # map to floats the lists of iterests, convert them to arrays with np.array(), and put the result in a list
# loop over all elements x of shPct, put 0 instead of NaNs and Infs or else convert to a float with 3 decimal points
shPctOK = [0 if np.isnan(x) or np.isinf(x) else float("{0:.3f}".format(x)) for x in shPct]

GPG = list( np.array(map(float, tableNLA[4])) / np.array(map(float,tableNLA[3])) )
GPGOK = [0 if np.isnan(x) or np.isinf(x) else float("{0:.2f}".format(x)) for x in GPG]

APG = list( np.array(map(float, tableNLA[5])) / np.array(map(float,tableNLA[3])) )
APGOK = [0 if np.isnan(x) or np.isinf(x) else float("{0:.2f}".format(x)) for x in APG]

PPG = list( np.array(map(float, tableNLA[6])) / np.array(map(float,tableNLA[3])) )
PPGOK = [0 if np.isnan(x) or np.isinf(x) else float("{0:.2f}".format(x)) for x in PPG]

SoGPG = list( np.array(map(float, tableNLA[9])) / np.array(map(float,tableNLA[3])) )
SoGPGOK = [0 if np.isnan(x) or np.isinf(x) else float("{0:.2f}".format(x)) for x in SoGPG]

tableNLA.extend([shPctOK, GPGOK, APGOK, PPGOK, SoGPGOK])  # add as last place in list of lists tableNLA


#tableNLAfinal = zip(*tableNLA)   # the star operator unpacks the list as separate arguments   

# loop to create a list for each row of the table (data for each player)
# equivalent to zip(*arg)
tableNLAfinal = []  
for idxLin in range(np.shape(tableNLA)[1]):     # np.shape(listOfLists)[1] = size(,1)
    listRow = []
    for idxCol in range(np.shape(tableNLA)[0]):   # np.shape(listOfLists)[0] = size(,2)
        if idxCol == 0 or idxCol == 2:      # if column has strings...
            listRow.append(tableNLA[idxCol][idxLin])  # ...simply append element...
        else:
            listRow.append(float(tableNLA[idxCol][idxLin]))   # ...otherwise, if numeric, convert to float
    tableNLAfinal.append(listRow)   # populate the final list of lists tableNLAfinal with the lists of each row
    
# sort descending (reverse=True) by SoG (10th column of index 9)
tableNLAsorted = sorted(tableNLAfinal, key=lambda tup: tup[14], reverse=True) 

tableNLAsorted.insert(0, headersPl)   # insert a first list with column headers

# save to a Excel file using package xlwt and 
book = xlwt.Workbook()
sheet1 = book.add_sheet('Players')   # use method add_sheet() on the object book
for idxLin, lin in enumerate(tableNLAsorted):   # enumerate() returns a tuple (idxLin, lin) with the index of the element (scalar idxLin) and the elements itself (list lin)
    for idxCol, case in enumerate(lin):
        sheet1.write(idxLin,idxCol,case)     # write in sheet1 the Excel cell case at row idxLin and column idxCol

sheet2 = book.add_sheet('Teams')   # use method add_sheet() on the object book
sheet2.write(0, 0, headerTmCorner)
for idxLin in range(teamTotals.shape[0]):   # enumerate() returns a tuple (idxLin, lin) with the index of the element (scalar idxLin) and the elements itself (list lin)
    sheet2.write(idxLin+1, 0, teams[idxLin])
    for idxCol in range(teamTotals.shape[1]):
        if idxLin == 0:
            sheet2.write(0,idxCol+1, headersTm[idxCol])
        case = float("{0:.2f}".format(teamTotals[idxLin, idxCol]))
        sheet2.write(idxLin+1,idxCol+1, case)     # write in sheet1 the Excel cell case at row idxLin and column idxCol    
    
# save file
name = "NLAstats.xls"
book.save(name)
book.save(TemporaryFile())




    
    

                
    
    
        
#    SoG = []
#    for node in soup.find_all("div", {"class": "table_cell SoG"}):
#        SoG.append(int(''.join(node.find_all(text=True))))
#        
#    Name = []
#    for node in soup.find_all("div", {"class": "table_cell Name"}):
#        nameSpaced = ''.join(node.find_all(text=True))
#        Name.append(nameSpaced.strip())
    
    
#    evenRows = []
#    for node in soup.find_all("div", {"class": "table_row_even"}):
#        even = []
#        
#        
#    odd = []
#    for node in soup.find_all("div", {"class": "table_row_odd"}):
#        oddSpaced = ''.join(node.find_all(text=True))
#        odd.append(oddSpaced.strip())
#        
#    table = []   
#    for el in range(0,max(len(even), len(odd))):
#        if el < len(even):
#            table.append(even[el])       
#        if el < len(odd):
#            table.append(odd[el])
    
#        
#    TotSoG = np.asarray(SoG).sum()
#    TotSoGs.append(TotSoG)
#    SoGs.append(SoG)
#    Names.append(Name)
