from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#import unzip
import numpy as np
import re
import os
import time
import sys
from shutil import copyfile
import math


#assignmentDirectory = "D:/temp/DM2111"
#assignmentDirectory = "D:/Temp/DM2122/Practical2"
#assignmentDirectory = "D:/Temp/DM2122/Practical3"
#assignmentDirectory = "D:/Temp/DM2122/Practical4"
assignmentDirectory = r"D:\temp\gradebook_2016S1-DM2111_Assignment2"
reportDirectory = assignmentDirectory
studentListFile = 'GDT16IDNames.csv'
printNames = False

reservedWords = set()
operators = []
additionalKeys = set()
omitPatterns = []





def getCPPTokens():
    """
    Reads in the list of reserved words and operators
    """
    #reserved words
    f = open("reservedWords.txt", 'r')
    for line in f:        
        for word in line.rstrip('\n').split(' '):
            reservedWords.add(word)                
    f.close()

    #operators
    f = open("operators.txt", 'r')   
    for line in f:        
        for word in line.rstrip('\n').split(' '):            
            operators.append(re.sub(r"(.)", r'\\\1', word))
    
    # sort the operators from longest to shortest
    operators.sort(lambda x,y: cmp(len(y), len(x)))    
    f.close()

    #additional keys
    f = open("keyFunctions.txt", 'r')
    for line in f:        
        for word in line.rstrip('\n').split(' '):
            additionalKeys.add(word)                
    f.close()

    #omit Patterns
    #text matching these patterns will be removed
    f = open("omitPattern.txt", 'r')
    for line in f:
        if line[0] != '#':
            omitPatterns.append(line.rstrip('\n'))                
    f.close()    



def CPPAnalyzer(fileContents):
    """
    Reads in the CPP file contents and parses out the unimportant parts
    such as comments
    """
    #remove comments, and literal strings    

    #parsedContents = re.sub("(//.*?\n)|(/\*.*?\*/)|(\".*?\")", '', fileContents, flags=re.DOTALL)
    if not CPPAnalyzer.cRegexRC:
        regexOmitPatterns = r"|".join(omitPatterns)
        regexString = r"(//.*?\n)|(/\*.*?\*/)|(\".*?\")|(" + regexOmitPatterns + ")"
        #print regexString
        CPPAnalyzer.cRegexRC = re.compile(regexString, flags=re.DOTALL)        
    parsedContents = CPPAnalyzer.cRegexRC.sub('', fileContents)

    # sieve out variable names
    if not CPPAnalyzer.cRegexAllowedTokens:
        regexReservedWords = r"\b(" + r"|".join(reservedWords) + r")\b"
        regexOperators = r"|".join(operators)
        regexAdditionalKeys = r"\b(" + r"|".join(additionalKeys) + r")\b"
        regexString = regexReservedWords + "|" + regexAdditionalKeys + "|" + regexOperators
        #print regexReservedWords
        #print regexOperators        
        CPPAnalyzer.cRegexAllowedTokens = re.compile(regexString)

    validWords = ""
    for m in CPPAnalyzer.cRegexAllowedTokens.finditer(parsedContents):
        validWords += m.group(0) + " "        

    #print ">{+++}>", validWords
    return validWords

CPPAnalyzer.cRegexRC = None
CPPAnalyzer.cRegexAllowedTokens = None

def getListofFiles(directory, filename="", extension="", filterParameter=""):
    filenames = []
    for root, dirs, files in os.walk(directory):
        for file in files:           
            if (filename == "" or file == filename) and \
               (extension == "" or file.endswith(extension)) and \
               (filterParameter == "" or re.search(filterParameter, os.path.join(root, file)) != None):
                filenames.append((os.path.join(root, file), root, file))            
                    
    return filenames

def getDocuments(directory):

    fileContents = dict()
    fileNameTuple = getListofFiles(directory, extension="cpp")
    
    for fullPath, root, file in fileNameTuple:
        studentID = fullPath
        
        m = re.search("\d{6}\w", fullPath) #extract the student ID
        if m:
            studentID = m.group(0)

        f = open(fullPath, 'r')
        if studentID in fileContents:
            fileContents[studentID] += ' ' + f.read()
        else:
            fileContents[studentID] = f.read() #read character by character
        
        try:
            fileContents[studentID].decode('utf-8')
        except UnicodeDecodeError:
            print "UnicodeDecodeError at ", fullPath  


    return fileContents



def printVocabFrequency(vocabulary, count_matrix):
    """
    Prints the break down of the vocabulary frequency
    """
    print "Vocabulary items =", len(vocabulary)
    f = open(reportDirectory+"/Vocabulary.txt", 'w')        
    
    inv_map = {v:k for k, v in vocabulary.items()}
    for key in sorted(inv_map.keys()):
        f.write("%d %s\n" % (key, inv_map[key]))        

    f.close()

    # save the vocabulary frequency matrix    
    print count_matrix.shape
    np.savetxt(reportDirectory+ "/VocabularyFrequency.csv", count_matrix.transpose().toarray(), delimiter=",")
    #print count_matrix.todense().transpose()
    



