"""
This script creates a subset of "oit_subset_01.tsv" which will be called "oit_subset_02.tsv".
- it will contain courses from "oit_subset_01.tsv" that are not in the "in_leganto.csv" file.
"""

import json, logging, os, pprint, sys

## setup logging ----------------------------------------------------
LOG_PATH: str = os.environ['LGNT__LOG_PATH']
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )

## update sys.path for project imports  -----------------------------
PROJECT_CODE_DIR = os.environ['LGNT__PROJECT_CODE_DIR']
sys.path.append( PROJECT_CODE_DIR )
from lib.common.validate_oit_file import is_utf8_encoded, is_tab_separated
from instructor_check_flow import common as instructor_common

## grab env vars ----------------------------------------------------
CSV_OUTPUT_DIR_PATH: str = os.environ['LGNT__CSV_OUTPUT_DIR_PATH']
ALREADY_IN_LEGANTO_FILEPATH: str = os.environ['LGNT__ALREADY_IN_LEGANTO_FILEPATH']
# OIT_COURSE_LIST_PATH: str = os.environ['LGNT__COURSES_FILEPATH']
# TARGET_SEASON: str = os.environ['LGNT__SEASON']
# TARGET_YEAR: str = os.environ['LGNT__YEAR']
# LEGIT_SECTIONS: str = json.loads( os.environ['LGNT__LEGIT_SECTIONS_JSON'] )
# OIT_SUBSET_01_OUTPUT_PATH: str = '%s/oit_subset_01.tsv' % os.environ['LGNT__CSV_OUTPUT_DIR_PATH']
# log.debug( f'OIT_COURSE_LIST_PATH, ``{OIT_COURSE_LIST_PATH}``' )
# log.debug( f'TARGET_SEASON, ``{TARGET_SEASON}``' )
# log.debug( f'TARGET_YEAR, ``{TARGET_YEAR}``' )
# log.debug( f'LEGIT_SECTIONS, ``{LEGIT_SECTIONS}``' )
# log.debug( f'OIT_SUBSET_01_OUTPUT_PATH, ``{OIT_SUBSET_01_OUTPUT_PATH}``' )

## constants --------------------------------------------------------
OIT_SUBSET_01_SOURCE_PATH = f'{CSV_OUTPUT_DIR_PATH}/oit_subset_01.tsv'
OIT_SUBSET_02_OUTPUT_PATH = f'{CSV_OUTPUT_DIR_PATH}/oit_subset_02.tsv'

## controller -------------------------------------------------------

def main():
    """ Controller.
        Called by if __name__ == '__main__' """

    ## validate already-in-leganto file -----------------------------
    assert is_utf8_encoded(ALREADY_IN_LEGANTO_FILEPATH) == True
    assert is_tab_separated(ALREADY_IN_LEGANTO_FILEPATH) == True
    assert already_in_leganto_columuns_are_valid(ALREADY_IN_LEGANTO_FILEPATH) == True

    ## load oit-subset-01 file --------------------------------------
    lines = []
    with open( OIT_SUBSET_01_SOURCE_PATH, 'r' ) as f:
        lines = f.readlines()

    ## get heading and data lines -----------------------------------
    new_subset_lines = []
    heading_line = lines[0]
    new_subset_lines.append( heading_line )
    parts = heading_line.split( '\t' )
    parts = [ part.strip() for part in parts ]
    log.debug( f'parts, ``{pprint.pformat(parts)}``' )
    data_lines = lines[1:]

    ## get already-in-leganto lines ---------------------------------
    already_in_leganto_lines = []
    with open( ALREADY_IN_LEGANTO_FILEPATH, 'r' ) as f:
        for line in f:
            already_in_leganto_lines.append( line.lower().strip() )
        # already_in_leganto_lines = f.readlines()
    for i in range( 0, 5 ):
        log.debug( f'already_in_leganto_lines[{i}], ``{already_in_leganto_lines[i]}``' )

    # log.debug( f'data_lines, ``{pprint.pformat(data_lines)}``' )



#     data_lines = [

