TEST_NAME="shape-param"

export ROOT_LOCATION="$(pwd)"

ASTE_LOCATION="${ROOT_LOCATION}/../aste" # CHANGE DEPENDING ON ASTE INSTALLATION
CONFIG_FILE="config-franke"

RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}/testcase"
MAPPING_TESTER="${ASTE_LOCATION}/tools/mapping-tester"
ASTE_BUILD="${ASTE_LOCATION}/build"
export PATH=$ASTE_BUILD:$PATH

rm -rf "${TEST_LOCATION}"
mkdir -p "${TEST_LOCATION}"

echo ""
echo "[TEST] generate.py"
echo ""

python3 "${MAPPING_TESTER}"/generate.py --setup "${RUN_LOCATION}/${CONFIG_FILE}.json" --outdir "${TEST_LOCATION}" --template "${MAPPING_TESTER}"/config-template.xml --exit

echo ""
echo "[TEST] preparemeshes.py"
echo ""

python3 "${MAPPING_TESTER}"/preparemeshes.py --setup "${RUN_LOCATION}/${CONFIG_FILE}.json" --outdir "${TEST_LOCATION}"

echo ""
echo "[TEST] runall.sh"
echo ""

cd "${TEST_LOCATION}"
bash ./runall.sh

echo ""
echo "[TEST] preparemeshes.py"
echo ""

bash ./postprocessall.sh

echo ""
echo "[TEST] gatherstats.py"
echo ""

mkdir -p "${RUN_LOCATION}/data"
cd "${RUN_LOCATION}/data"

python3 "${MAPPING_TESTER}"/gatherstats.py --outdir "${TEST_LOCATION}" --file statistics.csv
python3 ../../gather_greedy_stats.py --outdir "${TEST_LOCATION}" --file greedy_values.csv