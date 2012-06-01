
import os
import shutil
import sys
import re
import datetime
import filecmp

import patient



FM_DEBUG = False


# FileManager -
#     Creates and manages the directory where patient files are stored
#     and retrieved.
class FileManager:


    def __init__ (self):
        # valid file extensions and their directory names
        self._file_ext_dict = {'.img':'/images/', '.pkl':'/pickles/', 
                               '.fingerprint':'/fingerprints/',
                               '.csv':'/CSV/', '.xml':'/xmls/'}
        

    ################# Public Method Attributes #######################

    
    ######################## Accessors ###############################


    # Returns the the current clinic's directory.
    # Returns False if create_clinic_dir () has not yet been called.
    def get_clinic_dir (self):

        if self._clinic_path == '':
            self._file_mgr_error ('get_clinic_dir',
                                  'clinic directory not yet created')
            return False

        return self._clinic_path


    ######################## Mutators ################################


    # create_clinic_directory -
    #     Creates the directory structure for a clinic instance
    #     with the clinic directory and the patient data directories
    #     below it. This will be invoked one time on every workstation 
    #     that makes up a clinic. A clinic directory must be set up with
    #     this function before any of the other public method attributes
    #     can be called.
    # Arguments:
    #     clinic_name - A string containing the name of the clinic.
    #     root_dir - A string containing the name of the directory in 
    #         which the new clinic directory will be saved.
    # Returns: 
    #     - True for success, False for failure
    def create_clinic_dir (self, clinic_name, root_dir):

        if self._clinic_path != '':
            self._file_mgr_error ('create_clinic_dir',
                                  'create_clinic_dir () already called')
            return False

        clinic_dir = os.path.abspath (root_dir) + '/' + clinic_name

        if (FM_DEBUG): print "clinic_dir = ", clinic_dir

        if os.path.exists (clinic_dir):
            self._file_mgr_error ('create_clinic_dir',
                          'the path ' + clinic_dir + ' already exists')
            return False

        self._clinic_path = clinic_dir

        # make subdirectories
        os.makedirs (self._clinic_path + '/clinic_config')
        os.makedirs (self._clinic_path + '/patients')
        for directory in self._file_ext_dict.values ():
            os.makedirs (self._clinic_path + '/patients' + directory)

        return True



    # save_patient_files -
    #     Save a patient file(s) to the directory with the appropriate 
    #     name (could be pkl, img, xml, csv, or fingerprint file). Files
    #     with extentions other than .pkl, .img, .xml, .csv, or 
    #     .fingerprint will not be saved. If save_patient_files is 
    #     called for files which are already in the clinic directory, a 
    #     duplicate will be saved under a different name.
    # Arguments:
    #     patient_object - a patient object containing the fields 
    #         "UUID", "family_name", "given_name", and "date". "UUID", 
    #         "family_name", and "given_name" are strings. "date" is of
    #         class datetime.datetime.
    #     files - 1 or more strings containing the names of files to be
    #         saved
    #     special_files - If a keyword argument 
    #         'profile_image=file_name' (where file_name is a string 
    #         containg a specified filename) is given, file_name will be
    #         saved as the profile image. If a profile image is already 
    #         saved, it will be overwritten.
    # Returns: 
    #     - An array containing the paths of the files that were 
    #       successfully saved.
    #     - False if create_clinic_dir () has not yet been called
    #     - False if an error occurred 
    def save_patient_files (self, patient_object, *files, 
                            **special_files):

        if self._clinic_path == '':
            self._file_mgr_error ('save_patient_files',
                                  'clinic directory not yet created')
            return False

        if not isinstance (patient_object, patient.patient):
            self._file_mgr_error ('save_patient_files',
                                  'patient_object is not valid')
            return False

        if (not 'id' in patient_object.__dict__.keys ()
            or not 'given_name' in patient_object.__dict__.keys ()
            or not 'family_name' in patient_object.__dict__.keys ()
            or not 'date' in patient_object.__dict__.keys ()):
            self._file_mgr_error ('save_patient_files',
                                  'patient_object does not contain ' +
                                  'the fields "id", "given_name", ' +
                                  '"family_name", or "date"')
            return False

        if not isinstance (patient_object.date, datetime.datetime):
            self._file_mgr_error ('save_patient_files',
                                  str (patient_object) + 
                                  ': date attribute is not of class ' +
                                  'datetime')
            return False

        # extract patient info
        UUID = patient_object.id 
        patient_name = (patient_object.family_name + '_' +
                        patient_object.given_name)
        time_stamp = patient_object.date.strftime ('%m-%d-%Y-%H-%M-%S')

        if not UUID and patient_name != '_' and time_stamp:
            self._file_mgr_error ('save_patient_files',
                            'patient_object fields not all initialized')
            return False

        new_filename = ''
        counter = 0
        file_ext = ''
        filenames = []

        # save profile image if specified
        if 'profile_image' in special_files.keys ():
            if not os.path.isfile (special_files['profile_image']):
                self._file_mgr_error ('save_patient_files', 
                                      special_files['profile_image'] + 
                                      ': file does not exist')

            elif (re.search (r'(\.[^.]*$)|($)', 
                   special_files['profile_image']).group (1) != '.img'):
                self._file_mgr_error ('save_patient_files', 
                                      special_files['profile_image'] + 
                                      ': invalid file extension')
            else:
                new_filename = (self._clinic_path + '/patients' +
                                self._file_ext_dict ['.img'] + 
                                patient_name + '_' + UUID + '_' + 
                                time_stamp + '_p.img')
                shutil.copyfile (special_files['profile_image'], 
                                 new_filename)
                filenames.append (new_filename)

        # save the rest of the files
        for old_filename in files:

            if not os.path.isfile (old_filename):
                self._file_mgr_error ('save_patient_files', 
                                 old_filename + ': file does not exist')
                continue
                
            file_ext = ( 
                re.search (r'(\.[^.]*$)|($)', old_filename).group (1))

            if (FM_DEBUG): print "file_ext = ", file_ext

            if (not file_ext or 
                not file_ext in self._file_ext_dict.keys ()):
                self._file_mgr_error ('save_patient_files', 
                             old_filename + ': invalid file extension')
                continue

            new_filename = (self._clinic_path + '/patients' +
                            self._file_ext_dict [file_ext] + 
                            patient_name + '_' + UUID + '_' + 
                            time_stamp + '_' + str (counter) + file_ext)
                
            # If the filename already exists, suffix the filename with
            # the first available integer.
            while os.path.exists (new_filename):
                new_filename = re.sub (str (counter) + file_ext + r'$',
                                       str (counter + 1) + file_ext, 
                                       new_filename)
                counter = counter + 1
            counter = 0

            shutil.copyfile (old_filename, new_filename)

            filenames.append (new_filename)

        return filenames


   
    # Note: This function doesn't work on Windows.
    # set_images_symlink -
    #     Creates a symbolic link to the images directory and places it
    #     in the specified directory static_images_dir. 
    # Argument:
    #     static_images_dir - a string containing the path to the 
    #         directory where the symlink will be saved. This will 
    #         probably be the path to '/static/images' 
    # Returns:
    #     - False if create_clinic_dir () has not yet been called
    #     - False if static_images_dir is not a directory
    def set_images_symlink (self, static_images_dir):

        if self._clinic_path == '':
            self._file_mgr_error ('create_images_symlink',
                                  'clinic directory not yet created')
            return False

        if not os.path.isdir (static_images_dir):
            self._file_mgr_error ('create_images_symlink',
                                  static_images_dir + 
                                  ' is not a directory')
            return False

        os.symlink (self._clinic_path + '/patients/images', 
                    static_images_dir + '/images_sym')

        return True

        

    # get_patient_files -
    #     Retrieves all patient files that are connected to the 
    #     specified UUID. 
    # Argument:
    #     UUID - a string containing a UUID
    # Returns:
    #     - An array containing all files for the patient with the 
    #       specified UUID
    #     - False if create_clinic_dir () has not yet been called
    def get_patient_files (self, UUID):

        if self._clinic_path == '':
            self._file_mgr_error ('get_patient_files',
                                  'clinic directory not yet created')
            return False

        patient_files = []

        # look through all directories for file names containing UUID
        for directory in self._file_ext_dict.values ():
            for filename in os.listdir (self._clinic_path + '/patients'
                                        + directory):
                if UUID in filename:
                    patient_files.append (self._clinic_path + 
                                          '/patients' + directory + 
                                          filename)

        return patient_files



    # get_patient_files2 -
    #     Retrieves all files of a certain type or from a certain visit.
    # Arguments:
    #     file_info - Accepts a list of keyword arguments. If the 
    #         keyword argument "day=a_day" is given, this function
    #         will search for all files corresponding to visits during
    #         the given day. 
    #             e.g. day='05'
    #         If the keyword argument "file_type=file_type" is
    #         given, where file_type is one of '.pkl', '.xml', 
    #         '.csv', '.fingerprint', or '.img', this function will
    #         search for all files with the given file extension.
    #         If multiple keyword arguments are given, this function
    #         will return the files which satisfy all of the
    #         specifications.
    # Returns:
    #     - A list of files which satisfy the specifications given
    #        in file_info
    #     - False if create_clinic_dir () has not yet been called
    def get_patient_files2 (self, **file_info):

        if self._clinic_path == '':
            self._file_mgr_error ('get_patient_files2',
                                  'clinic directory not yet created')
            return False

        day = ''
        file_type = ''
        meets_criteria = True
        files = []

        if 'day' in file_info.keys ():
            day = file_info['day']

        if 'file_type' in file_info.keys ():
            file_type = file_info['file_type']

        # look through all directories for files meeting the specified
        # criteria
        for directory in self._file_ext_dict.values ():
            for filename in os.listdir (self._clinic_path + '/patients'
                                        + directory):
                if file_type != '' and not file_type in filename:
                    meets_criteria = False
                if (day != '' and 
                    re.search (r'^[^-]+-(..)|()', filename).group (1) !=
                    day):
                    meets_criteria = False
                if meets_criteria:
                    files.append (filename)
                meets_criteria = True

        return files



    # Note: doesn't work on Windows
    # transfer_clinic_files -
    #     Copies files from this clinic's directory to the target 
    #     directory. This clinic's subdirectories are copied 
    #     recursively. This would be invoked if the exit station needed
    #     to be moved from one workstation to another. 
    # Arguments:
    #     target_directory - a string containing the name of the 
    #         directory to which all files should be transferred
    #     interactive - if this is set to True, the user is asked 
    #         whether or not files in the target directory that have the
    #         same name as files in the source directory should be 
    #         overwritten. This is set to True by default.
    # Returns:
    #     - False if create_clinic_dir () has not yet been called or if
    #       the target directory does not exist.
    #     - True for success
    def transfer_clinic_files (self, target_directory, 
                               interactive=True):

        if self._clinic_path == '':
            self._file_mgr_error ('transfer_clinic_files',
                                  'clinic directory not yet created')
            return False

        if not os.path.isdir (target_directory):
            self._file_mgr_error ('transfer_clinic_files',
                              target_directory + ' is not a directory')
            return False

        user_input = ''
        target_dirpath = ''

        for dirpath, dirnames, filenames in os.walk (self._clinic_path):
            
            if (FM_DEBUG): print dirpath, dirnames, filenames

            target_dirpath = re.sub (self._clinic_path, 
                                     target_directory, dirpath)
            if (FM_DEBUG): print 'target_dirpath = ', target_dirpath
           
            for dirname in dirnames:
                if not os.path.isdir (target_dirpath + '/' + dirname):
                    os.makedirs (target_dirpath + '/' + dirname)

            for filename in filenames:

                if (not os.path.isfile (target_dirpath + '/' + filename)
                    or interactive == False):
                    shutil.copyfile (dirpath + '/' + filename,
                                     target_dirpath + '/' + filename)

                else: # os.path.isfile (target_dirpath + '/' + filename):
                      # interactive == True:
                    self._file_mgr_warn ('transfer_clinic_files',
                        filename + ' has the same name as a file in ' +
                        'the target directory. The files contents ' +
                        'may be identical or entirely unrelated')
                    user_input = raw_input (('Overwrite ' + 
                                             target_dirpath + '/' + 
                                             filename + '?'))
                    if user_input.startswith ('y'):
                        shutil.copyfile (dirpath + '/' + filename,
                                        target_dirpath + '/' + filename)
                        print "File overwritten"
                    else:
                        print "File not overwritten"

        return True



    ################# private method attributes ######################


    # prints out an error message to stderr of the form:
    # "class_name: function_name: error_message"
    def _file_mgr_error (self, func_name, error_msg):
        print >> sys.stderr, ('Error: ' + __name__ + ': ' + func_name + 
                              ': ' + error_msg)

    # prints out a warning message to stderr of the form:
    # "class_name: function_name: warning_message"
    def _file_mgr_warn (self, func_name, warning_msg):
        print >> sys.stderr, ('Warning: ' + __name__ + ': ' + 
                              func_name + ': ' + warning_msg)

            

    ################### private data attributes ######################


    # the path to the clinic directory
    _clinic_path = ''

    # valid file extensions and their directory names
    _file_ext_dict = {} 

































