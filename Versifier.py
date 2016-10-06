import os
import sys
import re

#PARATEXT MODULE VERSIFICATION TOOL
#VERSION 1.0.0
#Submitted October 6, 2016
#Tested in Python 2.5
#By Matthew Lee 
#ParaTExt has some basic tools to check Bible Modules, as well as showing references that are not yet translated. 
#While you can configure your current versification, there is no automated way to convert a module to a different versification. 
#This python script allows module creators to:
#  * verify valid /ref references of a Bible module (when used in conjunction with PT tools)
#  * specify verses when whole chapters are intended
#  * split refs properly when they span chapters. 
#  * convert all /ref imports and $() refs of an existing module to a new versification for wider distribution.  

#Usage
#=================================
#Edit the configurations in this header and launch the script in Python 2.5.

#Input File Config
#=================================
ParatextProjectsFolder = 'D:\Dropbox\My Paratext Projects\\'
InFile = ParatextProjectsFolder + 'Modules\ProtLec-VrsEng.sfm'

#Output File Config
#=================================
OutFile = ParatextProjectsFolder + 'Modules\Output\ProtLec-VrsOrgTemp.sfm'
#This file contains notes about conversion decisions made by this script. It can be used to cross-check the decisions made by the program.
CommentFile = ParatextProjectsFolder + 'Modules\Output\ProtLec-VrsEngTemp.Comments-NoNT.sfm'

#Versification Configuration
#================================= 
#If set to True, DoConvertVersification will convert from one versification to another as well as correcting incompatible verse references. If set to False, only corrects incompatible verses in the output file. 
DoConvertVersification = False 
#This is the Link to the versification files of the input Module from your Paratext Projects folder. 
InputVersification = ParatextProjectsFolder + 'eng.vrs'
#This is the Link to the target versification's confguration file from your Paratext Projects folder.
OutputVersification = ParatextProjectsFolder + 'org.vrs'
TargetVersificationName = 'Original'

#Filters
#=================================
#If set to True, FilterNTRefs will not include extracts from the New Testament (Useful if the community already has the NT, but not the OT).
FilterNTRefs = False

#=================================
#End of Config

def Convert(TargetVerse, Correlations):
    matchVerseless = re.match(ur'^([A-Z0-9]{3}) \d+(,\d+)*$',TargetVerse)
    needsChange = 'Unknown'
    if matchVerseless:
        needsChange = False
        return TargetVerse
    else:
        testBook = re.search(ur'^([A-Z0-9]{3})',TargetVerse)
        testChap = re.search(ur'^[A-Z0-9]{3} (\d+):',TargetVerse)    
        if not testBook or not testChap:
            print TargetVerse 
        currentBook = re.search(ur'^([A-Z0-9]{3})',TargetVerse).group(1)
        currentChapter = re.search(ur'^[A-Z0-9]{3} +(\d+):',TargetVerse).group(1)
        verseList = re.search(ur':(.*)',TargetVerse).group(1)
        verseArray = list(verseList)
        outputString = ""
        i = 0
        currentVerse = ""
        targetChapter = ""
        secondChapter= 0
        while i <= len(verseArray)-1:
            NextUp = str(verseArray[i])
            CharIsNum = re.match(r'\d',NextUp)
            if CharIsNum and i < len(verseArray)-1:
                currentVerse = currentVerse + str(verseArray[i])
                i = i+1
            elif CharIsNum and i == len(verseArray)-1:
                currentVerse = currentVerse + str(verseArray[i])
                sublist = [row for row in Correlations if (row[0] == currentBook and row[1] == int(currentChapter) and row[2] == int(currentVerse))]
                Found = False
                for entry in sublist:
                    if targetChapter == "":
                        targetChapter = entry[4]
                    elif entry[4] > int(targetChapter):
                        secondChapter = entry[4]
                    targetVerse = entry[5]
                    Found = True
                if Found and int(targetChapter) < secondChapter:
                    outputString = outputString + str(secondChapter) + ":"
                    #the dash is wrong
                if Found:
                    outputString = outputString + str(targetVerse)
                    currentVerse = ""
                else:
                    outputString = outputString + currentVerse
                    currentVerse = ""
                    targetChapter = currentChapter
                i = i+1
            elif not CharIsNum and currentVerse == "":
                outputString = outputString + verseArray[i]
                i = i+1
            else:
                sublist = [row for row in Correlations if (row[0] == currentBook and row[1] == int(currentChapter) and row[2] == int(currentVerse))]
                Found = False
                for entry in sublist:
                    if targetChapter == "":
                        targetChapter = entry[4]
                    elif entry[4] > int(targetChapter):
                        secondChapter = entry[4]
                    targetVerse = entry[5]
                    #need to flag if chapter changes twice
                    Found = True
                if Found and int(targetChapter) < secondChapter:
                    outputString = outputString + str(secondChapter) + ":"
                    #the dash is wrong
                if Found:
                    outputString = outputString + str(targetVerse) + verseArray[i]
                    currentVerse = ""
                else:
                    outputString = outputString + currentVerse + verseArray[i]
                    currentVerse = ""
                    targetChapter = currentChapter
                i = i+1
        finalString = currentBook + " " + str(targetChapter) +":"+ outputString
    return finalString


