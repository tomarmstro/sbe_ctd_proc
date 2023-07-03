# sbe_ctd_proc
 Seabird CTD Processor

Batch processing for Seabird CTD Data Processing.
Automated calibration file and CTD selection to process all files in a directory easily.

This script will process all .hex files in a directory and ask for latitude for each file's derive step.

Ensure all relevant calibration .xmlcon and .psa files are in the following config directory structure:
- config ->
   - ctd_id1
   - ctd_id2 ->
      -  calibration_files_20120131
      -  calibration_files_20170601 ->
         -   20170601.xmlcon
         -   AlignCTD.psa
         -   BinAvgIMOS.psa
         -   DatCnv.psa
         -   DeriveIMOS.psa
         -   Filter.psa
         -   LoopEditIMOS.psa


        