def computeSimilarity(documentDict):

    documents = documentDict.values()    

    #tfidf_vectorizer = TfidfVectorizer()
    #tfidf_vectorizer = TfidfVectorizer(preprocessor=CPPAnalyzer, token_pattern=r"[^\s]+")
    countVectorizer = CountVectorizer(preprocessor=CPPAnalyzer, token_pattern=r"[^\s]+")

    #print countVectorizer

    #tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
    count_matrix = countVectorizer.fit_transform(documents)

    printVocabFrequency(countVectorizer.vocabulary_, count_matrix)    
    #print tfidf_matrix.shape

    #similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    similarity = cosine_similarity(count_matrix, count_matrix)
        
    return similarity

def generateReport(similarity, studentIDs):
    results = []
    key = set()
    for (x,y), value in np.ndenumerate(similarity):
        if x != y:
            first = min(x,y)
            second = max(x,y)
            if (first, second) not in key:
                results.append((value, first, second))
                key.add((first, second))

    results.sort(lambda tup1,tup2: cmp(tup2[0], tup1[0]))
    #print results

    f = open(reportDirectory+"/SimilarityRanking.txt", 'w')
    for score, first, second in results:
        f.write("%s %s %f\n" % (studentIDs[first], studentIDs[second], score))
    f.close()    

    return results
    
def printPlot(studentIDs, similarity):
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.colors as colors
    from matplotlib.backends.backend_pdf import PdfPages


    #print "Similarity", similarity
    lowerLim = np.amin(similarity)
    lowerLim = lowerLim + (1.0 - lowerLim) / 2.0
        
    pp = PdfPages(reportDirectory + '/SimilarityGraph.pdf')
    # color graph
    plt.figure(1)    
    plt.imshow(similarity, cmap=cm.jet, interpolation='bilinear', vmin=lowerLim, vmax=1.0)

    numrows, numcols = similarity.shape
    def format_coord(x, y):
        col = int(x+0.5)
        row = int(y+0.5)
        if col>=0 and col<numcols and row>=0 and row<numrows:
            z = similarity[row,col]
            return 'x=%s, y=%s, z=%1.4f'%(studentIDs[col], studentIDs[row], z)
        else:
            return ''

    plt.format_coord = format_coord


    ind = range(len(studentIDs))
    plt.xticks(ind, studentIDs, ha='center', size=6, rotation=90)
    plt.yticks(ind, studentIDs, va='center', size=6)

    plt.figure(2)
    plt.plot(similarity, 'o')
    plt.ylim((lowerLim, 1.005))
    plt.xlim((-0.5,numcols-0.5))
    plt.xticks(ind, studentIDs, ha='center', size=6, rotation=90)
    
    pp.savefig(1)
    pp.savefig(2)

    pp.close()

    plt.show()

