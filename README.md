# CHIdata
This project aims to batch process the data obtained from testing using the CHI electrochemical workstation, converting it into a format that can be directly pasted into Origin for plotting.

This script can select folders containing Chenhua workstation data for data processing

The data must be saved in .txt or .csv format, and .bin files cannot be processed directly.

Batch processing of data files is possible; after selecting a primary folder, all data in its secondary folders will be processed

After importing data, select the data type (e.g., select CA for chronoamperometry) and multiple folders can be processed simultaneously

After selection is complete, click 'Finish Selection' to start processing and plotting. When multiple folders are imported simultaneously, only the image from the last imported folder will be displayed.

Data is stored in the selected folder in the format of data type_merged.txt. For example, the saved file for CA data is CA_merged.txt

DRT_all can perform DRT analysis and processing on EIS data from various electrochemical workstations, and its implementation is based on the hybdrt library https://github.com/jdhuang-csm/hybrid-drt