#  'brown.biol.0170.2023-fall.s01\tBiotechnology in Medicine\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '17115\t\t\t\t\t\t\t\t\t\t\t140172525\t\t\t\t\t\t\n',
#  'brown.biol.0190f.2023-fall.s01\tDarwinian Medicine\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16283\t\t\t\t\t\t\t\t\t\t\t010039980\t\t\t\t\t\t\n',
#  'brown.biol.0190p.2023-fall.s01\tPride/Prej Dev of Sci Theories\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16218\t\t\t\t\t\t\t\t\t\t\t010185769\t\t\t\t\t\t\n',
#  'brown.biol.0190r.2023-fall.s01\tPhage Hunters, Part I\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16191\t\t\t\t\t\t\t\t\t\t\t010047181\t\t\t\t\t\t\n',
#  'brown.biol.0200.2023-fall.s01\tFoundation of Living Systems\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16921\t\t\t\t\t\t\t\t\t\t\t010029289, 010025704, 010173242\t\t\t\t\t\t\n',
#  'brown.biol.0210.2023-fall.s01\tDiversity of Life\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16290\t\t\t\t\t\t\t\t\t\t\t010663200\t\t\t\t\t\t\n',
#  'brown.biol.0380.2023-fall.s01\tEco + Evo Infectious Disease\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16297\t\t\t\t\t\t\t\t\t\t\t010067136\t\t\t\t\t\t\n',
#  'brown.biol.0410.2023-fall.s01\tInvertebrate Zoology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16298\t\t\t\t\t\t\t\t\t\t\t002384032\t\t\t\t\t\t\n',
#  'brown.biol.0470.2023-fall.s01\tGenetics\tS01\tBIOL\tCOURSE_UNIT\t\t\t\t\t'
#  '06-09-2023\t21-12-2023\t0\t\t2023\t\t\t16219\t\t\t\t\t\t\t\t\t\t\t010025704, '
#  '010202963, 010171412, 020381960\t\t\t\t\t\t\n',
#  'brown.biol.0480.2023-fall.s01\tEvolutionary Biology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16300\t\t\t\t\t\t\t\t\t\t\t010028329\t\t\t\t\t\t\n',
#  'brown.biol.0530.2023-fall.s01\tPrinciples of Immunology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16196\t\t\t\t\t\t\t\t\t\t\t000809330\t\t\t\t\t\t\n',
#  'brown.biol.0940a.2023-fall.s01\tViral Epidemics\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16221\t\t\t\t\t\t\t\t\t\t\t010023221\t\t\t\t\t\t\n',
#  'brown.biol.0940d.2023-fall.s01\tRhode Island Flora:Local Plant\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '17392\t\t\t\t\t\t\t\t\t\t\t140129962\t\t\t\t\t\t\n',
#  'brown.biol.0946.2023-fall.s01\tResearch Design + Quantitative\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '17166\t\t\t\t\t\t\t\t\t\t\t140049000\t\t\t\t\t\t\n',
#  'brown.biol.0960.2023-fall.s01\tInd Study in Science Writing\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '12071\t\t\t\t\t\t\t\t\t\t\t010026147\t\t\t\t\t\t\n',
#  'brown.biol.1050.2023-fall.s01\tBiology of the Eukaryotic Cell\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16222\t\t\t\t\t\t\t\t\t\t\t010025369\t\t\t\t\t\t\n',
#  'brown.biol.1070.2023-fall.s01\tBiotechnology and Global Healt\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16596\t\t\t\t\t\t\t\t\t\t\t000822887\t\t\t\t\t\t\n',
#  'brown.biol.1090.2023-fall.s01\tPolymer Sci for Biomaterials\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16210\t\t\t\t\t\t\t\t\t\t\t010027138\t\t\t\t\t\t\n',
#  'brown.biol.1110.2023-fall.s01\tSignal Transduction\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '18196\t\t\t\t\t\t\t\t\t\t\t010301239\t\t\t\t\t\t\n',
#  'brown.biol.1140.2023-fall.s01\tTissue Engineering\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '18197\t\t\t\t\t\t\t\t\t\t\t010068735\t\t\t\t\t\t\n',
#  'brown.biol.1160.2023-fall.s01\tPrinciples Exercise Physiology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '17767\t\t\t\t\t\t\t\t\t\t\t010024823\t\t\t\t\t\t\n',
#  'brown.biol.1260.2023-fall.s01\tPhysiological Pharmacology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16226\t\t\t\t\t\t\t\t\t\t\t010027078\t\t\t\t\t\t\n',
#  'brown.biol.1270.2023-fall.s01\tAdvanced Biochemistry\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16228\t\t\t\t\t\t\t\t\t\t\t010676397, 140247671\t\t\t\t\t\t\n',
#  'brown.biol.1290.2023-fall.s01\tCancer Biology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16212\t\t\t\t\t\t\t\t\t\t\t010057865\t\t\t\t\t\t\n',
#  'brown.biol.1310.2023-fall.s01\tDevelopmental Biology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16923\t\t\t\t\t\t\t\t\t\t\t010029952\t\t\t\t\t\t\n',
#  'brown.biol.1430.2023-fall.s01\tFoundations Population Genetic\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16285\t\t\t\t\t\t\t\t\t\t\t010067136\t\t\t\t\t\t\n',
#  'brown.biol.1465.2023-fall.s01\tHuman Population Genomics\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16287\t\t\t\t\t\t\t\t\t\t\t140226055\t\t\t\t\t\t\n',
#  'brown.biol.1470.2023-fall.s01\tConservation Biology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '17800\t\t\t\t\t\t\t\t\t\t\t010272044\t\t\t\t\t\t\n',
#  'brown.biol.1520.2023-fall.s01\tInnate Immunity\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16205\t\t\t\t\t\t\t\t\t\t\t010115165\t\t\t\t\t\t\n',
#  'brown.biol.1560.2023-fall.s01\tVirology\tS01\tBIOL\tCOURSE_UNIT\t\t\t\t\t'
#  '06-09-2023\t21-12-2023\t0\t\t2023\t\t\t16206\t\t\t\t\t\t\t\t\t\t\t'
#  '140339009\t\t\t\t\t\t\n',
#  'brown.biol.1565.2023-fall.s01\tSurvey of Biomedical Informati\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16993\t\t\t\t\t\t\t\t\t\t\t140049966\t\t\t\t\t\t\n',
#  'brown.biol.1575.2023-fall.s01\tEval of Health Info Systems\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16216\t\t\t\t\t\t\t\t\t\t\t140184621\t\t\t\t\t\t\n',
#  'brown.biol.1950.2023-fall.s01\tDir Research/Independent Study\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '12077\t\t\t\t\t\t\t\t\t\t\t020272301\t\t\t\t\t\t\n',
#  'brown.biol.1970a.2023-fall.s01\tStem Cell Biology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16232\t\t\t\t\t\t\t\t\t\t\t010156824, 020801040\t\t\t\t\t\t\n',
#  'brown.biol.2010a.2023-fall.s01\tIntroduction to Molecular Rese\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16233\t\t\t\t\t\t\t\t\t\t\t010027582\t\t\t\t\t\t\n',
#  'brown.biol.2020.2023-fall.s01\tBiotech Science and Industry\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '17210\t\t\t\t\t\t\t\t\t\t\t002293515\t\t\t\t\t\t\n',
#  'brown.biol.2030.2023-fall.s01\tFound Adv Study Life Science\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16234\t\t\t\t\t\t\t\t\t\t\t010034371, 010171363\t\t\t\t\t\t\n',
#  'brown.biol.2050.2023-fall.s01\tBiology of the Eukaryotic Cell\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16224\t\t\t\t\t\t\t\t\t\t\t010025369\t\t\t\t\t\t\n',
#  'brown.biol.2075.2023-fall.s01\tEvaluation of Health Informati\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16217\t\t\t\t\t\t\t\t\t\t\t140184621\t\t\t\t\t\t\n',
#  'brown.biol.2089.2023-fall.s01\tBiotechnology IP\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16597\t\t\t\t\t\t\t\t\t\t\t010134775, 140123325\t\t\t\t\t\t\n',
#  'brown.biol.2150.2023-fall.s01\tScientific Communication\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16235\t\t\t\t\t\t\t\t\t\t\t010202963, 140304922\t\t\t\t\t\t\n',
#  'brown.biol.2180.2023-fall.s01\tExperiential Learning Industry\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16598\t\t\t\t\t\t\t\t\t\t\t000822887\t\t\t\t\t\t\n',
#  'brown.biol.2230.2023-fall.s01\tBiomed Eng and Biotech Seminar\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16214\t\t\t\t\t\t\t\t\t\t\t010068735, 010371084\t\t\t\t\t\t\n',
#  'brown.biol.2260.2023-fall.s01\tPhysiological Pharmacology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16922\t\t\t\t\t\t\t\t\t\t\t010027078\t\t\t\t\t\t\n',
#  'brown.biol.2270.2023-fall.s01\tAdvanced Biochemistry\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16229\t\t\t\t\t\t\t\t\t\t\t010676397, 140247671\t\t\t\t\t\t\n',
#  'brown.biol.2310.2023-fall.s01\tDevelopmental Biology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16925\t\t\t\t\t\t\t\t\t\t\t010029952\t\t\t\t\t\t\n',
#  'brown.biol.2560.2023-fall.s01\tAdvanced Virology\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16207\t\t\t\t\t\t\t\t\t\t\t140339009\t\t\t\t\t\t\n',
#  'brown.biol.2860.2023-fall.s01\tMoleculr Mechanisms of Disease\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '16215\t\t\t\t\t\t\t\t\t\t\t010594128\t\t\t\t\t\t\n',
#  'brown.biol.2980.2023-fall.s01\tGraduate Independent Study\tS01\tBIOL\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '12470\t\t\t\t\t\t\t\t\t\t\t020662886\t\t\t\t\t\t\n',
#  'brown.biol.3001.2023-fall.s01\tClerkship in Medicine\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10001\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3005.2023-fall.s01\tClerkship in Medicine - LIC\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10003\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3060.2023-fall.s01\tGastroenterology\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10024\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3640.2023-fall.s01\tDoctoring 1\tS01\tBIOM\tCOURSE_UNIT\t\t\t\t\t'
#  '01-08-2023\t15-12-2023\t0\t\t2023\t\t\t10250\t\t\t\t\t\t\t\t\t\t\t140124521, '
#  '140407759\t\t\t\t\t\t\n',
#  'brown.biol.3641.2023-fall.s01\tIntegrated Medical Sciences I\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10251\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3642.2023-fall.s01\tScientific Foundations of Med\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10252\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3643.2023-fall.s01\tHistology\tS01\tBIOM\tCOURSE_UNIT\t\t\t\t\t'
#  '01-08-2023\t15-12-2023\t0\t\t2023\t\t\t10253\t\t\t\t\t\t\t\t\t\t\t140124521, '
#  '140407759\t\t\t\t\t\t\n',
#  'brown.biol.3644.2023-fall.s01\tHuman Anatomy I\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10254\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3645.2023-fall.s01\tGeneral Pathology\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10256\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3654.2023-fall.s01\tEndocrine Sciences\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t07-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10257\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3656.2023-fall.s01\tHealth Systems Science\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10258\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3660.2023-fall.s01\tDoctoring 3\tS01\tBIOM\tCOURSE_UNIT\t\t\t\t\t'
#  '07-08-2023\t15-12-2023\t0\t\t2023\t\t\t10259\t\t\t\t\t\t\t\t\t\t\t140124521, '
#  '140407759\t\t\t\t\t\t\n',
#  'brown.biol.3661.2023-fall.s01\tIMS-3 Comprehensive\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t07-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10260\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3662.2023-fall.s01\tCardiovascular\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t07-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10261\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3663.2023-fall.s01\tPulmonary\tS01\tBIOM\tCOURSE_UNIT\t\t\t\t\t'
#  '07-08-2023\t15-12-2023\t0\t\t2023\t\t\t10262\t\t\t\t\t\t\t\t\t\t\t140124521, '
#  '140407759\t\t\t\t\t\t\n',
#  'brown.biol.3664.2023-fall.s01\tRenal\tS01\tBIOM\tCOURSE_UNIT\t\t\t\t\t'
#  '07-08-2023\t15-12-2023\t0\t\t2023\t\t\t10263\t\t\t\t\t\t\t\t\t\t\t140124521, '
#  '140407759\t\t\t\t\t\t\n',
#  'brown.biol.3665.2023-fall.s01\tSupporting Structures\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t07-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10264\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3666.2023-fall.s01\tIMS-3 Systemic Pathology\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t07-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10265\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3667.2023-fall.s01\tIMS-3 System-Based Pharmacolgy\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t07-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10266\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3674.2023-fall.s01\tHuman Reproduction\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t07-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10267\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3900.2023-fall.s01\tCore Clerkship in Surgery\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10300\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.3915.2023-fall.s01\tClerkship in Surgery - LIC\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10307\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.4500.2023-fall.s01\tCore Clerkship in Pediatrics\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10447\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.4515.2023-fall.s01\tClerkship in Pediatrics - LIC\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10452\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.4900.2023-fall.s01\tCore Clerkship in OB/Gyn\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10502\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.4915.2023-fall.s01\tClerkship in OB/Gyn - LIC\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10506\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5100.2023-fall.s01\tCore Clerkship in Psychiatry\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10541\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5300.2023-fall.s01\tClerkship Psych- Neuroscience\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10578\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5315.2023-fall.s01\tClerkship in Psychiatry\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10580\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5320.2023-fall.s01\tClerkship in Psychiatry - LIC\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10582\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5325.2023-fall.s01\tClerkship in Neurology\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10583\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5330.2023-fall.s01\tClerkship in Neurology - LIC\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10585\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5400.2023-fall.s01\tCore Clerkship in Comm Health\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10586\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5795.2023-fall.s01\tClrkshp in Family Medicine-LIC\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10618\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5800.2023-fall.s01\tCore Clerkship in Family Med\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t01-05-2023\t28-07-2023\t0\t\t2023\t\t\t'
#  '10619\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.5885.2023-fall.s01\tClinical Skills Clerkship\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t07-08-2023\t15-12-2023\t0\t\t2023\t\t\t'
#  '10641\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.7170.2023-fall.s01\tAcademic Scholar Program\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '12662\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',
#  'brown.biol.7171.2023-fall.s01\tAcademic Scholar Program\tS01\tBIOM\t'
#  'COURSE_UNIT\t\t\t\t\t06-09-2023\t21-12-2023\t0\t\t2023\t\t\t'
#  '12663\t\t\t\t\t\t\t\t\t\t\t140124521, 140407759\t\t\t\t\t\t\n',

