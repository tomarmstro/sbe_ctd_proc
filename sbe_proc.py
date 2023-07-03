"""
SBE CTD Data Processor
Author: Thomas Armstrong
Australian Institute of Marine Science
"""

#Imports
import SBE
import os
from datetime import datetime
from tkinter import filedialog
from tkinter import *

# package = customtkinter
import pip
try:
  import customtkinter
except:
  pip.main(['install', 'customtkinter'])
  # !pip install customtkinter
  import customtkinter
# import customtkinter

#config
raw_path = r"C:\Users\tarmstro\Python\sbe_ctd_proc\raw"
processed_path = r"C:\Users\tarmstro\Python\sbe_ctd_proc\processed"
config_path = r"C:\Users\tarmstro\Python\sbe_ctd_proc\config"
#Set whether the program designates latitude for the Derive module (1 for yes, 0 for no)
set_derive_latitude = 1

# CTD IDs
CTD_list = ['0597', '0890', '1009', '1233', '4409', '4525', '6180', '6390', '7053', '7360', '7816']

# Process .hex file (dat_cnv)
def process_hex(file_name, sbe):
    #run the data conversion processing
    with open(os.path.join(raw_path, file_name + '.hex'), "r", encoding='utf-8') as file:
        cnvfile = sbe.dat_cnv(file.read())
        try:
            with open(os.path.join(processed_path, file_name + 'C' + '.cnv'), "w") as file:
                file.write(cnvfile)
            print("HEX file converted successfully!")
        except IOError:
            print("Error while converting the CNV file!")

# All other processing steps
def process_step(file_name, processing_step, target_file_ext, result_file_ext, output_msg, error_msg):
    # run processing
    with open(os.path.join(processed_path, file_name + target_file_ext + '.cnv'), "r", encoding='utf-8') as read_file:
        print("File being processed: ", file_name)
        cnvfile = processing_step(read_file.read())
        try:
            with open(os.path.join(processed_path, file_name + result_file_ext + '.cnv'), "w") as write_file:
                write_file.write(cnvfile)
                print(output_msg)
        except IOError:
            print(error_msg)

#run processing
def process_cnv(file_name, sbe):
    process_step(file_name, sbe.filter, 'C', 'CF', "CNV file filtered successfully!", "Error while filtering the CNV file!")
    process_step(file_name, sbe.align_ctd, 'CF', 'CFA', "CNV file aligned filtered successfully!", "Error while aligning the CNV file!")
    process_step(file_name, sbe.loop_edit, 'CFA', 'CFAL', "CNV file loop editing  successfully!", "Error while loop editing the CNV file!")
    process_step(file_name, sbe.derive, 'CFAL', 'CFALD', "CNV file derived successfully!", "Error while deriving the CNV file!")
    process_step(file_name, sbe.bin_avg, 'CFALD', 'CFALDB', "CNV file bin averaged successfully!", "Error while bin averaging the CNV file!")