def generateSigmaJSData(studentIDs, sortedResults, threshold=0.95):
    import json
    import random
    import csv
    import colorsys

    startHSV = colorsys.rgb_to_hsv(0, 0.2, 0.8)
    endHSV = colorsys.rgb_to_hsv(1, 0, 0)

    def interpolateHSV(p, startHSV, endHSV):
        return (startHSV[0] + (endHSV[0] - startHSV[0]) * p, 
                startHSV[1] + (endHSV[1] - startHSV[1]) * p, 
                startHSV[2] + (endHSV[2] - startHSV[2]) * p)

    def RGBTupletoHex(rgb):
        return "#%06X" % (int(255 * rgb[0]) << 16 | int(255 * rgb[1]) << 8 | int(255 * rgb[2]))
    

    print "Generating sigma.js data"
    adminNumberDict = {}
    with open(studentListFile, 'rb') as csvfile:
        csvReader = csv.reader(csvfile)
        for entry in csvReader:
            adminNumberDict[entry[0]] = entry[1]
    # read names from CSV File


    nodes = {} # { "id": "n2", "label": "And a last one", "x": 1, "y": 3, "size": 1 }
    edges = [] # { "id": "e0", "source": "n0", "target": "n1" }

    count = 0
    radius = 500
    for adminID in sorted(studentIDs):
        label = adminID.upper()
        label += " " + adminNumberDict.get(adminID.upper(),"")
        if printNames:
            label += " " + adminNumberDict.get(adminID.upper(), "")
        nodes[adminID] = {"id": adminID, 
                          "label":  label, 
                          "x": math.cos(math.pi * 2 * count/len(studentIDs) - math.pi / 2.0) * radius, 
                          "y": math.sin(math.pi * 2 * count/len(studentIDs) - math.pi / 2.0) * radius, 
                          "size": 1, 
                          "color": 0x000000}
        count += 1

    extrapolateFactor = 1.0 / (1.0 - threshold)    
    
    for score, first, second in sortedResults:
        if score > threshold:
            studID1 = studentIDs[first]
            studID2 = studentIDs[second]

            nodes[studID1]["size"] += 1
            nodes[studID2]["size"] += 1
            normalizedScore = (score-threshold) * extrapolateFactor             
            
            if (nodes[studID1]["color"] < normalizedScore):
                nodes[studID1]["color"] = normalizedScore
            if (nodes[studID2]["color"] < normalizedScore):
                nodes[studID2]["color"] = normalizedScore
            resultHSV = interpolateHSV(normalizedScore, startHSV, endHSV)
            resultRGB = colorsys.hsv_to_rgb(resultHSV[0], resultHSV[1], resultHSV[2])            
            edges.append({"id": "e"+str(len(edges)), 
                          "source": studID1, 
                          "target": studID2,
                          "size": str(normalizedScore * 3.5 + 0.1),
                          "color" : RGBTupletoHex(resultRGB),
                          "type" : "curve",
                          })

    # convert colour data into CSS color format
    for key, value in nodes.iteritems():        
        resultHSV = interpolateHSV(value["color"], startHSV, endHSV)
        resultRGB = colorsys.hsv_to_rgb(resultHSV[0], resultHSV[1], resultHSV[2])
        value['color'] = RGBTupletoHex(resultRGB)

    jsonData = {}
    jsonData["nodes"] = nodes.values()
    jsonData["edges"] = edges

    f = open(reportDirectory+"/data.json", 'w')
    f.write(json.dumps(jsonData, indent=4, separators=(',', ': ')))
    f.close()

    #open the graphViewer.html file and insert this data in the HTML file, so that we don't need to load files
    with open("graphViewer.html") as f_old, open(reportDirectory+"/graphViewer.html", "w") as f_new:
        for line in f_old:            
            f_new.write(line)
            if '1999a794-b1d1-4c85-b7bb-65ea80194008' in line:
                f_new.write("data = ")
                f_new.write(json.dumps(jsonData, indent=4, separators=(',', ': ')))

    #copy files over to the report folder
    filesToCopy = ["sigma.js/sigma.min.js", 
                   "sigma.js/plugins/sigma.parsers.json.min.js",
                   "sigma.js/plugins/sigma.renderers.edgeLabels/settings.js",
                   "sigma.js/plugins/sigma.renderers.edgeLabels/sigma.canvas.edges.labels.curve.js",
                   "sigma.js/plugins/sigma.renderers.edgeLabels/sigma.canvas.edges.labels.curvedArrow.js",
                   "sigma.js/plugins/sigma.renderers.edgeLabels/sigma.canvas.edges.labels.def.js",
                   ]
    if not os.path.exists(reportDirectory+"/sigma.js"):
        os.makedirs(reportDirectory+"/sigma.js")
        if not os.path.exists(reportDirectory+"/sigma.js/plugins"):
            os.makedirs(reportDirectory+"/sigma.js/plugins")        
        if not os.path.exists(reportDirectory+"/sigma.js/plugins/sigma.renderers.edgeLabels"):
            os.makedirs(reportDirectory+"/sigma.js/plugins/sigma.renderers.edgeLabels")
        for file in filesToCopy:
            copyfile(file, reportDirectory+"/"+file)    

def main():
    # if there is a command line input
    global assignmentDirectory

    if len(sys.argv) > 1:
        assignmentDirectory = sys.argv[1]    
    print "Assignment Directory = ", assignmentDirectory

    #unzip.unzipFiles(assignmentDirectory, subdir="/extracted/")    
    getCPPTokens()
    fileContents = getDocuments(assignmentDirectory)
    
    print len(fileContents), "entries\n"
    f = open(reportDirectory+"/StudentIndex.txt", 'w')    
    f.write("\n".join(["%d %s" % (ind, val) for ind, val in enumerate(fileContents.keys())]))
    f.close()
    

    t0 = time.time()
    
    similarity = computeSimilarity(fileContents)
    sortedResults = generateReport(similarity, fileContents.keys())
    

    #printPlot(fileContents.keys(), similarity)
    top_percent = 15
    threshold = sortedResults[len(sortedResults)*top_percent/100][0]
    #print threshold
    print "Threshold set at %d%% at %f" % (top_percent, threshold)
    generateSigmaJSData(fileContents.keys(), sortedResults, threshold=threshold)
    
    
    t1 = time.time()
    print "Done in %fs" % (t1-t0)




##########START##########
if __name__ == '__main__':
    main()