#     ]

#     log.debug( f'len(data_lines), ``{len(data_lines)}``' )

    # 1/0

    ## make subset --------------------------------------------------
    for i, data_line in enumerate( data_lines ):
        course_code_dict = instructor_common.parse_course_code( data_line, i )
        match_try_1 = f'%s.%s' % ( course_code_dict['course_code_department'], course_code_dict['course_code_number'] )
        match_try_2 = f'%s %s' % ( course_code_dict['course_code_department'], course_code_dict['course_code_number'] )
        # log.debug( f'processing data_line, ``{data_line}``' )
        # log.debug( f'match_try_1, ``{match_try_1}``' )
        # log.debug( f'match_try_2, ``{match_try_2}``' )
        ## check if course is already in leganto --------------------
        match_found = False
        for leganto_line in already_in_leganto_lines:
            # log.debug( f'checking leganto_line, ``{leganto_line}`` on match_tries ``{match_try_1}`` and ``{match_try_2}``' )
            if match_try_1 in leganto_line:
                log.debug( f'found match on ``{match_try_1}`` for leganto_line, ``{leganto_line}``' )
                match_found = True
                break
            elif match_try_2 in leganto_line:
                log.debug( f'found match on ``{match_try_2}`` for leganto_line, ``{leganto_line}``' )
                match_found = True
                break
        if match_found == False:
            new_subset_lines.append( data_line )
    # log.debug( f'new_subset_lines, ``{pprint.pformat(new_subset_lines)}``' )
    log.debug( f'len(original subset lines), ``{len(lines)}``' )
    log.debug( f'len(new_subset_lines), ``{len(new_subset_lines)}``' )

    ## end def main() 



    1/0


    # ## make subset --------------------------------------
    # skipped_due_to_no_instructor = []
    # skipped_sections = []
    # subset_lines = []
    # for i, data_line in enumerate( data_lines ):
    #     data_ok = False
    #     if i < 5:
    #         log.debug( f'processing data_line, ``{data_line}``' )
    #     line_dict = parse_line( data_line, heading_line, i )
    #     course_code_dict = parse_course_code( data_line, i )
    #     if course_code_dict['course_code_year'] == TARGET_YEAR:
    #         log.debug( 'passed year check' )
    #         if course_code_dict['course_code_term'] == TARGET_SEASON:
    #             log.debug( 'passed season check' )
    #             if course_code_dict['course_code_section'] in LEGIT_SECTIONS:
    #                 log.debug( 'passed section check' )
    #                 data_ok = True
    #             else:
    #                 skipped_sections.append( course_code_dict['course_code_section'] )
    #             if data_ok == True and len( line_dict['ALL_INSTRUCTORS'].strip() ) > 0:
    #                 log.debug( 'passed instructor check' )
    #                 subset_lines.append( data_line )
    #                 log.debug( 'added to subset_lines' )
    #             else:
    #                 log.debug( 'skipped due to no instructor' )
    #                 skipped_due_to_no_instructor.append( data_line )
    # # log.debug( f'subset_lines, ``{pprint.pformat(subset_lines)}``' )
    # # log.debug( f'len(subset_lines), ``{len(subset_lines)}``' )
    # # log.debug( f'skipped_due_to_no_instructor, ``{pprint.pformat(skipped_due_to_no_instructor)}``' )
    # # log.debug( f'len(skipped_due_to_no_instructor), ``{len(skipped_due_to_no_instructor)}``' )

    # ## populate course-parts buckets --------------------------------
    # buckets_dict: dict  = make_buckets()  # returns dict like: ```( course_code_institutions': {'all_values': [], 'unique_values': []}, etc... }```
    # for i, summer_line in enumerate( subset_lines ):
    #     if i < 5:
    #         log.debug( f'processing summer-line, ``{summer_line}``' )
    #     course_code_dict = parse_course_code( summer_line, i )
    #     buckets_dict: dict = populate_buckets( course_code_dict, buckets_dict )
    # buckets_dict['skipped_sections_for_target_year_and_season']['all_values'] = skipped_sections
    # # log.debug( f'buckets_dict, ``{pprint.pformat(buckets_dict)}``' )

    # ## prepare bucket counts ----------------------------------------
    # buckets_dict: dict = add_counts( buckets_dict )
    # log.debug( f'updated_buckets_dict, ``{pprint.pformat(buckets_dict)}``' )

    # ## prep easyview output -----------------------------------------
    # # easyview_output = make_easyview_output( buckets_dict )
    # easyview_output = make_easyview_output( buckets_dict, skipped_due_to_no_instructor )
    # log.debug( f'easyview_output, ``{pprint.pformat(easyview_output)}``' )

    # ## write summer-2023 subset to file -----------------------------
    # with open( OIT_SUBSET_01_OUTPUT_PATH, 'w' ) as f:
    #     f.write( heading_line )
    #     for line in subset_lines:
    #         f.write( line )
        
    ## end main()


