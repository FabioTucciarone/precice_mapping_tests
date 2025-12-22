# set -e 

TEST_NAME="radius"

export ROOT_LOCATION="$(pwd)"

ASTE_LOCATION="${ROOT_LOCATION}/../aste" # CHANGE DEPENDING ON ASTE INSTALLATION

RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}/testcase"
MAPPING_TESTER="${ASTE_LOCATION}/tools/mapping-tester"
ASTE_BUILD="${ASTE_LOCATION}/build"
export PATH=$ASTE_BUILD:$PATH


rm    -rf "${TEST_LOCATION}_cos"
mkdir -p  "${TEST_LOCATION}_cos"

# TODO: mkdir für cos und franke3d

cd "${RUN_LOCATION}"
python3 "${MAPPING_TESTER}"/generate.py      --setup "${RUN_LOCATION}"/config-cos.json --outdir "${TEST_LOCATION}_cos" --template "${MAPPING_TESTER}"/config-template.xml --exit
python3 "${MAPPING_TESTER}"/preparemeshes.py --setup "${RUN_LOCATION}"/config-cos.json --outdir "${TEST_LOCATION}_cos"

cd "${TEST_LOCATION}_cos"
bash ./runall.sh
bash ./postprocessall.sh

python3 "${MAPPING_TESTER}"/gatherstats.py              --outdir "${TEST_LOCATION}_cos" --file "${RUN_LOCATION}/data/cos/statistics.csv"
python3 "${RUN_LOCATION}/../gather_additional_stats.py" --outdir "${TEST_LOCATION}_cos" --file "${RUN_LOCATION}/data/cos/additional.csv" --event_regex "map.rbf.(solveConservativeTest|condition)"


rm    -rf "${TEST_LOCATION}_franke3d" 
mkdir -p  "${TEST_LOCATION}_franke3d"

cd "${RUN_LOCATION}"
python3 "${MAPPING_TESTER}"/generate.py      --setup "${RUN_LOCATION}"/config-fanke3d.json --outdir "${TEST_LOCATION}_franke3d" --template "${MAPPING_TESTER}"/config-template.xml --exit
python3 "${MAPPING_TESTER}"/preparemeshes.py --setup "${RUN_LOCATION}"/config-fanke3d.json --outdir "${TEST_LOCATION}_franke3d"

cd "${TEST_LOCATION}_franke3d"
bash ./runall.sh
bash ./postprocessall.sh

python3 "${MAPPING_TESTER}"/gatherstats.py              --outdir "${TEST_LOCATION}_franke3d" --file "${RUN_LOCATION}/data/franke3d/statistics.csv"
python3 "${RUN_LOCATION}/../gather_additional_stats.py" --outdir "${TEST_LOCATION}_franke3d" --file "${RUN_LOCATION}/data/franke3d/additional.csv" --event_regex "map.rbf.(solveConservativeTest|condition)"


cd "${RUN_LOCATION}"