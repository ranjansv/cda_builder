import cPickle as pickle
import os
class Patient:

        def load_patient(self,filepath):
		print "Hey I am loading the patient.pkl file instead of blank..."
		print os.getcwd()
		print os.getcwd().split('/')
		self.__dict__ = pickle.load(file(filepath,'r+b'))
		print "***********************************************"
	def save_patient(self,location,filename):
		pickle.dump(self.__dict__, file(str(location)+str(filename)+'.pkl','wb'))
		print "Saving " + str(self.given_name) + " at location: " + str(location) + " to file: " + str(filename)