## helper functions -------------------------------------------------


def already_in_leganto_columuns_are_valid( filepath: str ) -> bool:
    """ Ensures tsv file is as expected.
        Called by main() """
    check_result = False
    line = ''
    with open( filepath, 'r' ) as f:
        line = f.readline()
    parts = line.split( '\t' )
    stripped_parts = [ part.strip() for part in parts ]
    if stripped_parts == [
        'Course ID',
        'Course Instructor',
        'Number Of Citations',
        'Course Section',
        'Course Name',
        'Current Course Start Date',
        'Reading List Code',
        'Course Modification Date',
        'Reading List Name',
        'Course Instructor Primary Identifier'    
        ]:
        check_result = True
    # log.debug( f'parts, ``{pprint.pformat(parts)}``' )
    log.debug( f'check_result, ``{check_result}``' )
    return check_result




if __name__ == '__main__':
    main()
    sys.exit(0)




# def make_easyview_output( buckets_dict: dict, skipped_due_to_no_instructor: list ) -> dict:
#     """ Prepares easyview output.
#         Called by main() """
#     assert type(buckets_dict) == dict
#     output_dict = {}
#     for key in buckets_dict.keys():
#         unsorted_unique_values = buckets_dict[key]['unique_values']
#         # sorted_unique_values = sorted( unsorted_unique_values, key=lambda x: x[1], reverse=True )
#         ## sort by count and then by string
#         # sorted_unique_values = sorted( unsorted_unique_values, key=lambda x: (x[1], x[0]), reverse=True )
#         ## sort by count-descending, and then by string-ascending
#         sorted_unique_values = sorted( unsorted_unique_values, key=lambda x: (-x[1], x[0]) )        
#         output_dict[key] = sorted_unique_values
#     output_dict['skipped_instructor_count_for_target_year_and_season_and_section'] = len( skipped_due_to_no_instructor )
#     # jsn = json.dumps( output_dict, indent=2 )
#     # with open( './output.json', 'w' ) as f:
#     #     f.write( jsn )
#     return output_dict


