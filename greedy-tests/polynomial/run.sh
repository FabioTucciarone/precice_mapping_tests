TEST_NAME="polynomial"

export ROOT_LOCATION="$(pwd)"

ASTE_PATH="${ROOT_LOCATION}/../aste" # CHANGE DEPENDING ON ASTE INSTALLATION

RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}/testcase"
MAPPING_TESTER="${ASTE_PATH}/tools/mapping-tester"
ASTE_BUILD="${ASTE_PATH}/build"
export PATH=$ASTE_BUILD:$PATH

export GRID_DISTANCE="0.01"
export CONVERGENCE_CRITERION="1e-3"

rm -rf $TEST_LOCATION
mkdir -p $TEST_LOCATION

echo ""
echo "[TEST] generate.py"
echo ""

python3 "${MAPPING_TESTER}/generate.py" --setup "${RUN_LOCATION}/config-franke.json"    --outdir "${TEST_LOCATION}/franke"    --template "${MAPPING_TESTER}"/config-template.xml --exit
python3 "${MAPPING_TESTER}/generate.py" --setup "${RUN_LOCATION}/config-eggholder.json" --outdir "${TEST_LOCATION}/eggholder" --template "${MAPPING_TESTER}"/config-template.xml --exit

echo ""
echo "[TEST] preparemeshes.py"
echo ""

python3 "${MAPPING_TESTER}/preparemeshes.py" --setup "${RUN_LOCATION}/config-franke.json"    --outdir "${TEST_LOCATION}/franke"
python3 "${MAPPING_TESTER}/preparemeshes.py" --setup "${RUN_LOCATION}/config-eggholder.json" --outdir "${TEST_LOCATION}/eggholder"

echo ""
echo "[TEST] runall.sh / postprocessall.sh"
echo ""

cd "${TEST_LOCATION}/franke"
bash ./runall.sh
bash ./postprocessall.sh
cd "${TEST_LOCATION}/eggholder"
bash ./runall.sh
bash ./postprocessall.sh

echo ""
echo "[TEST] gatherstats.py"
echo ""

cd "${RUN_LOCATION}/data"
python3 "${MAPPING_TESTER}/gatherstats.py" --outdir "${TEST_LOCATION}/franke" --file statistics_franke.csv
python3 ../../gather_greedy_stats.py       --outdir "${TEST_LOCATION}/franke" --file greedy_values_franke.csv
python3 "${MAPPING_TESTER}/gatherstats.py" --outdir "${TEST_LOCATION}/eggholder" --file statistics_eggholder.csv
python3 ../../gather_greedy_stats.py       --outdir "${TEST_LOCATION}/eggholder" --file greedy_values_eggholder.csv

cd $RUN_LOCATION