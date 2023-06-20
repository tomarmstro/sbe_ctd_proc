# sbe_ctd_proc
 Seabird CTD Processor

Batch processing for automated running of Seabird Data Processing for CTDs
Automated calibration file and ctd selection to process all files in a directory easily.

Config directory setup:
config ->
    ctd_id1
    ctd_id2 ->
        calibration_files_20120131
        calibration_files_20170601 ->
            20170601.xmlcon
            AlignCTD.psa
            BinAvgIMOS.psa
            DatCnv.psa
            DeriveIMOS.psa
            Filter.psa
            LoopEditIMOS.psa


        