#Init Temporary Variables
i = 0
InputVrs = []
Corr = []
numChanges = 0
lastS2 = ""
FoundCorrespondances = False

vrs1 = open(InputVersification,"r")
for line in vrs1:
    matchBook = re.search(r'^[A-Z0-9]{3} [^=]*\n',line)
    if matchBook:
        line = re.sub(r'\d+:',"",line)
        line = re.sub(r'\n',"",line)
        InputVrs.append(line.split(" "))
    matchCorrespondance = re.search(r'^[A-Z0-9]{3} .*?=.*?\n|# [A-Z0-9]{3} .*?=.*?\n',line)
    if matchCorrespondance:
        FoundCorrespondances = True
        line = re.sub(r'^# (.*) *#.*\n',r'\1\n',line)
        currentBook = re.sub(r'^([A-Z0-9]{3}).*\n',r'\1',line)
        InChap = int(re.sub(r'^[A-Z0-9]{3} (\d+).*\n',r'\1',line))
        InVerseStart = int(re.sub(r'^[A-Z0-9]{3} \d+:(\d+).*\n',r'\1',line))
        IsInStartPart = re.search(r'^[A-Z0-9]{3} \d+:\d+[a-d].*\n',line)
        if IsInStartPart:
            InVerseStartPart = re.sub(r'^[A-Z0-9]{3} \d+:\d+([a-d]).*\n',r'\1',line)
        else:
             InVerseStartPart = ""
        IsInVerseStop = re.search(r'^[A-Z0-9]{3} \d+:\d+-(\d+).*\n',line)
        if IsInVerseStop:
            InVerseStop = int(re.sub(r'^[A-Z0-9]{3} \d+:\d+-(\d+).*\n',r'\1',line))
            IsStopPart = re.search(r'^[A-Z0-9]{3} \d+:\d+[a-d]*-\d+[a-d].*\n',line)
            if IsStopPart:
                InVerseStopPart = re.sub(r'^[A-Z0-9]{3} \d+:\d+-\d+([a-d]).*\n',r'\1',line)
            else:
                InVerseStopPart = ""
        else:
            InVerseStop = InVerseStart
            InVerseStopPart= InVerseStartPart
                
        ChapLet = re.search(r'.*= [A-Z0-9]{3} ([A-Z]+).*\n',line)
        if not ChapLet:
            OutChap = int(re.sub(r'.*= [A-Z0-9]{3} (\d+).*\n',r'\1',line))
        OutVerseStart = int(re.sub(r'.*= [A-Z0-9]{3} \d+:(\d+).*\n',r'\1',line))
        IsOutStartPart = re.search(r'.*= [A-Z0-9]{3} \d+:\d+[a-d].*\n',line)
        if IsOutStartPart:
            OutVerseStartPart = re.sub(r'.*= [A-Z0-9]{3} \d+:\d+([a-d]).*\n',r'\1',line)
        else:
             OutVerseStartPart = ""
        IsOutVerseStop = re.search(r'.*= [A-Z0-9]{3} \d+:\d+-(\d+).*\n',line)
        if IsOutVerseStop:
            OutVerseStop = int(re.sub(r'.*= [A-Z0-9]{3} \d+:\d+-(\d+).*\n',r'\1',line))
            IsOutStopPart = re.search(r'.*= [A-Z0-9]{3} \d+:\d+[a-d]*-\d+[a-d].*\n',line)
            if IsOutStopPart:
                OutVerseStopPart = re.sub(r'^[A-Z0-9]{3} \d+:\d+-\d+([a-d]).*\n',r'\1',line)
            else:
                OutVerseStopPart = ""
        else:
            OutVerseStop = OutVerseStart
            OutVerseStopPart = OutVerseStartPart            
        
        Adder = 0
        if not IsInVerseStop:
            Entry = [currentBook,InChap,InVerseStart,InVerseStartPart,OutChap,OutVerseStart,OutVerseStartPart]
            Corr.append(Entry)
        else:
            for v in range(InVerseStart,InVerseStop+1):            
                if v == InVerseStart:
                    Entry = [currentBook,InChap,v,InVerseStartPart,OutChap,OutVerseStart,OutVerseStartPart]
                    Corr.append(Entry)
                elif v == InVerseStop:
                    Entry = [currentBook,InChap,v,"",OutChap,OutVerseStop,""]
                    Corr.append(Entry)
                else:
                    Entry = [currentBook,InChap,v,InVerseStopPart,OutChap,(OutVerseStart+Adder),OutVerseStopPart]
                    Corr.append(Entry)
                Adder = Adder + 1
        
