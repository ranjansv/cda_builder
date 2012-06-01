
# Creates a clinic, saves patient files and then retrieves all .pkl 
# files from a particular day.

from django.shortcuts import render_to_response
import file_manager
import datetime
import cPickle as pickle
import os
import sys
import pr

def create_clinic():
  os.system("rm -f -R ./my_clinic3")
  os.system("rm gen_report.csv")
  fm = file_manager.FileManager ()
  fm.create_clinic_dir ('my_clinic3', '.')
  os.system("cp ./*.pkl ./my_clinic3/patients/pickles/")


def return_attribute_list(request):
   list_attribute=[]
   obj=pr.Patient()
   #Since I do not have an file_manager handle for the my_clinic3 clinic I am directly accessing a sample pickle file
   obj.load_patient('./bill_clinton_12345_05-29-2012-07-17-06_0.pkl')
   for key,value in obj.__dict__.items():
       list_attribute.append(str(key))
   return render_to_response("reporting.html",locals())

def generate_csv(request):
    attribute_list=[]
    dina=request.POST.__getitem__('day')
    print dina
    hesaru=request.POST.getlist('name_of_attribute')
    print hesaru 
    
    for gothrgh in hesaru:
       attribute_list.append(str(gothrgh))
    print attribute_list
    fm = file_manager.FileManager ()
    os.system("rm -f -R ./my_clinic3")
    fm.create_clinic_dir ('my_clinic3', '.')
    os.system("cp ./*.pkl ./my_clinic3/patients/pickles/")
    os.system("cp ./*.csv ./my_clinic3/patients/CSV/")
    files = fm.get_patient_files2 (day=str(dina),file_type='.pkl')
    now = datetime.datetime.now()

    csv=open('./my_clinic3/patients/CSV/'+str(now.month)+'_'+str(now.day)+'_'+str(now.year)+'_'+str(now.hour)+'_'+str(now.minute)+str(now.second)+'.csv','w')

    for attri in attribute_list:
       convert_string=str(attri)
       csv.write(convert_string)
       csv.write(',')
    csv.write('\n')

    for filename in files:
       obj=pr.Patient()
       obj.load_patient('./my_clinic3/patients/pickles/'+filename)
       for key,value in obj.__dict__.items():
          if key in attribute_list:
            convert_string=str(value)
            csv.write(convert_string)
            csv.write(',')
       csv.write('\n')
    os.system("cp ./my_clinic3/patients/CSV/* .")
    return render_to_response("generate_csv.html",locals())
