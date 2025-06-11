set -e

TEST_NAME="performance"

export ROOT_LOCATION="$(pwd)"
RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}/testcase"
ASTE_SRC="${ROOT_LOCATION}/../aste/src"
ASTE_BUILD="${ROOT_LOCATION}/../aste/build"
MAPPING_TESTER="${ROOT_LOCATION}/../aste/tools/mapping-tester"

HEAPTRACK_LOCATION="${ROOT_LOCATION}/../heaptrack/build/bin"
PATH=$PATH:$HEAPTRACK_LOCATION

echo $HEAPTRACK_LOCATION

rm -rf "${TEST_LOCATION}"
mkdir -p "${TEST_LOCATION}"

echo ""
echo "[TEST] precice-aste-evaluate"
echo ""

cd "${TEST_LOCATION}"

# Calculate franke function on fine mesh
precice-aste-evaluate -m "${ROOT_LOCATION}/meshes/t_0.008.vtk" -f "franke3d" -d "Franke Function" -o "fine_mesh_nn.vtk"

echo ""
echo "[TEST] precice-aste-run"
echo ""

# Map from the finer mesh to coarser mesh
heaptrack precice-aste-run -v -p A --mesh "fine_mesh_nn" --data "Franke Function" -c "${RUN_LOCATION}/precice-config.xml" &
heaptrack precice-aste-run -v -p B --mesh "${ROOT_LOCATION}/meshes/t_0.006" --output "map_nn" --data "InterpolatedData" -c "${RUN_LOCATION}/precice-config.xml"

echo ""
echo "[TEST] precice-aste-evaluate"
echo ""

# Calculate statistics
precice-aste-evaluate -m "map_nn.vtk" -f "franke3d" -d difference --diffdata "InterpolatedData" --diff

cd "${ROOT_LOCATION}"