vrs1.close
if DoConvertVersification:
    vrs2 = open(OutputVersification,"r")
    OutputVrs = []
    for line in vrs2:
        matchCorrespondance = re.search(r'^[A-Z0-9]{3} .*?=.*?\n|# [A-Z0-9]{3} .*?=.*?\n',line)
        matchBook = re.search(r'^[A-Z0-9]{3} ',line)
        if matchBook and not matchCorrespondance:
            line = re.sub(r'\d+:',"",line)
            line = re.sub(r'\n',"",line)
            OutputVrs.append(line.split(" "))
        if matchCorrespondance:
            if FoundCorrespondances == True:
                break
            line = re.sub(r'^# (.*) *#.*\n',r'\1\n',line)
            #The following line reads correspondances in reverse. 
            line = re.sub(r'(.*)( = )(.*)',r'\3\2\1',line)
            currentBook = re.sub(r'^([A-Z0-9]{3}).*\n',r'\1',line)
            InChap = int(re.sub(r'^[A-Z0-9]{3} (\d+).*\n',r'\1',line))
            InVerseStart = int(re.sub(r'^[A-Z0-9]{3} \d+:(\d+).*\n',r'\1',line))
            IsInStartPart = re.search(r'^[A-Z0-9]{3} \d+:\d+[a-d].*\n',line)
            if IsInStartPart:
                InVerseStartPart = re.sub(r'^[A-Z0-9]{3} \d+:\d+([a-d]).*\n',r'\1',line)
            else:
                 InVerseStartPart = ""
            IsInVerseStop = re.search(r'^[A-Z0-9]{3} \d+:\d+-(\d+).*\n',line)
            if IsInVerseStop:
                InVerseStop = int(re.sub(r'^[A-Z0-9]{3} \d+:\d+-(\d+).*\n',r'\1',line))
                IsStopPart = re.search(r'^[A-Z0-9]{3} \d+:\d+[a-d]*-\d+[a-d].*\n',line)
                if IsStopPart:
                    InVerseStopPart = re.sub(r'^[A-Z0-9]{3} \d+:\d+-\d+([a-d]).*\n',r'\1',line)
                else:
                    InVerseStopPart = ""
            else:
                InVerseStop = InVerseStart
                InVerseStopPart= InVerseStartPart
                
            ChapLet = re.search(r'.*= [A-Z0-9]{3} ([A-Z]+).*\n',line)
            if not ChapLet:
                OutChap = int(re.sub(r'.*= [A-Z0-9]{3} (\d+).*\n',r'\1',line))
            OutVerseStart = int(re.sub(r'.*= [A-Z0-9]{3} \d+:(\d+).*\n',r'\1',line))
            IsOutStartPart = re.search(r'.*= [A-Z0-9]{3} \d+:\d+[a-d].*\n',line)
            if IsOutStartPart:
                OutVerseStartPart = re.sub(r'.*= [A-Z0-9]{3} \d+:\d+([a-d]).*\n',r'\1',line)
            else:
                 OutVerseStartPart = ""
            IsOutVerseStop = re.search(r'.*= [A-Z0-9]{3} \d+:\d+-(\d+).*\n',line)
            if IsOutVerseStop:
                OutVerseStop = int(re.sub(r'.*= [A-Z0-9]{3} \d+:\d+-(\d+).*\n',r'\1',line))
                IsOutStopPart = re.search(r'.*= [A-Z0-9]{3} \d+:\d+[a-d]*-\d+[a-d].*\n',line)
                if IsOutStopPart:
                    OutVerseStopPart = re.sub(r'^[A-Z0-9]{3} \d+:\d+-\d+([a-d]).*\n',r'\1',line)
                else:
                    OutVerseStopPart = ""
            else:
                OutVerseStop = OutVerseStart
                OutVerseStopPart = OutVerseStartPart            
        
            Adder = 0
            if not IsInVerseStop:
                Entry = [currentBook,InChap,InVerseStart,InVerseStartPart,OutChap,OutVerseStart,OutVerseStartPart]
                Corr.append(Entry)
            else:
                for v in range(InVerseStart,InVerseStop+1):            
                    if v == InVerseStart:
                        Entry = [currentBook,InChap,v,InVerseStartPart,OutChap,OutVerseStart,OutVerseStartPart]
                        Corr.append(Entry)
                    elif v == InVerseStop:
                        Entry = [currentBook,InChap,v,"",OutChap,OutVerseStop,""]
                        Corr.append(Entry)
                    else:
                        Entry = [currentBook,InChap,v,InVerseStopPart,OutChap,(OutVerseStart+Adder),OutVerseStopPart]
                        Corr.append(Entry)
                    Adder = Adder + 1