# def add_counts( buckets_dict: dict ) -> dict:
#     """ Updates 'unique_set': {'count': 0, 'unique_values': []} """
#     assert type(buckets_dict) == dict
#     for key in buckets_dict.keys():
#         log.debug( f'key, ``{key}``' ) 
#         unique_values_from_set = list( set( buckets_dict[key]['all_values'] ) )
#         unique_tuple_list = [ (value, buckets_dict[key]['all_values'].count(value)) for value in unique_values_from_set ]
#         log.debug( f'unique_tuple_list, ``{unique_tuple_list}``' )
#         buckets_dict[key]['unique_values'] = unique_tuple_list
#     # log.debug( f'buckets_dict, ``{pprint.pformat(buckets_dict)}``' )
#     return buckets_dict


# def populate_buckets( course_code_dict: dict, buckets_dict: dict ) -> dict:
#     """ Populates buckets. """
#     assert type(course_code_dict) == dict
#     assert type(buckets_dict) == dict
#     for key in course_code_dict.keys():
#         if key == 'course_code_institution':
#             buckets_dict['subset_institutions']['all_values'].append( course_code_dict[key] )
#         elif key == 'course_code_department':
#             buckets_dict['subset_departments']['all_values'].append( course_code_dict[key] )
#         elif key == 'course_code_year':
#             buckets_dict['subset_years']['all_values'].append( course_code_dict[key] )
#         elif key == 'course_code_term':
#             buckets_dict['subset_terms']['all_values'].append( course_code_dict[key] )
#         elif key == 'course_code_section':
#             buckets_dict['subset_sections']['all_values'].append( course_code_dict[key] )
#     return buckets_dict


# def make_buckets() -> dict:
#     """ Returns dict of buckets. """
#     buckets_dict = {
#         'subset_institutions': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'subset_departments': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'subset_years': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'subset_terms': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'subset_sections': { 
#             'all_values': [], 
#             'unique_values': [] },
#         'skipped_sections_for_target_year_and_season': { 
#             'all_values': [], 
#             'unique_values': [] },
#         }
#     log.debug( f'initialized buckets_dict, ``{pprint.pformat(buckets_dict)}``' )
#     return buckets_dict


