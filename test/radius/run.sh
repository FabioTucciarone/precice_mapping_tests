# set -e 

TEST_NAME="radius"

export ROOT_LOCATION="$(pwd)"

ASTE_LOCATION="${ROOT_LOCATION}/../aste" # CHANGE DEPENDING ON ASTE INSTALLATION

RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}/testcase"
MAPPING_TESTER="${ASTE_LOCATION}/tools/mapping-tester"
ASTE_BUILD="${ASTE_LOCATION}/build"
export PATH=$ASTE_BUILD:$PATH

rm -rf "${TEST_LOCATION}"
mkdir -p "${TEST_LOCATION}"

python3 "${MAPPING_TESTER}"/generate.py --setup "${RUN_LOCATION}"/config-fanke3d.json --outdir "${TEST_LOCATION}" --template "${MAPPING_TESTER}"/config-template.xml --exit
python3 "${MAPPING_TESTER}"/preparemeshes.py --setup "${RUN_LOCATION}"/config-fanke3d.json --outdir "${TEST_LOCATION}"

cd "${TEST_LOCATION}"

bash ./runall.sh
bash ./postprocessall.sh
python3 "${MAPPING_TESTER}"/gatherstats.py --outdir "${RUN_LOCATION}" --file statistics.csv

cd "${RUN_LOCATION}"

python3 show.py testcase/statistics.csv