# Main process loop
def process():
    for file in os.listdir(raw_path):
        #Get input for derive latitude
        if set_derive_latitude == 1:
            derive_latitude = customtkinter.CTkInputDialog(text="What is the latitude for: " + file + "?", title="Derive Latitude Input").get_input()
        else:
            derive_latitude = ""
        ctd_id = ""
        if file.endswith(".hex"):
            # find ctd id for the cast
            print("Processing file: ", file)
            base_file_name = os.path.splitext(file)[0]
            with open(os.path.join(raw_path, base_file_name + '.hex'), "r", encoding='utf-8') as file_name:
                print("file name: ", file_name)
                for line in file_name:
                    if 'Temperature SN =' in line:
                        ctd_id = line[-5:].strip()
                    #Livewire ctds have different temperature IDs - Adjust them here
                    if ctd_id == '5165':
                        ctd_id = '1233'
                    if ctd_id == '4851':
                        ctd_id = '0890'
                    if 'cast' in line:
                        cast_date = datetime.strptime(line[11:22], "%d %b %Y")
                    if 'NMEA UTC (Time) =' in line:
                        cast_date = datetime.strptime(line[20:31], "%b %d %Y")
                if ctd_id == "":
                    print("No serial number found!")
            if ctd_id in CTD_list:
                print("CTD ID: ", ctd_id)
            else:
                break
            # get config subdirs for the relevant ctd by date
            # subfolders = [f.path for f in os.scandir(os.path.join(r"C:\Users\tarmstro\Python\sbe_ctd_proc\config", ctd_id)) if f.is_dir()]
            subfolders = [f.path for f in os.scandir(os.path.join(config_path, ctd_id)) if f.is_dir()]

            found_config = 0
            for folder in subfolders:
                folder_date = datetime.strptime(folder[-8:], "%Y%m%d")
                # find date range our cast fits into
                if folder_date < cast_date:
                    temp_folder = folder
                else:
                    config_folder = temp_folder
                    break
                if found_config == 0:
                    config_folder = folder

            print("Configuration Folder: ", config_folder)
            for file in os.listdir(config_folder):
                if file.endswith(".xmlcon"):
                    print("Configuration File: ", file)
                    xmlcon_file = file
            cwd = os.path.dirname(__file__)

            #Remove name appends and enter latitude
            #psa files for AIMS modules
            psa_files = ['Filter.psa', 'AlignCTD.psa', 'LoopEditIMOS.psa', 'DeriveIMOS.psa', 'BinAvgIMOS.psa']
            for psa_file in psa_files:
                #open psa file and store all lines
                with open(os.path.join(cwd, config_folder, psa_file), 'r') as f:
                    get_all = f.readlines()
                try:
                    #open new psa file and rewrite, changing lines if NameAppend or Latitude are found
                    with open(os.path.join(cwd, config_folder, psa_file), 'w') as f:
                        for i, line in enumerate(get_all, 0):  ## STARTS THE NUMBERING FROM 1 (by default it begins with 0)
                        # for line in get_all:
                            if '  <NameAppend value=\"' in line:
                                f.writelines('  <NameAppend value="" />\n')
                            elif '    <Latitude value=' in line:
                                f.writelines('    <Latitude value=\"' + derive_latitude + '\" />\n')
                                print("Psa latitude changed!")
                            else:
                                f.writelines(line)
                except TypeError:
                    with open(os.path.join(cwd, config_folder, psa_file), 'w') as f:
                        for i, line in enumerate(get_all, 0):
                            f.writelines(line)

            # Create instance of SBE functions with config_path files
            sbe = SBE.SBE(
                bin=os.path.join(cwd, 'SBEDataProcessing-Win32'),  # default
                temp_path=os.path.join(cwd, 'raw'),  # default
                xmlcon=os.path.join(cwd, config_folder, xmlcon_file),

                # AIMS processing modules
                psa_dat_cnv=os.path.join(cwd, config_folder, 'DatCnv.psa'),
                psa_filter=os.path.join(cwd, config_folder, 'Filter.psa'),
                psa_align_ctd=os.path.join(cwd, config_folder, 'AlignCTD.psa'),
                psa_loop_edit=os.path.join(cwd, config_folder, 'LoopEditIMOS.psa'),
                psa_derive=os.path.join(cwd, config_folder, 'DeriveIMOS.psa'),
                psa_bin_avg=os.path.join(cwd, config_folder, 'BinAvgIMOS.psa'),

                # unused for AIMS processing
                # psa_cell_thermal_mass=os.path.join(cwd, 'psa', 'CellTM.psa'),
                # psa_dat_cnv=os.path.join(cwd, 'psa', 'DatCnv.psa'),
                # psa_derive_teos10=os.path.join(cwd, 'psa', 'DeriveTEOS_10.psa'),
                # psa_sea_plot=os.path.join(cwd, 'psa', 'SeaPlot.psa'),
                # psa_section=os.path.join(cwd, 'psa', 'Section.psa'),
                # psa_wild_edit=os.path.join(cwd, 'psa', 'WildEdit.psa')
            )
            #run DatCnv
            process_hex(base_file_name, sbe)
            #Run other AIMS modules
            process_cnv(base_file_name, sbe)

#Get the raw directory with button click (default assigned to local directory)
def select_raw_directory():
    print("Raw Directory Button clicked!")
    raw_directory_selected = filedialog.askdirectory()
    global raw_path
    # raw_path = r"C:\Users\tarmstro\Python\sbe_ctd_proc\raw"
    raw_path = raw_directory_selected
    raw_path_label.config(text=raw_path)

#Get the processed directory with button click (default assigned to local directory)
def select_processed_directory():
    print("Processed Directory Button clicked!")
    processed_directory_selected = filedialog.askdirectory()
    global processed_path
    # processed_path = r"C:\Users\tarmstro\Python\sbe_ctd_proc\processed"
    processed_path = processed_directory_selected
    processed_path_label.config(text=processed_path)

# Get the processed directory with button click (default assigned to local directory)
def select_config_directory():
    print("Configuration Directory Button clicked!")
    config_directory_selected = filedialog.askdirectory()
    global config_path
    # config_path = r"C:\Users\tarmstro\Python\sbe_ctd_proc\config"
    config_path = config_directory_selected
    config_path_label.config(text=config_path)


# Create a tkinter window
window = customtkinter.CTk()  # create CTk window like you do with the Tk window
window.geometry("350x350")
window.grid_columnconfigure(0, weight=1)
customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
# Set the window title
window.title("Seabird CTD Processor")

# raw directory button
raw_directory_button = customtkinter.CTkButton(window, text="Select Raw Directory", command=select_raw_directory).pack(pady=20)

raw_path_label = Label(window)
raw_path_label.config(text=raw_path)
raw_path_label.pack()

# processed directory button
processed_directory_button = customtkinter.CTkButton(window, text="Select Processed Directory", command=select_processed_directory).pack(pady=20)
processed_path_label = Label(window)
processed_path_label.config(text=processed_path)
processed_path_label.pack()

# processed directory button
config_directory_button = customtkinter.CTkButton(window, text="Select Configuration Directory", command=select_config_directory).pack(pady=20)
config_path_label = Label(window)
config_path_label.config(text=config_path)
config_path_label.pack()

# process button
process_button = customtkinter.CTkButton(window, text="Process", font=("Arial", 25), command=process).pack(pady=20)

# Start the tkinter event loop
window.mainloop()
