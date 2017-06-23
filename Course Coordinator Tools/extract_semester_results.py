import re
from collections import OrderedDict
from os import path
import sys

#convert PDF to text first.
#use A-PDF text extractor
#http://www.a-pdf.com/text/

all_regex = OrderedDict()
all_regex["admin_id"] = "Adm\. No :\s+([0-9]{6}[A-Z])\s+[A-Z \-\']+"
all_regex["name"] = "Adm\. No :\s+[0-9]{6}[A-Z]\s+([A-Z \-b\']+)"
all_regex["sem"] = "No\. of Semesters in NYP :\s+([0-9])"
all_regex["credit_earned"] = "Credit Earned \(CM/PE/CE\)\s+:\s+((\d+)/(\d+)/(\d+))"
all_regex["credit_req"] = "Credit Required \(CM/PE/CE\)\s+:\s+((\d+)/(\d+)/(\d+))"
all_regex["gpa"] = "Grade Point Average \(GPA\) :\s+(\d+\.?\d*)"
all_regex["cwa"] = "Cumulative Weighted Average :\s+(\d+\.?\d*)"
all_regex["hgpa"] = "\\bGPA :\s+(\d+\.?\d*)"
all_regex["sgpa"] = "SGPA :\s+(\d?\.?\d*)"
all_regex["swa"] = "SWA : (\d+\.?\d*)"
all_regex["module_result"] = "(DM.+?)\s+(.+?)\s+(\w\w)\s+(\d)\s+([A-Z ])\s+(\d)\s+((?:\d+| ))\s+([\w\*\+]+)\s*([\d ])?"

#convert all_regex to compiled form
for key, value in all_regex.iteritems():
    all_regex[key] = re.compile(value)

def extract_results(filename):  
    all_students = []
    student = dict()
    adminID = ""
    with open(filename, 'r') as f:
        for line in f:          
            for key, regex in all_regex.iteritems():
                result = regex.search(line)
                if result:
                    if key == "module_result":                      
                        relevantList = []
                        module_result = result.groups()
                        #print m.group(1)
                        #print "\t".join(results)
                        
                        relevantList.append(module_result[0]) # module code
                        relevantList.append(module_result[1]) # module abbr
                        relevantList.append(module_result[2]) # module type
                        relevantList.append(module_result[6]) # module score
                        relevantList.append(module_result[7]) # module grade
                                                
                        #print module_result, relevantList
                        if key not in student:
                            student[key] = []
                        student[key].append(relevantList)
                    elif key == "hgpa" or key == "sgpa" or key == "swa":
                        if key not in student:
                            student[key] = []
                        student[key].append(result.group(1))
                    elif key == "credit_earned" or key == "credit_req":
                        #student[key] = result.group(1)                     
                        student[key+"_CM"] = result.group(2)
                        student[key+"_PE"] = result.group(3)
                        student[key+"_CE"] = result.group(4)
                    else:
                        if key == "admin_id" and student and student[key] != result.group(1):
                            all_students.append(student)
                            #print student
                            student = dict() #reset the student data
                        student[key] = result.group(1)


                    #print key, result.group(1)
            
        
            #print student
        # last student
        all_students.append(student)

    print len(all_students), "students results processed"
    return all_students

def print_results(all_student_results, name_file, module_result_file, gpa_trend_file):
    fname = open(name_file, 'w')
    fmr = open(module_result_file, 'w')
    fgpat = open(gpa_trend_file, 'w')

    fields = ["admin_id", "name", "sem", "credit_earned_CM", "credit_earned_PE", "credit_earned_CE", "credit_req_CM", "credit_req_PE", "credit_req_CE", "gpa", "cwa"]
    result_fields = ["admin_id", "sem", "module_code", "module_abbr", "module_type", "module_score", "module_grade"]
    gpa_trend_fields = ["admin_id", "name", "sgpa"]

    fname.write("\t".join(fields) + "\n")
    fmr.write("\t".join(result_fields) + "\n")
    fgpat.write("\t".join(gpa_trend_fields) + "\n")

    for student in all_student_results:
        #print student
        fname.write("\t".join([student.get(field_name, "") for field_name in fields]) + "\n")

        composite_key = [student["admin_id"], student["sem"]]
        for module_result in student["module_result"]:
            fmr.write("\t".join(composite_key + module_result) + "\n")

        # for GPA 
        gpa_data = []
        gpa_data.extend([student["admin_id"], student["name"]])
        gpa_data.extend(student["sgpa"])
        
        fgpat.write("\t".join(gpa_data) + "\n")


    fname.close()
    fmr.close()
    fgpat.close()


if __name__ == "__main__":
    SIMS_result_file = ""

    if len(sys.argv) > 1:        
        SIMS_result_file = sys.argv[1]        
    else:
        raw_input( "Enter the filename of your SIMS result file in text format or drag the file and drop it on top of this executable file to begin." )
        sys.exit(0)

    filename = path.splitext(path.basename(SIMS_result_file))[0]
    directory = path.dirname(SIMS_result_file)
        
    #directory = r"D:\temp\grades\/"
    #SIMS_result_file = r"D:\temp\grades\DMD09_15XX.txt"

    print SIMS_result_file

    all_results = extract_results(SIMS_result_file)
    print_results(all_results, 
                path.join(directory, filename + " names.tsv"), 
                path.join(directory, filename + " module_results.tsv"),  
                path.join(directory, filename + " gpa_trend.tsv"))

    raw_input("Done!")