else:
    OutputVrs = InputVrs

f = open(InFile,"r")
copyoffile = open(OutFile,"wt")
changes = open(CommentFile,"wt")
lineNum = 0
for line in f:
    lineNum = lineNum + 1
    lineOrig = line
    printLines = True
#Breakpoint for testing specific verses, change the search and set a breakpoint on the print command.
    FindVerse = re.search('Google',line)
    if FindVerse:
        print 'Found'
#End testing
    matchRef = re.search(r'\\ref',line)
    matchR = re.search(ur'[A-Z0-9]{3} [:\(\)\d,—\-0-9]+',line,re.UNICODE)
    matchNT = re.search(r'MAT|MRK|LUK|JHN|ACT|ROM|1CO|2CO|GAL|EPH|PHP|COL|1TH|2TH|1TI|2TI|TIT|PHM|HEB|JAS|1PE|2PE|1JN|2JN|3JN|JUD|REV',line)
    if matchRef:
        if matchNT and FilterNTRefs:
            printLines = False
            changes.write("(" + str(lineNum) + ') Removed NT Ref: '+ line[:-1] + '\n')
            print "(" + str(lineNum) + ') Removed NT Ref: '+ line[:-1]
            numChanges = numChanges + 1
        else:
            #need check for splitchaps in refs
            matchSplitChap = re.search(ur':[—0-9a-e-]{1,8}?:',line)
            matchVerseless = re.search(ur'^\\ref ([A-Z0-9]{3}) (\d+\n|\d+,\d.*\n)',line)
            if not matchSplitChap and not matchVerseless:
                p = re.compile(ur'([A-Z0-9]{3} [:\(\)\d, \xe20-9a-e-]+\d[a-e]?)')
                verses = p.findall(line)
                for verseRange in verses:              
                    if DoConvertVersification:
                        result = Convert(verseRange, Corr)
                    else:
                        result = verseRange
                    if result <> verseRange:
                        line = line.replace(verseRange,result)
                printLines = True          
            matchSplitChap = re.search(ur':[—\-0-9a-e]{1,8}?:',line)
            matchVerseless = re.search(ur'^\\ref ([A-Z0-9]{3}) \d+\n',line)
            if matchSplitChap and not matchVerseless:
                currentBook = re.search(r'([A-Z0-9]{3}).*\d.*',line).group(1)
                currentChapter = int(re.search(r'.*?(\d+):\d+',line).group(1))
                for x in OutputVrs:
                    if x[0] == currentBook:
                        maxVerse = x[currentChapter] 
                line = re.sub('—','-',line)
                line = re.sub(r'-\d+:','-' + maxVerse + '\n\\\\ref ' + currentBook + " " + str(currentChapter + 1) + ':1-',line) #something broken in unicode
                line = re.sub(r':(\d+)-\1([^\d]|$)',r':\1\2',line)
                printLines=True
            if matchVerseless:
                Changed = True
                currentBook = re.search(r'([A-Z0-9]{3}).*\n',line).group(1)
                TestDouble = re.search(r'[A-Z0-9]{3} (\d+), *\d+\n',line)
                if TestDouble: #need a better test here
                    currentChapter = int(re.search(r'[A-Z0-9]{3} (\d+).*?\n',line).group(1))
                    sublist = [row for row in OutputVrs if (row[0] == currentBook)]
                    for x in sublist:
                        MaxVerse = x[currentChapter] 
                    if sublist:
                        line =  line.replace(' ' + str(currentChapter),str(currentChapter)+":1-"+str(MaxVerse))
                    else:
                        line =  line.replace(' ' + str(currentChapter),str(currentChapter)+":2-"+str(MaxVerse))
                    currentChapter = int(re.search(r', *(\d+)\n',line).group(1))
                    sublist = [row for row in OutputVrs if (row[0] == currentBook)]
                    for x in sublist:
                        MaxVerse = x[currentChapter] 
                    if sublist:
                        line =  line.replace(',' + str(currentChapter),'\n\\ref '+ currentBook +str(currentChapter)+":1-"+MaxVerse)
                    else:
                        line =  line.replace(',' + str(currentChapter),'\n\\ref '+ currentBook +str(currentChapter)+":2-"+MaxVerse)
                else:
                    currentChapter = int(re.search(r'[A-Z0-9]{3} (\d+)\n',line).group(1))
                    sublist = [row for row in OutputVrs if (row[0] == currentBook)]
                    for x in sublist:
                        MaxVerse = x[currentChapter]
                    sublist = [row for row in Corr if (row[0] == currentBook and row[1] == int(currentChapter) and row[2] == 0)]
                    if sublist:
                        line =  re.sub(str(currentChapter),str(currentChapter)+":2-"+str(MaxVerse),line)
                    else:
                        line =  re.sub(str(currentChapter),str(currentChapter)+":1-"+str(MaxVerse),line)
                printLines=True
    elif matchR and DoConvertVersification:
        p = re.compile(ur'([A-Z0-9]{3} [:\(\)\d,—\-0-9a-e]+\d[a-e]?)',re.UNICODE) # [0-9\:\(\)\d,�\-]+
        verses = p.findall(line)
        for verseRange in verses:
            result = Convert(verseRange, Corr)
            if verseRange <> result:
                line = line.replace(verseRange,result)
                printLines=True
    else:
        isS2 = re.search(r'\\s2',line)
        if isS2:
            S2 = line
            printLines=True
        isS1 = re.search(r'\\s1',line)
        if isS1:
            S1 = line
            printLines=True
        isVersification = re.search(r'\\vrs',line)
        if isVersification:
            line = '\\vrs ' + TargetVersificationName + '\n'
            printLines=False
            copyoffile.write(line)
        isRemark = re.search(r'\\rem ',line)
        if isRemark and lineNum > 1:
            printLines = False
        isAbb = re.search(r'\\abb ',line)
        if isAbb and lineNum > 1:
            printLines = False
    matchParen = re.search(r'([A-Z0-9]{3} [:\d,—\-0-9a-e]+\()',line)
    #Modules can't handle secondary parentheses in \ref tags or $( ) tags. This 'Fixes' it. 
    if matchParen:
            line = re.sub(ur'(\$\([A-Z0-9]{3})( [:\(\)\d,—\-0-9a-e]+?\(\d*.*?\d\)[:\(\)\d,—\-0-9a-e]*(\(\d*.*?\d\)[:\(\)\d,—\-0-9a-e]*)*)\)',r'\1)\2',line)
    if printLines:
        #This section prints relevant S1's, S2's, line mumbers, and changed lines to the comments file.
        if lineOrig <> line:
            numChanges = numChanges+1
            if S2 <> lastS2:
                changes.write("\n")
                print ""
                changes.write(S2[4:-1] + ":\n")
                print S2[4:-1]+': '+ S1[4:-1]
                changes.write(S1[4:] + '------------\n')
                print '------------'
            lastS2 = S2
            print '(' + str(lineNum) + ') ' + lineOrig[:-1] +' --> ' + line[:-1]
            changes.write('(' + str(lineNum) + ') ' + lineOrig[:-1] +' --> ' + line)
        copyoffile.write(line)
f.close()
print str(numChanges) + " lines changed in total."
changes.write(str(numChanges) + " lines changed in total.")
changes.close()
copyoffile.close()